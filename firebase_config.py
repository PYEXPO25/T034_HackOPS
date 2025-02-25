import firebase_admin
from firebase_admin import credentials, auth

# Load the Firebase service account JSON file
cred = credentials.Certificate("your-service-account.json")  # Replace with your JSON filename
firebase_admin.initialize_app(cred)
