from fastapi import FastAPI, HTTPException, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
import uuid
import uvicorn
from dotenv import load_dotenv
from get_convo import *
from airtable_prompt_handler import AirtablePromptHandler
from web_socket_state_machine import WebSocketStateMachine

# Load environment variables
load_dotenv()

app = FastAPI()

# CORS middleware setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Query(BaseModel):
    text: str
    session_id: str = None
    additional_vars: dict = {}

class TimeSeriesQuery(BaseModel):
    participant1: str
    participant2: str
    factor1: str
    factor2: str
    text: str

# Global instance of AirtablePromptHandler
airtable_prompt_handler = AirtablePromptHandler()

@app.get("/get-convo")
async def get_conversation(min_messages: int = 10, has_personal_attack: bool = True, min_toxicity: float = 0.3):
    try:
        convo_df = await get_convo(min_messages, has_personal_attack, min_toxicity)
        if convo_df is not None:
            return convo_df.to_dict(orient='records')
        else:
            raise HTTPException(status_code=404, detail="No conversation found matching the criteria")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
# New route for getting conversation by ID
@app.get("/get_conversation_by_id/{convo_id}")
async def get_conversation_by_id(convo_id: str):
    convo_df = get_convo_by_id(convo_id)
    if convo_df is not None and not convo_df.empty:
        return convo_df.to_dict(orient='records')
    else:
        raise HTTPException(status_code=404, detail="Conversation not found")


@app.post("/is-mingable")
async def is_mingable(query: Query):
    # Instantiate handler for each request to maintain state isolation
    handler = AirtablePromptHandler(create_new_agent=True)

    if query.session_id:
        # Remove the session if it already exists
        handler.agent_handler.remove_session(query.session_id)

    # Create a new agent session
    session_id = handler.agent_handler.create_agent()

    # Process the prompt
    result = await handler.process_prompt(
        "InitialValidation",
        query.text,
        session_id=session_id
    )

    return {"result": result, "session_id": session_id}

@app.post("/remove-agent")
async def remove_agent(query: Query):
    airtable_prompt_handler = AirtablePromptHandler()
    airtable_prompt_handler.remove_agent(query.session_id)
    return {"message": "Agent removed"}

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    state_machine = WebSocketStateMachine()
    try:
        while True:
            # Receive text from client
            text = await websocket.receive_text()

            # Process based on the current state
            if state_machine.state == "id_interlocutors_awaiting_ai_response":
                result = await state_machine.process_id_interlocutors(text)
                await websocket.send_text(result)
                state_machine.receive_human_response_id()

            elif state_machine.state == "feedback_awaiting_ai_response":
                feedback, timeseries = await state_machine.process_feedback(text, {})
                await websocket.send_json({"feedback": feedback, "timeseries": timeseries})
                state_machine.trigger_feedback()

    except Exception as e:
        print(f"WebSocket error: {e}")
        await websocket.close()

# Main function to run the app
if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True, log_level="debug")
