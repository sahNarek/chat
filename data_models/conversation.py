from pymongo import MongoClient
from core.config import app_config

connection_url = app_config.DATABASE_URL


class Conversation:
    def __init__(self) -> None:
        self.client = MongoClient(connection_url)
        self.database = self.client.get_database("chatDb")
        self.conversations = self.database.get_collection("conversations")

    def get_user_conversations(self, user_id: str):
        conversations = self.conversations.find_one({"user_id": user_id})
        if conversations:
            return conversations.get("conversations")
        return []
    
    def save_conversation(self, user_id: str, conversation: dict):
        conversations_exist = self.get_user_conversations(user_id)
        if conversations_exist:
            return self.update_conversation(user_id, conversation)
        else:
            return self.insert_conversation(user_id, conversation)


    def insert_conversation(self, user_id: str, conversation: dict):
        return self.conversations.insert_one({
            "user_id": user_id,
            "conversations": [conversation]
        })


    def update_conversation(self, user_id: str, conversation: dict):
        return self.conversations.update_one(
            {"user_id": user_id},
            {"$push": {"conversations": conversation}}
        )

    def delete_conversation(self, user_id: str):
        return self.conversations.delete_one({"user_id": user_id})
    
    def delete_all_conversations(self):
        return self.conversations.delete_many({})
    
    def get_all_conversations(self):
        return self.conversations.find({})
    
