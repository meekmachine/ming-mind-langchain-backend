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

async def overall_evaluation(input_text):
    handler = AirtablePromptHandler()
    return await handler.process_prompt("OverallEvaluation", input_text)

async def identify_interlocutors(input_text):
    handler = AirtablePromptHandler()
    return await handler.process_prompt("IdentifyInterlocutors", input_text)
