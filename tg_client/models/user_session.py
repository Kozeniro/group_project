from datetime import datetime
import json
from typing import Optional, Dict, Any
from redis_client import redis_client

class UserSession:
    def __init__(self, chat_id: int):
        self.chat_id = str(chat_id)
        self._key = f"user:{chat_id}"
        
    def save(self, 
             status: str, 
             login_token: Optional[str] = None,
             access_token: Optional[str] = None,
             refresh_token: Optional[str] = None,
             user_id: Optional[int] = None):
        
        data = {
            "chat_id": self.chat_id,
            "status": status,
            "login_token": login_token,
            "access_token": access_token,
            "refresh_token": refresh_token,
            "user_id": user_id,
            "updated_at": datetime.now().isoformat()
        }
        
        if not redis_client.get_user(self.chat_id):
            data["created_at"] = datetime.now().isoformat()
            
        redis_client.save_user(self.chat_id, data)
        return data
    
    def load(self) -> Optional[Dict[str, Any]]:
        return redis_client.get_user(self.chat_id)
    
    def delete(self):
        redis_client.delete_user(self.chat_id)
    
    def update_field(self, field: str, value: Any):
        data = self.load()
        if data:
            data[field] = value
            data["updated_at"] = datetime.now().isoformat()
            redis_client.save_user(self.chat_id, data)
    
    @staticmethod
    def get_all_by_status(status: str):
        pattern = "user:*"
        users = []
        for key in redis_client.redis.scan_iter(match=pattern):
            data = redis_client.redis.get(key)
            if data:
                user_data = json.loads(data)
                if user_data.get("status") == status:
                    users.append(user_data)
        return users