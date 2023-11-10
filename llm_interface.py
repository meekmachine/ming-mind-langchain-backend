from airtable import Airtable

def get_newest_row(table_name):
    # Get all rows from the table
    rows = airtable.iterate(table_name)

    # Sort rows by created_at in descending order
    sorted_rows = sorted(rows, key=lambda row: datetime.datetime.strptime(row['fields']['created_at'], '%Y-%m-%dT%H:%M:%S.%fZ'), reverse=True)

    # If the sorted list is not empty, the first row is the newest
    if sorted_rows:
        return sorted_rows[0]
    else:
        return None
    
def get_prompt(prompt: str):
    newest_row = get_newest_row('table1')  # replace 'table1' with your actual table name
    if newest_row is not None:
        # Use the newest row as the prompt
        prompt = newest_row['fields']['prompt']
        return prompt
    else:
        return {"error": "No rows in table"}

def intitial_validation(llm, input):
    prompt = get_prompt("IntialValidaition")
    return 1 if llm.run(f"{prompt} {input}")[0] == '1' else 0

def initial_validation_failed(llm, input):
    prompt = get_prompt("InitialValidationFailed")
    return llm.run(f"{prompt} {input}")

def parse_messages(llm, input):
    prompt = get_prompt("ParseMessages")
    return llm.run(f"{prompt} {input}")

def identify_interlocutors(llm, inout):
    prompt = get_prompt("IdentifyInterlocutors")
    return llm.run(f"{prompt} {input}")

def get_overall_evaluation(llm, input):
    prompt = get_prompt("OverallEvaluation")
    return llm.run(f"{prompt} {input}")