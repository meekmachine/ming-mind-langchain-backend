import firebase_admin
from firebase_admin import credentials, firestore
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

# Initialize Firebase
cred = credentials.Certificate(".keys/ming-527ed-firebase-adminsdk-z38ui-27b7e06411.json")
firebase_admin.initialize_app(cred)
db = firestore.client()

def fetch_embeddings_from_firebase():
    # Fetch embeddings from Firebase
    # Assuming embeddings are stored in a collection named 'embeddings'
    embeddings = {}
    docs = db.collection('embeddings').stream()
    for doc in docs:
        embeddings[doc.id] = doc.to_dict()
    return embeddings

def calculate_cosine_similarity(embedding1, embedding2):
    # Calculate cosine similarity between two embeddings
    return cosine_similarity([embedding1], [embedding2])[0][0]

def update_similarity_scores(new_embeddings, existing_embeddings):
    # Calculate and update similarity scores
    for new_id, new_emb in new_embeddings.items():
        for existing_id, existing_emb in existing_embeddings.items():
            similarity = calculate_cosine_similarity(new_emb, existing_emb)
            # Update the similarity score in Firebase
            # You might want to structure how you store these similarity scores
            # For example, in a separate collection or as a subcollection
            db.collection('similarities').document(f'{new_id}_{existing_id}').set({'score': similarity})

def main():
    existing_embeddings = fetch_embeddings_from_firebase()
    new_embeddings = {}  # Fetch or calculate new embeddings

    # Update similarity scores
    update_similarity_scores(new_embeddings, existing_embeddings)

if __name__ == "__main__":
    main()
