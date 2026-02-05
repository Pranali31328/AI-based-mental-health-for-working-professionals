from pymongo import MongoClient
import os
from dotenv import load_dotenv

load_dotenv()

client = MongoClient(os.getenv("MONGO_URI"))
db = client["mentalhealth"]

users_collection = db["users"]
chat_collection = db["chats"]
assessment_collection = db["assessments"]
alerts_collection = db["alerts"]

print("Database Connected Successfully")