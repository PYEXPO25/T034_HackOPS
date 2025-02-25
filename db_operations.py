from firebase_config import db
from firebase_admin import  firestore 

def save_progress(user_id, score, streak):
    try:
        user_ref = db.collection("users").document(user_id)
        user_ref.set({
            "score": score,
            "streak": streak,
            "total_games": firestore.Increment(1)  # Increments total games played
        }, merge=True)
        return {"message": "Progress saved!"}
    except Exception as e:
        return {"error": str(e)}

def get_progress(user_id):
    try:
        user_ref = db.collection("users").document(user_id)
        user_data = user_ref.get()
        if user_data.exists:
            return user_data.to_dict()
        return {"score": 0, "streak": 0, "total_games": 0}  # Default values for new users
    except Exception as e:
        return {"error": str(e)}
