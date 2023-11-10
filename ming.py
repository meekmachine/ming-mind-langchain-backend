"""
[M]ediation for [I]nterloculative [N]oxiousness and [G]rievences
This app uses the "Conversations Gone Awry" corpus from the ConvoKit library 
published by the Cornell University Social Dynamics Lab to test the capabilities
of llms in recognising "toxicity" and personal attacks in conversations.
"""
import os
import argparse
import pandas as pd
from convokit import Corpus, download
from langchain.llms import HuggingFaceHub
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def format_conversation(convo_df):
    formatted_convo = []
    for _, row in convo_df.iterrows():
        formatted_convo.append(f"{row['speaker']}: {row['text']}")
    return "\n".join(formatted_convo)

def parse_llm_response(response, convo_df):
    # Example parsing logic based on the structure provided in the prompt
    # This is a placeholder and should be adapted to your specific response format
    parsed_response = {
        "personal_attacks": [],
        "toxicity_scores": []
    }
    for line in response.split('\n'):
        if "Personal Attack:" in line:
            parsed_response["personal_attacks"].append(line)
        elif "Toxicity Score:" in line:
            parsed_response["toxicity_scores"].append(line)
    return parsed_response

def main(min_messages, has_personal_attack, num_conversations):
    hf_api_key = os.getenv("HF_API_KEY")
    llm = HuggingFaceHub(model="gpt2", api_key=hf_api_key)  # Replace 'gpt2' with your desired model

    corpus = Corpus(filename=download("conversations-gone-awry-corpus"))
    conversations_df = corpus.get_conversations_dataframe()
    utterances_df = corpus.get_utterances_dataframe()
    speakers_df = corpus.get_speakers_dataframe()

    merged_df = pd.merge(utterances_df, speakers_df, left_on='speaker', right_index=True)
    merged_df = pd.merge(merged_df, conversations_df, left_on='conversation_id', right_index=True)

    if has_personal_attack:
        merged_df = merged_df[merged_df['meta.conversation_has_personal_attack'] == True]

    for convo_id in merged_df['conversation_id'].unique()[:num_conversations]:
        convo_df = merged_df[merged_df['conversation_id'] == convo_id]
        formatted_convo = format_conversation(convo_df)

        prompt = f"Analyze the following conversation for personal attacks and toxicity:\n{formatted_convo}\n\nResponse:"
        response = llm.generate(prompt, max_tokens=150)
        result = parse_llm_response(response, convo_df)

        print(f"Conversation ID: {convo_id}")
        print("Result:", result)
        print("\n")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Process conversation dataset.')
    parser.add_argument('--min_messages', type=int, default=0, help='Minimum number of messages in a conversation')
    parser.add_argument('--has_personal_attack', type=bool, default=False, help='Whether the conversation includes a personal attack')
    parser.add_argument('--num_conversations', type=int, default=10, help='Number of conversations to analyze')
    args = parser.parse_args()
    main(args.min_messages, args.has_personal_attack, args.num_conversations)
