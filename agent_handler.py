from langchain.chat_models import ChatOpenAI
from langchain.memory import RedisChatMessageHistory, ConversationBufferMemory
from langchain.chains import LLMChain
from langchain.prompts import ChatPromptTemplate
import os
import uuid
import redis
from dotenv import load_dotenv
from pydantic import BaseModel

# Load environment variables
load_dotenv()

class AIMessage(BaseModel):
    content: str  # Ensuring content is always a string

class AgentHandler:
    def __init__(self):

        self.chains = {}

    def create_agent(self, session_id=None):
        if not session_id:
            session_id = str(uuid.uuid4())

        # Initialize RedisChatMessageHistory and wrap it in ConversationBufferMemory
        redis_history = RedisChatMessageHistory(session_id=session_id)
        memory = ConversationBufferMemory(chat_history=redis_history, token_limit=4096)

        # Define the prompt template
        template = """{history}\nHuman: {input}\nAssistant:"""
        prompt = ChatPromptTemplate.from_template(template)

        # Initialize ChatOpenAI
        llm = ChatOpenAI(openai_api_key=os.getenv("OPENAI_API_KEY"), model_name="gpt-3.5-turbo")

        # Create and store the chain
        self.chains[session_id] = LLMChain(prompt=prompt, llm=llm, verbose=True, memory=memory)

        return session_id 


    def run_agent(self, session_id, human_input):

        if session_id not in self.chains:
            raise ValueError(f"No agent found for session ID: {session_id}")
            print(list(self.chains.keys())[0])
            print(type(session_id))
        chain = self.chains[session_id]

        # Add the human's input to the chat history
        chain.memory.chat_memory.add_user_message(human_input)

        # Retrieve the conversation history within the token limit
        # Ensuring that the method or property is used correctly
        history_text = ""
        if hasattr(chain.memory, 'get_memory_string'):
            history_text = chain.memory.get_memory_string()  # If it's a method
        elif hasattr(chain.memory, 'memory_string'):
            history_text = chain.memory.memory_string  # If it's a property

        # Construct the prompt with the history and new input
        prompt = f"{history_text}\nHuman: {human_input}\nAssistant:"

        # Run the chain with the constructed prompt
        response = chain.run({"input": prompt})

        # Extract and handle the response
        response_content = response.content if hasattr(response, 'content') else str(response)
        chain.memory.chat_memory.add_ai_message(response_content)
        if session_id not in self.chains:
            print(type(list(self.chains.keys()[0])))
            print(type(session_id))
        return response_content


    def llm(self, input_text):
        llm = ChatOpenAI(openai_api_key=os.getenv("OPENAI_API_KEY"))
        result = llm.invoke(input_text)
        return result.content
