import os
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Firebase Admin using the service account key
cred = credentials.Certificate(".keys/ming-527ed-firebase-adminsdk-z38ui-27b7e06411.json")
firebase_admin.initialize_app(cred)

# Initialize Firestore
db = firestore.client()

# Define the collection name
collection_name = 'topics'  # Replace with your collection name


def print_structure(data, level=0):
    indent = "  " * level
    if isinstance(data, dict):
        for key, value in data.items():
            print(f"{indent}{key}:")
            print_structure(value, level + 1)
    else:
        print(f"{indent}{data}")

def print_first_document_structure(collection_name):
    # Get the collection reference
    collection_ref = db.collection(collection_name)

    # Fetch the first document based on integer ID ordering
    docs = collection_ref.order_by('__name__').limit(1).stream()

    # Print the structure of the first document
    for doc in docs:
        print(f'First Document ID: {doc.id}')
        print_structure(doc.to_dict())

# Call the function
print_first_document_structure(collection_name)
