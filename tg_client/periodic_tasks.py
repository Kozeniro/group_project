import asyncio
import logging
from datetime import datetime
from typing import Dict, List
from aiogram import Bot

from utils.redis_utils import get_all_anonymous_users, get_all_authorized_users, delete_user_state, update_user_tokens, get_user_state
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
        
        if not anonymous_users:
            return
        
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
                status = status_data.get('status')
                
                if status == 'authorized':
                    access_token = status_data.get('access_token')
                    refresh_token = status_data.get('refresh_token')
                    
                    if not access_token or not refresh_token:
                        logger.error(f"No tokens for chat {chat_id}")
                        continue
                    
                    update_user_tokens(chat_id, access_token, refresh_token)
                    
                    try:
                        await self.bot.send_message(
                            chat_id=chat_id,
                            text="Успешная авторизация."
                        )
                    except Exception as e:
                        logger.error(f"Failed to send auth success message: {e}")
                
                elif status in ['expired', 'denied']:
                    delete_user_state(chat_id)
                    
                    if status == 'denied':
                        try:
                            await self.bot.send_message(
                                chat_id=chat_id,
                                text="Авторизация отклонена. Попробуйте снова: /login"
                            )
                        except Exception as e:
                            logger.error(f"Failed to send denied message: {e}")
                
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
                            except Exception as e:
                                logger.error(f"Failed to send notification: {e}")
                        
                        await main_api_client.delete_notifications(access_token)
                            
                except Exception as e:
                    if "401" in str(e):
                        refreshed = await refresh_tokens(chat_id)
                        if not refreshed:
                            logger.warning(f"Failed to refresh tokens for {chat_id}")
                    else:
                        logger.error(f"Error getting notifications: {e}")
                
            except Exception as e:
                logger.error(f"Error processing notifications for {chat_id}: {e}")