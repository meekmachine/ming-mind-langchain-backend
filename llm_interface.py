from airtable_prompt_handler import AirtablePromptHandler

# Global dictionary to store session data
sessions = {}

from airtable_prompt_handler import AirtablePromptHandler

async def describe_convo(input_text):
    handler = AirtablePromptHandler()
    return await handler.process_prompt("AwryConvoDescription", input_text)

async def initial_validation(input_text):
    handler = AirtablePromptHandler()
    return await handler.process_prompt("InitialValidation", input_text)

async def initial_validation_failed(input_text):
    handler = AirtablePromptHandler()
    return await handler.process_prompt("InitialValidationFailed", input_text)

async def parse_messages(input_text):
    handler = AirtablePromptHandler()
    return await handler.process_prompt("ParseMessages", input_text)

async def id_interlocutors(input_text):
    handler = AirtablePromptHandler(create_new_agent=True)
    response, session_id = await handler.process_prompt("IdentifyInterlocutors", input_text)
    return response, session_id

async def overall_evaluation(input_text, session_id, interlocutor):
    handler = AirtablePromptHandler(use_agent=True)
    return await handler.process_prompt("Feedback", input_text, interlocutor=interlocutor, session_id=session_id)