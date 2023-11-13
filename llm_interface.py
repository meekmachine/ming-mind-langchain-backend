import json
import os
from pyairtable import Table
import datetime
from dotenv import load_dotenv
from langchain.llms import HuggingFaceHub
from langchain.chat_models import ChatOpenAI
from langchain.prompts.few_shot import FewShotPromptTemplate
from langchain.prompts.prompt import PromptTemplate


load_dotenv()  # take environment variables from .env.

airtable_keys = {
    "InitialValidation": "tbl3PFTH0wovOXlLY",
    "AwrConvoDescription": "tblPiiHeKCkynTJgC",
}

def from_js(js_string):
    # Replace backticks with double quotes
    json_string = js_string.replace('`', '"')
    json_string = json_string.replace('\n', '\\n')

    # Replace single quotes around keys and values with double quotes
    json_string = json_string.replace("'", '"')

    # Now, parse the JSON string
    return json.loads(json_string)

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
    pprompt, examples, model_name = await get_prompt("InitialValidation")
    print("================================")
    # example_prompt = PromptTemplate(input_variables=["input", "expected_output"], template="{expected_output}")
    # q = json.loads(examples)

    # prompt = FewShotPromptTemplate(
    #     examples = q,
    #     example_prompt=example_prompt,
    #     suffix="{input}",
    #     input_variables=["input", "expected_output"],
    # )
    prompt = PromptTemplate.from_template(f"{pprompt} \n {input}")
    print(prompt)
    model = ChatOpenAI(openai_apibe_con_key=os.getenv("OPENAI_API_KEY"))
    chain = prompt | modelvo
    print(prompt)
    result = chain.invoke(input)
    print("================================")
    print(result)
    return result.content

async def describe_convo(input):
    pprompt, examples, model_name = await get_prompt("AwryConvoDescription")
    print("================================")
    # example_prompt = PromptTemplate(input_variables=["input", "expected_output"], template="{expected_output}")
    # q = json.loads(examples)

    # prompt = FewShotPromptTemplate(
    #     examples = q,
    #     example_prompt=example_prompt,
    #     suffix="{input}",
    #     input_variables=["input", "expected_output"],
    # )
    prompt = PromptTemplate.from_template(f"{pprompt} \n {input}")
    print(prompt)
    model = ChatOpenAI(openai_api_key=os.getenv("OPENAI_API_KEY"))
    chain = prompt | model
    print(prompt)
    result = chain.invoke(input)
    print("================================")
    print(result)
    return result.content

def initial_validation_failed(llm, input):
    prompt = get_prompt("InitialValidationFailed")
    return llm.run(f"{prompt} {input}")

def parse_messages(llm, input):
    prompt = get_prompt("ParseMessages")
    return llm.run(f"{prompt} {input}")

# def identify_interlocutors(llm, inout):
#     prompt = get_prompt("IdentifyInterlocutors")
#     return llm.run(f"{prompt} {input}")

def get_overall_evaluation(llm, input):
    prompt = get_prompt("OverallEvaluation")
    return llm.run(f"{prompt} {input}")