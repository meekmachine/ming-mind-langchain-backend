import os
import redis
import json
import uuid
from langchain.agents import initialize_agent, load_tools
from langchain.llms import HuggingFaceHub
from langchain.chat_models import ChatOpenAI
from dotenv import load_dotenv

load_dotenv()

class AgentHandler:
    def __init__(self):
        # Load environment variables
        self.huggingfacehub_api_token = os.getenv("HUGGINGFACEHUB_API_TOKEN")
        self.redis_host = os.getenv("REDIS_HOST", 'localhost')
        self.redis_port = int(os.getenv("REDIS_PORT", 6379))
        self.redis_db = int(os.getenv("REDIS_DB", 0))

        # Initialize Redis for session management
        self.redis_client = redis.Redis(host=self.redis_host, port=self.redis_port, db=self.redis_db)
        self.agents = {}

    def create_agent(self):
        session_id = str(uuid.uuid4())
        llm = ChatOpenAI(os.getenv(openai_api_key="OPENAI_API_KEY"))
        agent = initialize_agent(llm=llm, tools=load_tools(), agent="conversational-react-description", verbose=True)
        self.agents[session_id] = agent
        return session_id

    def get_agent(self, session_id):
        return self.agents.get(session_id)

    def run_agent(self, session_id, input_text):
        agent = self.get_agent(session_id)
        if agent:
            return agent.run(input_text)
        else:
            raise ValueError("Agent not found")

    def llm(self, input_text):
        llm = ChatOpenAI(openai_api_key=os.getenv("OPENAI_API_KEY"))
        # Assuming 'run' is a method to process text. Adjust this call as per your LLM usage.
        print(f"LLM input: {input_text}")
        result = llm.invoke(input_text)
        return result.content
