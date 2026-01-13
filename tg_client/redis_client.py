import redis    
import json
from datetime import datetime
from utils.config import Config

class RedisClient:
    def __init__(self):
        self.redis = redis.Redis(
            host=Config.REDIS_HOST,
            port=Config.REDIS_PORT,
            db=Config.REDIS_DB,
            decode_responses=True 
        )  
    
    def save_user(self, chat_id, user_data):
        if not self.redis:
            return 
        
        data_json = json.dumps(user_data)
        self.redis.set(f"chat:{chat_id}", data_json)

    def get_user(self, chat_id):
        if not self.redis:
            return None
        
        data = self.redis.get(f"chat:{chat_id}")
        if data:
            return json.loads(data)
        return {'state': 'unknown'}

    def delete_user(self, chat_id):
        if not self.redis:
            return 
        
        self.redis.delete(f"chat:{chat_id}")

    def save_login_token(self, token, data):
        if not self.redis:
            return
        
        data_json = json.dumps(data)
        self.redis.setex(f"login_token:{token}", 300, data_json)

    def get_login_token(self, token):
        if not self.redis:
            return None
    
        data = self.redis.get(f"login_token:{token}")
        if data:
            return json.loads(data)
        return None
    
    def delete_login_token(self, token: str):
        if not self.redis:
            return
        
        self.redis.delete(f"login_token:{token}")

    def save_user_session(self, chat_id, session_data):    
        if 'created_at' not in session_data:
            session_data['created_at'] = datetime.now().isoformat()
        session_data['updated_at'] = datetime.now().isoformat()        
        data_json = json.dumps(session_data)

        self.redis.setex(f"user:{chat_id}", 2592000, data_json)     
    
    def get_user_session(self, chat_id):
        data = self.redis.get(f"user:{chat_id}")
        if data:
            return json.loads(data)
        return None
    
    def delete_user_session(self, chat_id):
        self.redis.delete(f"user:{chat_id}")
  
        
redis_client = RedisClient()