import os
import random
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

    async def get_random_active_row(self, table_name):
        try:
            table = Table(self.api_key, self.app_id, table_name)
            active_rows = [row for row in table.all() if row['fields'].get('Active')]
            if not active_rows:
                raise ValueError("No active rows found in table")
            return random.choice(active_rows)
        except Exception as e:
            print(f"Error in get_random_active_row: {e}")
            raise


    async def process_prompt(self, table_name, input_text, session_id=None, additional_vars=None, use_personality=False):
        row = await self.get_random_active_row(table_name)
        prompt_text = row['fields']['Prompt']

        # Replace variables in the prompt
        if additional_vars:
            for key, value in additional_vars.items():
                prompt_text = prompt_text.replace(f"{{{key}}}", value)

        # Append examples to the prompt if available
        if 'Examples' in row['fields']:
            examples = row['fields']['Examples']
            prompt_text += "\n" + examples

        # Handle the use_personality feature
        if use_personality:
            personality_row = await self.get_random_active_row("Personality")
            if 'Prompt' in personality_row['fields']:
                personality_prompt = personality_row['fields']['Prompt']
                prompt_text = personality_prompt + "\n" + prompt_text

        response = ""
        if self.use_agent and session_id:
            response = self.agent_handler.run_agent(session_id, f"{prompt_text} \n {input_text}")
        elif self.create_new_agent:
            new_session_id = self.agent_handler.create_agent()
            response = self.agent_handler.run_agent(new_session_id, f"{prompt_text} \n {input_text}")
            return response, new_session_id
        else:
            response = self.agent_handler.llm(f"{prompt_text} \n {input_text}")

        await self.save_response(row['id'], response)
        return response
        
        response = ""
        if self.use_agent and session_id:
            response = self.agent_handler.run_agent(session_id, f"{prompt_text} \n {input_text}")
        elif self.create_new_agent:
            new_session_id = self.agent_handler.create_agent()
            response = self.agent_handler.run_agent(new_session_id, f"{prompt_text} \n {input_text}")
            return response, new_session_id
        else:
            response = self.agent_handler.llm(f"{prompt_text} \n {input_text}")

        await self.save_response(row['id'], response)
        return response

    async def save_response(self, uid, result):
        self.responses_table.create({"UID": uid, "Result": result})
