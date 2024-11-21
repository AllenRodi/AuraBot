import os
from dotenv import load_dotenv

load_dotenv()

try:
    GUILD_ID = int(os.getenv("GUILD_ID"))
    print(f"GUILD_ID loaded successfully: {GUILD_ID}")
except (TypeError, ValueError) as e:
    GUILD_ID = None
    print(f"Error loading GUILD_ID: {e}")
