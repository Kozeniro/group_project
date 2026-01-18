import asyncio
import logging
from datetime import datetime
from typing import Dict, List
from aiogram import Bot

from utils.redis_utils import get_all_anonymous_users, get_all_authorized_users, delete_user_state, update_user_tokens, get_user_state, set_user_state
from utils.auth_client import auth_client
from utils.main_api_client import main_api_client
from utils.token_utils import refresh_tokens

logger = logging.getLogger(__name__)

class PeriodicTasks:
    def __init__(self, bot: Bot):
        self.bot = bot
        self.running = False
        
    async def start(self):
        self.running = True
        asyncio.create_task(self._check_anonymous_users())
        asyncio.create_task(self._check_notifications())
        
    async def stop(self):
        self.running = False
    
    async def _check_anonymous_users(self):
        while self.running:
            try:
                await self._check_anonymous_users_batch()
            except Exception as e:
                logger.error(f"Error checking anonymous users: {e}")
            
            await asyncio.sleep(30)
    
    async def _check_anonymous_users_batch(self):
        anonymous_users = get_all_anonymous_users()
        
        for chat_id in anonymous_users:
            try:
                user_state = get_user_state(chat_id)
                if user_state['state'] != 'anonymous':
                    continue
                    
                login_token = user_state.get('login_token')
                if not login_token:
                    delete_user_state(chat_id)
                    continue
                
                status_data = await auth_client.check_login_status(login_token)
                
                if 'error' in status_data:
                    if "404" in status_data['error'] or "400" in status_data['error']:
                        delete_user_state(chat_id)
                    continue
                
                status = status_data.get('status')
                
                if status in ['authorized', 'approved']:
                    access_token = status_data.get('access_token')
                    refresh_token = status_data.get('refresh_token')
                    
                    if not access_token or not refresh_token:
                        continue
                    
                    update_user_tokens(chat_id, access_token, refresh_token)
                    
                    await self.bot.send_message(
                        chat_id=chat_id,
                        text="Авторизация успешно завершена!"
                    )
                    
                elif status in ['expired', 'denied']:
                    delete_user_state(chat_id)
                    
                    if status == 'denied':
                        await self.bot.send_message(
                            chat_id=chat_id,
                            text="Авторизация отклонена. Попробуйте снова: /login"
                        )
                        
            except Exception as e:
                logger.error(f"Error processing anonymous user {chat_id}: {e}")
    
    async def _check_notifications(self):
        while self.running:
            try:
                await self._check_notifications_batch()
            except Exception as e:
                logger.error(f"Error checking notifications: {e}")
            
            await asyncio.sleep(60)
    
    async def _check_notifications_batch(self):
        authorized_users = get_all_authorized_users()
        
        if not authorized_users:
            return
        
        notifications_found = 0
        
        for chat_id in authorized_users:
            try:
                user_state = get_user_state(chat_id)
                if user_state['state'] != 'authorized':
                    continue
                    
                access_token = user_state.get('access_token')
                if not access_token:
                    continue
                

                try:
                    notifications = await main_api_client.get_notifications(access_token)
                    
                    if notifications and isinstance(notifications, list):
                        for notification in notifications:
                            try:
                                
                                await self.bot.send_message(
                                    chat_id=chat_id,
                                    text=f"Уведомление: {notification}"
                                )
                                notifications_found += 1
                            except Exception as e:
                                logger.error(f"Failed to send notification to {chat_id}: {e}")
                        
                        
                        if notifications:
                            await main_api_client.delete_notifications(access_token)
                                
                except Exception as e:
                    if "401" in str(e):
                        
                        refreshed = await self._refresh_user_tokens(chat_id)
                        if not refreshed:
                            logger.warning(f"Failed to refresh tokens for {chat_id}")
                    else:
                        logger.error(f"Error getting notifications for {chat_id}: {e}")
                
            except Exception as e:
                logger.error(f"Error processing notifications for {chat_id}: {e}")
        
        if notifications_found > 0:
            logger.info(f"Sent {notifications_found} notifications")

    async def _refresh_user_tokens(self, chat_id: str) -> bool:
        user_state = get_user_state(chat_id)
        
        if user_state['state'] != 'authorized':
            return False
        
        refresh_token = user_state.get('refresh_token')
        if not refresh_token:
            return False
        
        try:
            new_tokens = await auth_client.refresh_access_token(refresh_token)
            
            if new_tokens and 'access_token' in new_tokens:
                
                user_state['access_token'] = new_tokens['access_token']
                user_state['refresh_token'] = new_tokens.get('refresh_token', refresh_token)
                set_user_state(chat_id, 'authorized', user_state)
                return True
            else:
                
                delete_user_state(chat_id)
                return False
                
        except Exception as e:
            logger.error(f"Error refreshing tokens for {chat_id}: {e}")
            return False