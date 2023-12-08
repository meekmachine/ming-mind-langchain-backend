import os
import uuid
from langchain.llms import HuggingFaceHub
from langchain.chat_models import ChatOpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class AgentHandler:
    def __init__(self):
        self.sessions = {}

    def create_session(self, session_id=None, model_name=None, temperature=None):
        session_id = session_id if session_id else str(uuid.uuid4())
        self.sessions[session_id] = {
            "variables": {},
            "model": self._initialize_llm(model_name, temperature),
            "text": ""  # To store the conversation text
        }
        return session_id

    def _initialize_llm(self, model_name, temperature):
        if model_name:
            if model_name == "gpt-3.5-turbo":
                return ChatOpenAI(openai_api_key=os.getenv("OPENAI_API_KEY"), model_name=model_name)
            else:
                return HuggingFaceHub(model_name=model_name, temperature=temperature, api_token=os.getenv("HUGGINGFACEHUB_API_TOKEN"))
        else:
            return ChatOpenAI(openai_api_key=os.getenv("OPENAI_API_KEY"))

    def run_query(self, session_id, prompt):
        if session_id not in self.sessions:
            raise ValueError(f"No session found for session ID: {session_id}")

        session = self.sessions[session_id]
        for key, value in session["variables"].items():
            prompt = prompt.replace(f"{{{key}}}", value)

        result = session["model"].invoke(prompt)
        return result.content

    def update_session_variables(self, session_id, variables):
        if session_id not in self.sessions:
            raise ValueError(f"No session found for session ID: {session_id}")

        self.sessions[session_id]["variables"].update(variables)

    def store_text(self, session_id, text):
        if session_id not in self.sessions:
            raise ValueError(f"No session found for session ID: {session_id}")

        self.sessions[session_id]["text"] = text

    def remove_session(self, session_id):
        if session_id in self.sessions:
            del self.sessions[session_id]

    def simple_llm_query(self, input_text):
        llm = ChatOpenAI(openai_api_key=os.getenv("OPENAI_API_KEY"))
        return llm.invoke(input_text).content

# Usage example
# agent_handler = AgentHandler()
# simple_result = agent_handler.simple_llm_query("Your prompt here")
