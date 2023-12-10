import os
import uuid
from langchain.chat_models import ChatOpenAI
from langchain.llms import HuggingFaceHub
from langchain.memory import RedisChatMessageHistory, ConversationBufferMemory
from langchain.chains import LLMChain
from langchain.prompts import ChatPromptTemplate
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class AgentHandler:
    def __init__(self):
        self.chains = {}

    def create_agent(self, session_id=None, model_name=None, temperature=None):

        session_id = str(uuid.uuid4())

        # Initialize RedisChatMessageHistory and wrap it in ConversationBufferMemory
        redis_history = RedisChatMessageHistory(session_id=session_id)
        memory = ConversationBufferMemory(chat_history=redis_history, token_limit=4094)

        # Define the prompt template
        template = """{history}\nHuman: {input}\nAssistant:"""
        prompt = ChatPromptTemplate.from_template(template)

        # Initialize the LLM based on model name and temperature
        if model_name:
            if model_name == "gpt-3.5-turbo" or not temperature:
                llm = ChatOpenAI(openai_api_key=os.getenv("OPENAI_API_KEY"), model_name=model_name)
            else:
                llm = HuggingFaceHub(model_name=model_name, temperature=temperature, api_token=os.getenv("HUGGINGFACEHUB_API_TOKEN"))
        else:
            llm = ChatOpenAI(openai_api_key=os.getenv("OPENAI_API_KEY"))

        # Create and store the chain
        self.chains[session_id] = LLMChain(prompt=prompt, llm=llm, verbose=True, memory=memory)

        return session_id

    def run_agent(self, session_id, human_input):
        if session_id not in self.chains:
            raise ValueError(f"No agent found for session ID: {session_id}")

        chain = self.chains[session_id]
        chain.memory.chat_memory.add_user_message(human_input)

        # Retrieve the conversation history as a string
        history_text = chain.memory.get_memory_string() if hasattr(chain.memory, 'get_memory_string') else ''

        # Manually trim the history if it's too long
        max_tokens = 4096  # Adjust this limit based on the model's capabilities
        while len(history_text.split()) > max_tokens:
            # Remove the oldest message until the token count is within limits
            messages = history_text.split('\n')
            messages.pop(0)  # Remove the oldest message
            history_text = '\n'.join(messages)

        # Construct the prompt with the trimmed history and new input
        prompt = f"{history_text}\nHuman: {human_input}\nAssistant:"

        # Run the chain with the constructed prompt
        response = chain.run({"input": prompt})
        response_content = response.content if hasattr(response, 'content') else str(response)
        chain.memory.chat_memory.add_ai_message(response_content)
        return response_content


    def llm(self, input_text):
        llm = ChatOpenAI(openai_api_key=os.getenv("OPENAI_API_KEY"))
        result = llm.invoke(input_text)
        return result.content
