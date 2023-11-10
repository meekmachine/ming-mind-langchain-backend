import argparse
import pandas as pd
from convokit import Corpus, download

# Set up command line arguments
parser = argparse.ArgumentParser(description='Process conversation dataset.')
parser.add_argument('--min_messages', type=int, default=0, help='Minimum number of messages in a conversation')
parser.add_argument('--has_personal_attack', type=bool, default=False, help='Whether the conversation includes a personal attack')
args = parser.parse_args()

# Download and load the corpus
corpus = Corpus(filename=download("conversations-gone-awry-corpus"))

# Create DataFrames
conversations_df = corpus.get_conversations_dataframe()
utterances_df = corpus.get_utterances_dataframe()
speakers_df = corpus.get_speakers_dataframe()

# Merge DataFrames
merged_df = pd.merge(utterances_df, speakers_df, left_on='speaker', right_index=True)
merged_df = pd.merge(merged_df, conversations_df, left_on='conversation_id', right_index=True)

# Filter based on command line arguments
if args.min_messages > 0:
    convo_counts = merged_df['conversation_id'].value_counts()
    valid_convos = convo_counts[convo_counts >= args.min_messages].index
    merged_df = merged_df[merged_df['conversation_id'].isin(valid_convos)]

if args.has_personal_attack:
    merged_df = merged_df[merged_df['meta.conversation_has_personal_attack'] == True]

# Process each conversation
for convo_id in merged_df['conversation_id'].unique():
    convo_df = merged_df[merged_df['conversation_id'] == convo_id]
    
    # Calculate total toxicity and count personal attacks
    total_toxicity = convo_df['meta.toxicity'].sum()
    personal_attacks_count = convo_df['meta.comment_has_personal_attack'].sum()

    print(f"Conversation ID: {convo_id}")
    print(f"Total Toxicity: {total_toxicity}")
    print(f"Personal Attacks: {personal_attacks_count}")
    for _, row in convo_df.iterrows():
        speaker_name = row['speaker']  # Assuming 'speaker' column contains speaker names
        print(f"{speaker_name}: {row['text']}")

    print("\n")

# Optionally, save to a file or further process as needed
