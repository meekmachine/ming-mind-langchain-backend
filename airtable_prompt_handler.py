import os
from pyairtable import Table
from dotenv import load_dotenv
from agent_handler import AgentHandler

load_dotenv()  # Load environment variables from .env.

class AirtablePromptHandler:
    def __init__(self, use_agent=False, session_id=None):
        self.api_key = os.getenv("AIRTABLE_API_KEY")
        self.app_id = os.getenv("AIRTABLE_APP_ID")
        self.agent_handler = AgentHandler()
        self.use_agent = use_agent
        self.session_id = session_id

        # Check if API key and App ID are retrieved correctly
        if not self.api_key or not self.app_id:
            raise ValueError("Missing AIRTABLE_API_KEY or AIRTABLE_APP_ID in environment variables")

        self.responses_table = Table(self.api_key, self.app_id, "Responses")

    async def get_first_row(self, table_name):
        try:
            table = Table(self.api_key, self.app_id, table_name)
            rows = table.all()
            return rows[0] if rows else None
        except Exception as e:
            print(f"Error in get_first_row: {e}")
            return None

    async def process_prompt(self, table_name, input_text):
        row = await self.get_first_row(table_name)
        if row:
            prompt_text = row['fields']['Prompt']

            # Decide whether to use an agent-based LLM or a direct LLM
            if self.use_agent and self.session_id:
                response = self.agent_handler.run_agent(self.session_id, f"{prompt_text} \n {input_text}")
            else:
                response = self.agent_handler.llm(f"{prompt_text} \n {input_text}")



            # Optionally, save the response to Airtable
            await self.save_response(row['id'], response)
            return response
        else:
            return {"error": "No rows in table"}

    async def save_response(self, uid, result):
        # Debugging print before saving the response
        print(f"Saving response for UID {uid}: {result}")

        self.responses_table.create({"UID": uid, "Result": result})
