import redis    
import json

class RedisClient:
    def __init__(self):
        self.redis = redis.Redis(
            host='localhost',
            port=6379,
            db=0,
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
        return 

    def delete_user(self, chat_id):
        if not self.redis:
            return 
        
        self.redis.delete(f"chat:{chat_id}")

        
redis_client = RedisClient()