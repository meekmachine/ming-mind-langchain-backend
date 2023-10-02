from flask import Flask, request, jsonify
from langchain.llms import openai
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get the OpenAI API key from environment variable
openai_api_key = os.environ.get('OPENAI_API_KEY')

app = Flask(__name__)

# Initialize LangChain's OpenAI LLM
llm = openai()

@app.route('/')
def index():
    return jsonify({"error": "Invalid request. Please use the appropriate endpoint."}), 400

@app.route('/analyze-text', methods=['POST'])
def analyze_text():
    data = request.json
    text = data.get('text', '')

    # Load the prompt template from the file
    with open('prompt_template.txt', 'r') as file:
        prompt_template = file.read()

    # Replace the placeholder with the actual text
    formatted_prompt = prompt_template.replace("{user_text}", text)

    # Use LangChain's LLM to analyze the formatted prompt
    feedback = llm.predict(formatted_prompt)

    return jsonify({"feedback": feedback})

if __name__ == "__main__":
    app.run(debug=True)
