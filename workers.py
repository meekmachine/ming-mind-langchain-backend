from airtable_prompt_handler import AirtablePromptHandler

# Global store for worker process results
worker_results = {}

async def process_id_interlocutors(session_id, text):
    """
    Process ID Interlocutors query in the background and store the result.
    """
    try:
        # Instantiate AirtablePromptHandler for processing the prompt
        airtable_prompt_handler = AirtablePromptHandler()

        # Process the prompt with given session ID and text
        result = await airtable_prompt_handler.process_prompt(
            "IdentifyInterlocutors",
            text,
            session_id=session_id
        )

        # Store the result for future retrieval
        worker_results[session_id] = result

    except Exception as e:
        # Handle any exceptions (log or store them as needed)
        print(f"Error processing ID interlocutors: {e}")
        worker_results[session_id] = str(e)

def get_worker_result(session_id):
    """
    Retrieve the result of the background task for a given session ID.
    """
    return worker_results.get(session_id)
