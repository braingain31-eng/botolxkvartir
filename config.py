import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
GROK_API_KEY = os.getenv("GROK_API_KEY")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
FIREBASE_CREDENTIALS_PATH = os.getenv("FIREBASE_CREDENTIALS_PATH", "service-account.json")
ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))
BOOKING_PARTNER_ID = os.getenv("BOOKING_PARTNER_ID")
BOOKING_SECRET = os.getenv("BOOKING_SECRET")
STRIPE_TOKEN = os.getenv("STRIPE_TOKEN")  # или RAZORPAY_TOKEN

# Цены
WEEK_PRICE_USD = 10.0
MONTH_PRICE_USD = 20.0
WEEK_PRICE_STARS = 1000
MONTH_PRICE_STARS = 2000

# Кошельки для крипты
CRYPTO_WALLETS = {
    "TON": "EQ...your_ton_wallet",
    "USDT_TRC20": "T...your_usdt_trc20_wallet"
}

# Oxylabs Credentials
OXYLABS_USERNAME = "andre_7MCmN"
OXYLABS_PASSWORD = "3avDSV_=w3c739p"