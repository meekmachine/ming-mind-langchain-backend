import uuid
from fastapi import FastAPI
from pydantic import BaseModel
from langchain.agents import initialize_agent, load_tools
from langchain.llms import HuggingFaceHub
from langchain.cache import RedisCache
from dotenv import load_dotenv
from langchain.globals import set_llm_cache
import os
import redis
import uuid
from airtable import Airtable

redis_url = "redis://localhost:6379"

load_dotenv()  # take environment variables from .env.

app = FastAPI()

# Define the memory store
redis_db = redis.Redis(host='localhost', port=6379, db=0)

# Define the language model
llm = HuggingFaceHub(repo_id="google/flan-t5-xxl", model_kwargs={"temperature": 0.1, "max_length": 200}, huggingfacehub_api_token=os.getenv("HUGGINGFACEHUB_API_KEY"))

# Initialize the agent
agent = initialize_agent(llm=llm, tools=[], agent="conversational-react-description", verbose=True)

# Define a dictionary to store sessions
sessions = {}

# Initialize Airtable
airtable = Airtable("AIRTABLE_API_KEY")  # replace with your actual base key and API key

class Query(BaseModel):
    text: str

def get_session(session_id):
    if session_id is None:
        session_id = str(uuid.uuid4())
        sessions[session_id] = RedisCache(redis_db)
    elif session_id not in sessions:
        return None, "Invalid session_id"
    return sessions[session_id], None

def get_newest_row(table_name):
    # Get all rows from the table
    rows = airtable.iterate(table_name)

    # Sort rows by created_at in descending order
    sorted_rows = sorted(rows, key=lambda row: datetime.datetime.strptime(row['fields']['created_at'], '%Y-%m-%dT%H:%M:%S.%fZ'), reverse=True)

    # If the sorted list is not empty, the first row is the newest
    if sorted_rows:
        return sorted_rows[0]
    else:
        return None
        
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

@app.get("/method1")
async def get_overall_evaluation(query: Query, session_id: str = None):
    try:
        # Get the session
        cache, error = get_session(session_id)
        if error:
            return {"error": error}

        # Set the cache for the current session
        agent.cache = cache

        # Get the newest row from the corresponding table
        newest_row = get_newest_row('table1')  # replace 'table1' with your actual table name

        if newest_row is not None:
            # Use the newest row as the prompt
            prompt = newest_row['fields']['prompt']

            # Run the agent with the prompt
            result = agent.run("Method 1: " + prompt)
            return {"result": result}
        else:
            return {"error": "No rows in table"}
    except Exception as e:
        return {"error": str(e)}

@app.post("/method2")
async def method2(query: Query, session_id: str = None):
    try:
        # Get the session
        cache, error = get_session(session_id)
        if error:
            return {"error": error}

        # Set the cache for the current session
        agent.cache = cache

        # Get the newest row from the corresponding table
        newest_row = get_newest_row('table2')  # replace 'table2' with your actual table name

        if newest_row is not None:
            # Use the newest row as the prompt
            prompt = newest_row['fields']['prompt']

            # Run the agent with the prompt
            result = agent.run("Method 2: " + prompt)
            return {"result": result}
        else:
            return {"error": "No rows in table"}
    except Exception as e:
        return {"error": str(e)}