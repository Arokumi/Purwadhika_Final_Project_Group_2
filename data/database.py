import os
import pymongo
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")

def get_db():
    if not MONGO_URI:
        print("MONGO_URI not set!")
        return None
    try:
        client = pymongo.MongoClient(MONGO_URI)
        #nama db = career_assistant
        return client.career_assistant
    except Exception as e:
        print(f"Error connecting to DB: {e}")
        return None

USER_ID = "user_1"

def save_user_data(data):
    db = get_db()
    if db is not None:
        db.users.update_one(
            {"user_id": USER_ID}, 
            {"$set": data}, 
            upsert=True
        )

def load_user_data():
    db = get_db()
    if db is not None:
        data = db.users.find_one({"user_id": USER_ID})
        if data and '_id' in data:
            del data['_id'] 
        return data
    return {}