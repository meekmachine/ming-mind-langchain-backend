import argparse
import pandas as pd
from convokit import Corpus, download
import random
import redis
import pickle

# Set up command line arguments
parser = argparse.ArgumentParser(description='Process conversation dataset.')
parser.add_argument('--min_messages', type=int, default=7, help='Minimum number of messages in a conversation')
parser.add_argument('--has_personal_attack', type=bool, default=False, help='Whether the conversation includes a personal attack')
parser.add_argument('--min_toxicity', type=float, default=0.3, help='Minimum toxicity score for at least one message in the conversation')
args = parser.parse_args()

# Connect to Redis
r = redis.from_url(os.environ.get("REDIS_URL"))
#r = redis.Redis(host='localhost', port=6379, db=1)

# Check if DataFrames are in Redis
conversations_df = r.get('conversations_df')
utterances_df = r.get('utterances_df')
speakers_df = r.get('speakers_df')

if conversations_df is None or utterances_df is None or speakers_df is None:
    # Download and load the corpus
    corpus = Corpus(filename=download("conversations-gone-awry-corpus"))

    # Create DataFrames
    conversations_df = corpus.get_conversations_dataframe()
    utterances_df = corpus.get_utterances_dataframe()
    speakers_df = corpus.get_speakers_dataframe()

    # Trim unnecessary columns
    conversations_df = conversations_df.drop(columns=['vectors'])
    utterances_df = utterances_df.drop(columns=['meta.parsed'])
    speakers_df = speakers_df.drop(columns=['vectors'])  # Adjust as needed

    # Serialize and store the DataFrames in Redis
    r.set('conversations_df', pickle.dumps(conversations_df))
    r.set('utterances_df', pickle.dumps(utterances_df))
    r.set('speakers_df', pickle.dumps(speakers_df))
else:
    # Deserialize the DataFrames
    conversations_df = pickle.loads(conversations_df)
    utterances_df = pickle.loads(utterances_df)
    speakers_df = pickle.loads(speakers_df)

# Merge DataFrames
merged_df = pd.merge(utterances_df, speakers_df, left_on='speaker', right_index=True)
merged_df = pd.merge(merged_df, conversations_df, left_on='conversation_id', right_index=True)

# Define the get_convo function
async def get_convo(min_messages=7, has_personal_attack=False, min_toxicity=0.5):
    # Filter based on criteria
    if min_messages > 0:
        convo_counts = merged_df['conversation_id'].value_counts()
        valid_convos = convo_counts[convo_counts >= min_messages].index
        df = merged_df[merged_df['conversation_id'].isin(valid_convos)]
    else:
        df = merged_df

    if has_personal_attack:
        df = df[df['meta.conversation_has_personal_attack'] == True]

    # Filter for conversations with at least one message having toxicity above the threshold
    if min_toxicity > 0.0:
        toxic_convo_ids = df[df['meta.toxicity'] >= min_toxicity]['conversation_id'].unique()
        df = df[df['conversation_id'].isin(toxic_convo_ids)]

    # Get a random conversation
    if not df.empty:
        convo_id = random.choice(df['conversation_id'].unique())
        return df[df['conversation_id'] == convo_id].sort_values('timestamp', ascending=True)
    else:
        return None

# Get a random conversation based on command line arguments
convo_df = get_convo(min_messages=args.min_messages, has_personal_attack=args.has_personal_attack, min_toxicity=args.min_toxicity)

print(convo_df)
 