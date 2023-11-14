import pandas as pd
from convokit import Corpus, download
import openai
from firebase_admin import credentials, firestore, initialize_app
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

# Firebase setup
cred = credentials.Certificate('path/to/firebase/credentials.json')
initialize_app(cred)
db = firestore.client()

# OpenAI setup
openai.api_key = 'your-openai-api-key'

def calculate_embeddings(text):
    response = openai.Embedding.create(input=text, engine="text-similarity-babbage-001")
    return response['data'][0]['embedding']

# Download and load the corpus
corpus = Corpus(filename=download("conversations-gone-awry-corpus"))
conversations_df = corpus.get_conversations_dataframe()
utterances_df = corpus.get_utterances_dataframe()
speakers_df = corpus.get_speakers_dataframe()

def process_conversations(conversations_df, utterances_df, speakers_df):
    embeddings = {}
    for convo_id in conversations_df.index:
        # Aggregate conversation texts
        convo_texts = utterances_df[utterances_df['conversation_id'] == convo_id]['text']
        aggregated_text = ' '.join(convo_texts)
        embedding = calculate_embeddings(aggregated_text)
        embeddings[convo_id] = embedding

        # Calculate the earliest timestamp (start time) of the conversation
        start_time = utterances_df[utterances_df['conversation_id'] == convo_id]['timestamp'].min()

        # Additional conversation data
        total_attacks = utterances_df[utterances_df['conversation_id'] == convo_id]['meta.comment_has_personal_attack'].sum()
        average_toxicity = utterances_df[utterances_df['conversation_id'] == convo_id]['meta.toxicity'].mean()

        # Include all available metadata fields
        convo_metadata = conversations_df.loc[convo_id].to_dict()

        # Aggregate speaker information
        speaker_ids = utterances_df[utterances_df['conversation_id'] == convo_id]['speaker'].unique()
        speaker_info = speakers_df.loc[speaker_ids].to_dict(orient='index')

        # Store conversation data in Firebase
        convo_doc_ref = db.collection('awry_convos').document(convo_id)
        convo_doc_ref.set({
            'embedding': embedding,
            'total_personal_attacks': total_attacks,
            'average_toxicity': average_toxicity,
            'start_time': start_time,
            'metadata': convo_metadata,
            'speakers': speaker_info,
            'uid': convo_id  # Using conversation ID as UID
        })

    # Calculate similarity between conversations
    embedding_matrix = np.array(list(embeddings.values()))
    similarity_matrix = cosine_similarity(embeding_matrix)

    # Store similarity data
    for i, convo_id in enumerate(embeddings.keys()):
        similar_convos = {}
        for j, other_convo_id in enumerate(embeddings.keys()):
            if i != j:
                similar_convos[other_convo_id] = similarity_matrix[i, j]
        similarity_doc_ref = db.collection('conversation_similarity').document(convo_id)
        similarity_doc_ref.set(similar_convos)

process_conversations(conversations_df.head(100), utterances_df, speakers_df)
