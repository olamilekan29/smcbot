# # data.py — Twelve Data version
# import requests
# import pandas as pd
# import os
# from dotenv import load_dotenv

# load_dotenv()

# API_KEY  = os.getenv("TWELVE_API_KEY")
# BASE_URL = "https://api.twelvedata.com"

# # Timeframe map — Twelve Data format
# TF_MAP = {
#     "H4":  "4h",
#     "H1":  "1h",
#     "M15": "15min"
# }

# def get_candles(symbol, granularity, count=300):
#     """
#     symbol      = "EUR/USD", "GBP/USD" etc (Twelve Data uses slash format)
#     granularity = "H4", "H1", "M15"
#     """
#     interval = TF_MAP.get(granularity, granularity)

#     url = f"{BASE_URL}/time_series"
#     params = {
#         "symbol":     symbol,
#         "interval":   interval,
#         "outputsize": count,
#         "apikey":     API_KEY,
#         "format":     "JSON"
#     }

#     response = requests.get(url, params=params)

#     if response.status_code != 200:
#         print(f"Error: {response.text}")
#         return None

#     data = response.json()

#     if "values" not in data:
#         print(f"No data for {symbol}: {data.get('message', 'unknown error')}")
#         return None

#     df = pd.DataFrame(data["values"])
#     df = df.rename(columns={
#         "datetime": "time",
#         "open":  "open",
#         "high":  "high",
#         "low":   "low",
#         "close": "close",
#         "volume":"volume"
#     })

#     df["time"]   = pd.to_datetime(df["time"])
#     df["open"]   = df["open"].astype(float)
#     df["high"]   = df["high"].astype(float)
#     df["low"]    = df["low"].astype(float)
#     df["close"]  = df["close"].astype(float)

#     # Twelve Data returns newest first — reverse to oldest first
#     df = df.iloc[::-1].reset_index(drop=True)

#     return df



import requests
import pandas as pd
import os
from dotenv import load_dotenv

load_dotenv()

API_KEY  = os.getenv("POLYGON_API_KEY")
BASE_URL = "https://api.polygon.io"

# Timeframe map — Polygon format
TF_MAP = {
    "H4":  ("hour",   4),
    "H1":  ("hour",   1),
    "M15": ("minute", 15)
}

def get_candles(symbol, granularity, count=300):
    """
    symbol      = "EUR/USD" — auto converted to Polygon format C:EURUSD
    granularity = "H4", "H1", "M15"
    """
    # Convert EUR/USD → C:EURUSD
    poly_symbol = "C:" + symbol.replace("/", "")

    timespan, multiplier = TF_MAP[granularity]

    url = f"{BASE_URL}/v2/aggs/ticker/{poly_symbol}/range/{multiplier}/{timespan}/2020-01-01/2030-01-01"

    params = {
        "adjusted": "true",
        "sort":     "asc",
        "limit":    count,
        "apiKey":   API_KEY
    }

    response = requests.get(url, params=params)

    if response.status_code != 200:
        print(f"Error fetching {symbol} {granularity}: {response.text}")
        return None

    data = response.json()

    if "results" not in data or not data["results"]:
        print(f"No data for {symbol} {granularity}")
        return None

    df = pd.DataFrame(data["results"])
    df = df.rename(columns={
        "t": "time",
        "o": "open",
        "h": "high",
        "l": "low",
        "c": "close",
        "v": "volume"
    })

    df["time"]   = pd.to_datetime(df["time"], unit="ms")
    df["open"]   = df["open"].astype(float)
    df["high"]   = df["high"].astype(float)
    df["low"]    = df["low"].astype(float)
    df["close"]  = df["close"].astype(float)

    # Return only the last `count` candles
    df = df.tail(count).reset_index(drop=True)

    return df