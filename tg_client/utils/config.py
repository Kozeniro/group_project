import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    BOT_TOKEN = os.getenv("BOT_TOKEN")
    AUTH_SERVER_URL = os.getenv("AUTH_SERVER_URL", "http://localhost:8081")
    MAIN_API_URL = os.getenv("MAIN_API_URL")