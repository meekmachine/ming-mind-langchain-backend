import requests

API_URL = "http://localhost:3000/api/v1/prediction/bc6ea7c3-5ec0-480e-9c6a-74d066b32cba"

def query(payload):
    response = requests.post(API_URL, json=payload)
    return response.json()
    
output = query({
    "question": "Hey, how are you?",
})
print (output)