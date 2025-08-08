# config.py
import os

# Reads the secrets from the GitHub Actions environment
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

# This key can remain as it is not a private secret
SERPAPI_KEY = "0762446de39b652188001b268cdd5ec4262f2ddcbe3118d6bc95a804ebb4a33a"
INDEED_API_KEY = "0762446de39b652188001b268cdd5ec4262f2ddcbe3118d6bc95a804ebb4a33a"
