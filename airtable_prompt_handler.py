import os
from pyairtable import Table
from dotenv import load_dotenv
from agent_handler import AgentHandler

load_dotenv()

class AirtablePromptHandler:
    def __init__(self, use_agent=False, create_new_agent=False, session_id=None):
        self.api_key = os.getenv("AIRTABLE_API_KEY")
        self.app_id = os.getenv("AIRTABLE_APP_ID")
        self.agent_handler = AgentHandler()
        self.use_agent = use_agent
        self.create_new_agent = create_new_agent
        self.session_id = session_id

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
        if not row:
            return {"error": "No rows in table"}

        prompt_text = row['fields']['Prompt']
        response = ""

        if self.use_agent and self.session_id:
            response = self.agent_handler.run_agent(self.session_id, f"{prompt_text} \n {input_text}")
        elif self.create_new_agent:
            self.session_id = self.agent_handler.create_agent()
            response = self.agent_handler.run_agent(self.session_id, f"{prompt_text} \n {input_text}")
        else:
            response = self.agent_handler.llm(f"{prompt_text} \n {input_text}")

        await self.save_response(row['id'], response)
        return response, self.session_id if self.create_new_agent else response

    async def save_response(self, uid, result):
        self.responses_table.create({"UID": uid, "Result": result})
