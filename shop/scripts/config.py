import os 
from dotenv import load_dotenv


load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN = int(os.getenv("ADMIN_ID"))
CRYPTOBOT_API_TOKEN = os.getenv("CRYPTOBOT_API_TOKEN")
