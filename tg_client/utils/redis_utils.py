from redis_client import redis_client
from datetime import datetime
import json

def get_user_state(chat_id):
    user_data = redis_client.get_user(chat_id)
    if user_data:
        return user_data
    return {'state': 'unknown'}

def set_user_state(chat_id, state, data=None):
    if data is None:
        data = {}
    
    user_data = {'state': state, **data}
    
    if state == 'anonymous':
        redis_client.add_to_set('anonymous_users', chat_id)
        redis_client.remove_from_set('authorized_users', chat_id)
    elif state == 'authorized':
        redis_client.add_to_set('authorized_users', chat_id)
        redis_client.remove_from_set('anonymous_users', chat_id)
    elif state == 'unknown':
        redis_client.remove_from_set('anonymous_users', chat_id)
        redis_client.remove_from_set('authorized_users', chat_id)
    
    redis_client.save_user(chat_id, user_data)

def delete_user_state(chat_id):
    redis_client.remove_from_set('anonymous_users', chat_id)
    redis_client.remove_from_set('authorized_users', chat_id)
    redis_client.delete_user(chat_id)

def get_all_anonymous_users():
    return redis_client.get_set_members('anonymous_users')

def get_all_authorized_users():
    return redis_client.get_set_members('authorized_users')

def update_user_tokens(chat_id, access_token, refresh_token):
    user_data = get_user_state(chat_id)
    user_data['access_token'] = access_token
    user_data['refresh_token'] = refresh_token
    user_data['state'] = 'authorized'
    set_user_state(chat_id, 'authorized', user_data)

def save_login_token(token, data):
    redis_client.save_login_token(token, data)

def get_login_token(token):
    return redis_client.get_login_token(token)

def delete_login_token(token):
    redis_client.delete_login_token(token)