from redis_client import redis_client
from datetime import datetime

def get_user_state(chat_id):
    user_data = redis_client.get_user(chat_id)
    if user_data:
        return user_data
    return {'state': 'unknown'}

def set_user_state(chat_id, state, data=None):
    if data is None:
        data = {}   
    user_data = {'state': state, **data}
    redis_client.save_user(chat_id, user_data)

def delete_user_state(chat_id):
    redis_client.delete_user(chat_id)

def save_login_token(token, chat_id, auth_type='pending'):
    data = {
        'chat_id': chat_id,
        'auth_type': auth_type,
        'created_at': datetime.now().isoformat(),
        'status': 'pending'
    }
    redis_client.save_login_token(token, data)

def get_login_token(token):
    return redis_client.get_login_token(token)

def delete_login_token(token):
    redis_client.delete_login_token(token)