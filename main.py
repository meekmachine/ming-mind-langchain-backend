from fastapi import FastAPI, WebSocket, HTTPException
from pydantic import BaseModel
import uvicorn
from web_socket_state_machine import WebSocketStateMachine
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = FastAPI()

# CORS middleware setup (as before)

# Pydantic models for request bodies
class Query(BaseModel):
    text: str
    additional_vars: dict = {}

# Pydantic models for WebSocket responses
class IDInterlocutorsResponse(BaseModel):
    selected_option: str

class FeedbackResponse(BaseModel):
    feedback: str
    timeseries_data: dict

# WebSocket route
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    session_id = None  # Session ID for the state machine (can be generated or received from the client)
    # Initialize the state machine
    ws_state_machine = WebSocketStateMachine()

    while True:
        data = await websocket.receive_text()
        query = Query.parse_raw(data)

        if ws_state_machine.state == 'id_interlocutors_awaiting_ai_response':
            result = await ws_state_machine.process_id_interlocutors(session_id, query.text)
            await websocket.send_json(result)
            ws_state_machine.receive_human_response_id()

        elif ws_state_machine.state == 'feedback_awaiting_ai_response':
            feedback_result, timeseries_result = await ws_state_machine.process_feedback(session_id, query.text, query.additional_vars)
            response = FeedbackResponse(feedback=feedback_result, timeseries_data=timeseries_result)
            await websocket.send_json(response.dict())
            ws_state_machine.trigger_feedback()

        elif ws_state_machine.state == 'feedback_awaiting_human_response':
            # Process human response for feedback
            pass

        # Additional logic for other states and transitions

        # Handle reset or end of communication
        if 'end' in query.text:
            ws_state_machine.reset()
            break

    await websocket.close()

# Additional HTTP routes (as before)

# Main function to run the app
if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True, log_level="debug")
