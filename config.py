# import os
# from dotenv import load_dotenv

# load_dotenv()

# # OANDA credentials
# API_KEY    = os.getenv("OANDA_API_KEY")
# ACCOUNT_ID = os.getenv("OANDA_ACCOUNT_ID")
# BASE_URL   = os.getenv("OANDA_BASE_URL")

# HEADERS = {
#     "Authorization": f"Bearer {API_KEY}",
#     "Content-Type": "application/json"
# }

# # Pairs to monitor (OANDA format)
# PAIRS = [
#     "EUR/USD",
#     "GBP/USD",
#     "GBP/JPY",
#     "XAU/USD"   
# ]

# # Timeframes
# TF_BIAS  = "H4"   # 4 hour  — bias
# TF_POI   = "H1"   # 1 hour  — mark OB
# TF_ENTRY = "M15"  # 15 min  — entry

# # Strategy settings
# CANDLE_COUNT    = 300   # how many candles to pull
# SWING_LOOKBACK  = 3     # candles each side for swing detection
# IMPULSE_FACTOR  = 1.5   # body must be 1.5x average to count as impulse
# RR_RATIO        = 3     # 1:3 risk reward
# SL_BUFFER       = 0.0015  # buffer below/above sweep for SL



import os
from dotenv import load_dotenv

load_dotenv()

# ── API CREDENTIALS ──────────────────────────────────────────
POLYGON_API_KEY = os.getenv("POLYGON_API_KEY")

# ── PAIRS TO MONITOR ─────────────────────────────────────────
PAIRS = [
    "EUR/USD",
    "GBP/USD",
    "USD/JPY",
    "XAU/USD"
]

# ── TIMEFRAMES ───────────────────────────────────────────────
TF_BIAS  = "H4"    # 4H  — determines bias
TF_POI   = "H1"    # 1H  — marks order blocks
TF_ENTRY = "M15"   # 15M — entry confirmation

# ── STRATEGY SETTINGS ────────────────────────────────────────
CANDLE_COUNT   = 300    # candles to pull per request
SWING_LOOKBACK = 3      # candles each side for swing detection
IMPULSE_FACTOR = 2.0    # body must be 2x average to count as impulse
RR_RATIO       = 3      # 1:3 risk reward
SL_BUFFER      = 0.0020 # buffer above/below sweep wick for SL