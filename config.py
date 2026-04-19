# config.py
import os
from dotenv import load_dotenv

load_dotenv()

# Telegram Bot Token
BOT_TOKEN = os.getenv("BOT_TOKEN", "8111731612:AAFmQlvErUyLRBj1_MzlPrIsJBuJ9SLfuzg")

# HeroSMS API Key
HEROSMS_API_KEY = os.getenv("HEROSMS_API_KEY", "3007e25b167dA69eff19d7b5dd848713")

# HeroSMS API URL
HEROSMS_API_URL = "https://hero-sms.com/stubs/handler_api.php"

# Default settings
DEFAULT_COUNTRY = 4  # India
DEFAULT_SERVICE = "wa"  # WhatsApp

# Service codes
SERVICES = {
    "wa": "WhatsApp",
    "tg": "Telegram",
    "fb": "Facebook",
    "ig": "Instagram",
    "go": "Google",
    "tw": "Twitter",
    "tk": "TikTok",
    "wb": "WeChat",
    "ln": "LinkedIn",
    "dc": "Discord",
    "gh": "GitHub",
    "am": "Amazon",
    "ap": "Apple",
    "ms": "Microsoft"
}

# Country codes
COUNTRIES = {
    0: "Russia",
    1: "Ukraine",
    2: "Kazakhstan",
    3: "China",
    4: "India",
    5: "USA",
    6: "UK",
    7: "France",
    8: "Germany",
    9: "Indonesia",
    10: "Brazil",
    11: "Vietnam",
    12: "Philippines",
    13: "Turkey",
    14: "Egypt",
    15: "Bangladesh"
}

# Status codes
STATUS_CODES = {
    "STATUS_WAIT_CODE": "⏳ Waiting for SMS",
    "STATUS_WAIT_RETRY": "🔄 Waiting for code retry",
    "STATUS_WAIT_RESEND": "📨 Waiting for SMS resend",
    "STATUS_OK": "✅ Success! Code received",
    "STATUS_CANCEL": "❌ Canceled",
    "STATUS_WAIT_CALL": "📞 Waiting for call"
}