from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from langchain.agents import initialize_agent, load_tools
from langchain.llms import HuggingFaceHub
from langchain.cache import RedisCache
from dotenv import load_dotenv
from langchain.globals import set_llm_cache
import os
import redis
import uuid
from get_convo import get_convo
from airtable import Airtable
import uvicorn
import datetime
from llm_interface import *

load_dotenv()  # take environment variables from .env.

app = FastAPI()
# Define the memory store
redis_db = redis.Redis(host='localhost', port=6379, db=0)

# Define the language model
llm = HuggingFaceHub(repo_id="google/flan-t5-xxl", model_kwargs={"temperature": 0.1, "max_length": 200}, huggingfacehub_api_token=os.getenv("HUGGINGFACEHUB_API_TOKEN"))

# Initialize the agent
agent = initialize_agent(llm=llm, tools=[], agent="conversational-react-description", verbose=True)

# Define a dictionary to store sessions
sessions = {}

class AwryQuery(BaseModel):
    data: str
# Set up CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # List of allowed origins (React app URL)
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

class Query(BaseModel):
    text: str
    session_id: str = None
    interlocutor: str = None

def get_session(session_id):
    if session_id is None:
        session_id = str(uuid.uuid4())
        sessions[session_id] = RedisCache(redis_db)
    elif session_id not in sessions:
        return None, "Invalid session_id"
    return sessions[session_id], None

        
async def run(query: Query, session_id: str = None):
    try:
        # Always create a new session
        session_id = str(uuid.uuid4())
        sessions[session_id] = RedisCache(redis_db)
        # Set the cache for the current session
        agent.cache = sessions[session_id]

        # Run the agent
        result = agent.run(query.text)
        return {"result": result, "session_id": session_id}
    except Exception as e:
        return {"error": str(e)}

@app.get("/get-convo")
async def get_conversation(min_messages: int = 10, has_personal_attack: bool = True, min_toxicity: float = 0.3):
    print("Endpoint hit with parameters:", min_messages, has_personal_attack, min_toxicity)
    try:
        convo_df = await get_convo(min_messages, has_personal_attack, min_toxicity)
        if convo_df is not None:
            return convo_df.to_dict(orient='records')
        else:
            raise HTTPException(status_code=404, detail="No conversation found matching the criteria")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/clear")
async def clear(session_id: str):
    try:
        # Clear the memory store for the specified session
        cache, error = get_session(session_id)
        if error:
            return {"error": error}

        cache.clear()
        return {"message": "Memory store cleared"}
    except Exception as e:
        return {"error": str(e)}



@app.post("/is-mingable")
async def is_mingable(query: Query):
    try:
        response = await initial_validation(query.text)
        print(response)
        if response[0] == "1":
            return {"valid": 1}
        else:
            return "Not MINGable."
    except Exception as e:
        print(e)
        return {"error": str(e)}

@app.post("/awry-describer")
async def awry_describer(query: AwryQuery):
    try:
        print(query)
        return await describe_convo(query.data)

    except Exception as e:
        print(e)
        return {"error": str(e)}

@app.post("/id-interlocutors")
async def api_id_interlocutors(query: Query):
    try:
        result = await id_interlocutors(query.text)
        return {"result": result, "session_id": 'session_id'}
    except Exception as e:
        return {"error": str(e)}

class TimeSeriesQuery(BaseModel):
    interlocutor: str
    text: str

@app.post("/feedback")
async def api_feedback(query: Query):
    try:
        # Create a dictionary for additional variables, including 'interlocutor'
        additional_vars = {"interlocutor": query.interlocutor}
        
        # Call the 'overall_evaluation' function with the new arguments
        result = await overall_evaluation(input_text=query.text, additional_vars=additional_vars)
        
        return {"result": result}
    except Exception as e:
        return {"error": str(e)}

class TimeSeriesQuery(BaseModel):
    participant1: str
    participant2: str
    factor1: str
    factor2: str
    text: str

@app.post("/timeseries")
async def get_timeseries_data(query: TimeSeriesQuery):
    try:
        # Implement logic to process timeseries data based on the query parameters
        # For now, we'll just return the query parameters as a placeholder
        return {"participant1": query.participant1, "participant2": query.participant2, "factor1": query.factor1, "factor2": query.factor2, "text": query.text}
    except Exception as e:
        return {"error": str(e)}

  
if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True, log_level="debug")

