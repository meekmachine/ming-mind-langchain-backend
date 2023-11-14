import firebase_admin
from firebase_admin import credentials, firestore
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

# Initialize Firebase
cred = credentials.Certificate(".keys/ming-527ed-firebase-adminsdk-z38ui-27b7e06411.json")
if not firebase_admin._apps:
    firebase_admin.initialize_app(cred)
db = firestore.client()

def fetch_embeddings_from_firebase(verbose=True):
    # Fetch embeddings from Firebase
    embeddings = {}
    docs = db.collection('awry_convos').stream()
    for doc in docs:
        data = doc.to_dict()
        if 'embedding' in data:
            embeddings[doc.id] = data['embedding']
            if verbose:
                print(f"Fetched embedding for conversation {doc.id}")
    return embeddings

def calculate_cosine_similarity(embedding1, embedding2):
    return cosine_similarity([embedding1], [embedding2])[0][0]

def update_similarity_scores(new_embeddings, existing_embeddings, verbose=True):
    for new_id, new_emb in new_embeddings.items():
        similarity_scores = {}
        for existing_id, existing_emb in existing_embeddings.items():
            if new_id != existing_id:
                similarity = calculate_cosine_similarity(new_emb, existing_emb)
                similarity_scores[existing_id] = similarity
                if verbose:
                    print(f"Calculated similarity between {new_id} and {existing_id}: {similarity}")
        db.collection('awry_convos').document(new_id).update({'similarities': similarity_scores})
        if verbose:
            print(f"Updated similarity scores for conversation {new_id}")

def main():
    existing_embeddings = fetch_embeddings_from_firebase()
    new_embeddings = {}  # Fetch or calculate new embeddings

    update_similarity_scores(new_embeddings, existing_embeddings)

if __name__ == "__main__":
    main()