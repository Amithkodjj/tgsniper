import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    API_ID = int(os.getenv('API_ID'))
    API_HASH = os.getenv('API_HASH')
    SESSION_NAME = os.getenv('SESSION_NAME', 'marketchecker')
    
    DISCORD_WEBHOOK_URL = os.getenv('DISCORD_WEBHOOK_URL')
    
    MIN_PRICE = int(os.getenv('MIN_PRICE', 600))
    MAX_PRICE = int(os.getenv('MAX_PRICE', 1600))
    MIN_PROFIT_PERCENTAGE = float(os.getenv('MIN_PROFIT_PERCENTAGE', 30))
    USE_CONCURRENT = os.getenv('USE_CONCURRENT', 'true').lower() == 'true'
    BATCH_SIZE = int(os.getenv('BATCH_SIZE', 50))
    SCAN_INTERVAL = float(os.getenv('SCAN_INTERVAL', 1.0))
    SUMMARY_INTERVAL = int(os.getenv('SUMMARY_INTERVAL', 100))

config = Config() 