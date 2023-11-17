from langchain.chat_models import ChatOpenAI
from langchain.memory import RedisChatMessageHistory, ConversationBufferMemory
from langchain.chains import LLMChain
from langchain.prompts import ChatPromptTemplate
import os
import uuid
import redis
from dotenv import load_dotenv
from pydantic import BaseModel

class AIMessage(BaseModel):
    content: str  # Ensuring content is always a string
    ttext: str

# Load environment variables
load_dotenv()

class AgentHandler:
    def __init__(self):

        self.chains = {}

    def create_agent(self, session_id=None):
        if not session_id:
            session_id = str(uuid.uuid4())

        # Initialize RedisChatMessageHistory and wrap it in ConversationBufferMemory
        redis_history = RedisChatMessageHistory(session_id=session_id)
        memory = ConversationBufferMemory(chat_history=redis_history)

        # Define the prompt template
        template = """Previous conversation:
{history}
Human: {input}
Assistant:"""
        prompt = ChatPromptTemplate.from_template(template)

        # Initialize ChatOpenAI
        llm = ChatOpenAI(openai_api_key=os.getenv("OPENAI_API_KEY"), model_name="gpt-3.5-turbo", temperature=0)

        # Create and store the chain
        self.chains[session_id] = LLMChain(prompt=prompt, llm=llm, verbose=True, memory=memory)

        return session_id

    def run_agent(self, session_id, human_input):
        if session_id not in self.chains:
            raise ValueError(f"No agent found for session ID: {session_id}")

        chain = self.chains[session_id]

        # Add the human's input to the chat history
        chain.memory.chat_memory.add_user_message(human_input)

        # Run the chain with the input
        response = chain.run({"input": human_input})

        # Extract the content from the response
        # Assuming response is an object and the actual text is in a field named 'content'
        response_content = response.content if hasattr(response, 'content') else str(response)

        # Add the AI's response to the chat history
        chain.memory.chat_memory.add_ai_message(response_content)

        return response_content


    def llm(self, input_text):
        llm = ChatOpenAI(openai_api_key=os.getenv("OPENAI_API_KEY"))
        result = llm.invoke(input_text)
        return result.content
