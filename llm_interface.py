from airtable_prompt_handler import AirtablePromptHandler

# Create a global instance of AirtablePromptHandler
airtable_prompt_handler = AirtablePromptHandler()

async def describe_convo(input_text, session_id=None):
    return await airtable_prompt_handler.process_prompt("AwryConvoDescription", input_text, session_id)

async def initial_validation(input_text, session_id=None):
    return await airtable_prompt_handler.process_prompt("InitialValidation", input_text, session_id)

async def initial_validation_failed(input_text, session_id=None):
    return await airtable_prompt_handler.process_prompt("InitialValidationFailed", input_text, session_id)

async def parse_messages(input_text, session_id=None):
    return await airtable_prompt_handler.process_prompt("ParseMessages", input_text, session_id)

async def id_interlocutors(input_text):
    return await airtable_prompt_handler.process_prompt(table_name="IdentifyInterlocutors", input_text=input_text, use_personality=True )

async def overall_evaluation(input_text, additional_vars):
    return await airtable_prompt_handler.process_prompt(
        table_name="Feedback", 
        input_text=input_text,
        use_personality=True,
        additional_vars=additional_vars
    )           

async def handle_timeseries(input_text, participants, factors):
    # Here, we assume 'Timeseries' is the name of the table in Airtable
    return await airtable_prompt_handler.process_prompt(
        "Timeseries", 
        input_text, 
        additional_vars={"participants": participants, "factors": factors}
    )
# Additional functions can follow the same pattern.
