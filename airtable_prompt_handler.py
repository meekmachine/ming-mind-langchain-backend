class AirtablePromptHandler:
    def __init__(self, use_agent=False, create_new_agent=False, session_id=None):
        self.api_key = os.getenv("AIRTABLE_API_KEY")
        self.app_id = os.getenv("AIRTABLE_APP_ID")
        self.agent_handler = AgentHandler()
        self.use_agent = use_agent
        self.create_new_agent = create_new_agent

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

        prompt_text = row['fields'].get('Prompt', '')
        examples_text = row['fields'].get('Examples', '')

        # Concatenate examples text with prompt text if examples are present
        full_prompt = f"{examples_text}\n{prompt_text}\n{input_text}" if examples_text else f"{prompt_text}\n{input_text}"

        response = ""
        if self.use_agent and self.session_id:
            response = self.agent_handler.run_agent(self.session_id, full_prompt)
        elif self.create_new_agent:
            self.session_id = self.agent_handler.create_agent()
            response = self.agent_handler.run_agent(self.session_id, full_prompt)
        else:
            response = self.agent_handler.llm(full_prompt)

        await self.save_response(row['id'], response)
        if self.create_new_agent:
            return response, self.session_id
        else:
            return response

    async def save_response(self, uid, result):
        self.responses_table.create({"UID": uid, "Result": result})
