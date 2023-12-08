from transitions.extensions import HierarchicalMachine as Machine
from airtable_prompt_handler import AirtablePromptHandler
import asyncio

class WebSocketStateMachine:
    def __init__(self):
        self.at_prompt_handler = AirtablePromptHandler(create_new_agent=True)

        # Define states
        states = [
            'start',
            {'name': 'id_interlocutors', 'children': ['awaiting_ai_response', 'awaiting_human_response']},
            {'name': 'feedback', 'children': ['awaiting_ai_response', 'awaiting_human_response']}
        ]

        # Initialize state machine
        self.machine = Machine(model=self, states=states, initial='start')

        # Add transitions
        self.machine.add_transition('trigger_id_interlocutors', 'start', 'id_interlocutors_awaiting_ai_response')
        self.machine.add_transition('receive_human_response_id', 'id_interlocutors_awaiting_ai_response', 'feedback_awaiting_ai_response')
        self.machine.add_transition('trigger_feedback', 'feedback_awaiting_ai_response', 'feedback_awaiting_human_response')
        self.machine.add_transition('reset', '*', 'start')

    async def process_id_interlocutors(self, session_id, text):
        # Process ID Interlocutors using AirtablePromptHandler
        return await self.at_prompt_handler.process_prompt("IdentifyInterlocutors", text, session_id)

    async def process_feedback(self, session_id, text, additional_vars):
        # Process Feedback and Timeseries using AirtablePromptHandler
        feedback_result = await self.at_prompt_handler.process_prompt("Feedback", text, session_id, additional_vars)
        timeseries_result = await self.at_prompt_handler.process_prompt("Timeseries", text, additional_vars)
        return feedback_result, timeseries_result
