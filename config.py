import os
from dotenv import load_dotenv

load_dotenv()

# OANDA credentials
API_KEY    = os.getenv("OANDA_API_KEY")
ACCOUNT_ID = os.getenv("OANDA_ACCOUNT_ID")
BASE_URL   = os.getenv("OANDA_BASE_URL")

HEADERS = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

# Pairs to monitor (OANDA format)
PAIRS = [
    "EUR/USD",
    "GBP/USD",
    "USD/JPY",
    "GBP/JPY",
    "XAU/USD"   # Gold
]

# Timeframes
TF_BIAS  = "H4"   # 4 hour  — bias
TF_POI   = "H1"   # 1 hour  — mark OB
TF_ENTRY = "M15"  # 15 min  — entry

# Strategy settings
CANDLE_COUNT    = 300   # how many candles to pull
SWING_LOOKBACK  = 5     # candles each side for swing detection
IMPULSE_FACTOR  = 1.5   # body must be 1.5x average to count as impulse
RR_RATIO        = 3     # 1:3 risk reward
SL_BUFFER       = 0.0005  # buffer below/above sweep for SL