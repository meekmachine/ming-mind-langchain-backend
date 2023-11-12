import os
from pyairtable import Table
import datetime
from dotenv import load_dotenv
from langchain.llms import HuggingFaceHub

load_dotenv()  # take environment variables from .env.

airtable_keys = {
    "InitialValidation": "tbl3PFTH0wovOXlLY",
}

async def get_first_row(table_name):
    try:
        # Initialize Airtable for the specific table
        table = Table(os.getenv("AIRTABLE_API_KEY"), "appdqeUDRi9TsyVPA", table_name)
        rows = table.all()

        # If the list is not empty, the first row is the first
        if rows:
            return rows[0]
        else:
            return None
    except Exception as e:
        print(f"Error in get_first_row: {e}")
        return None
    
async def get_prompt(prompt: str):
    newest_row = await get_first_row(prompt)  # replace 'table1' with your actual table name
    print(newest_row)
    if newest_row is not None:
        # Use the newest row as the prompt
        return (newest_row['fields']['Prompt'], newest_row['fields']['Examples'], newest_row['fields']['Model_Name'])
    else:
        return {"error": "No rows in table"}

async def intitial_validation(input):
    # Define the language model
    prompt, examples, model_name = await get_prompt("InitialValidation")
    print(prompt, model_name)
    llm = HuggingFaceHub(repo_id=model_name, model_kwargs={"temperature": 0.1, "max_length": 200}, huggingfacehub_api_token=os.getenv("HUGGINGFACEHUB_API_TOKEN"))
    print(llm.run(f"{prompt} Examples: {examples} {input}"))
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