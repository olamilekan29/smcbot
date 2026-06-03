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



# import requests
# import pandas as pd
# import os
# from dotenv import load_dotenv

# load_dotenv()

# API_KEY  = os.getenv("POLYGON_API_KEY")
# BASE_URL = "https://api.polygon.io"

# # Timeframe map — Polygon format
# TF_MAP = {
#     "H4":  ("hour",   4),
#     "H1":  ("hour",   1),
#     "M15": ("minute", 15)
# }

# def get_candles(symbol, granularity, count=300):
#     """
#     symbol      = "EUR/USD" — auto converted to Polygon format C:EURUSD
#     granularity = "H4", "H1", "M15"
#     """
#     # Convert EUR/USD → C:EURUSD
#     poly_symbol = "C:" + symbol.replace("/", "")

#     timespan, multiplier = TF_MAP[granularity]

#     url = f"{BASE_URL}/v2/aggs/ticker/{poly_symbol}/range/{multiplier}/{timespan}/2020-01-01/2030-01-01"

#     params = {
#         "adjusted": "true",
#         "sort":     "asc",
#         "limit":    count,
#         "apiKey":   API_KEY
#     }

#     response = requests.get(url, params=params)

#     if response.status_code != 200:
#         print(f"Error fetching {symbol} {granularity}: {response.text}")
#         return None

#     data = response.json()

#     if "results" not in data or not data["results"]:
#         print(f"No data for {symbol} {granularity}")
#         return None

#     df = pd.DataFrame(data["results"])
#     df = df.rename(columns={
#         "t": "time",
#         "o": "open",
#         "h": "high",
#         "l": "low",
#         "c": "close",
#         "v": "volume"
#     })

#     df["time"]   = pd.to_datetime(df["time"], unit="ms")
#     df["open"]   = df["open"].astype(float)
#     df["high"]   = df["high"].astype(float)
#     df["low"]    = df["low"].astype(float)
#     df["close"]  = df["close"].astype(float)

#     # Return only the last `count` candles
#     df = df.tail(count).reset_index(drop=True)

#     return df


# import requests
# import pandas as pd
# import os
# from datetime import datetime, timedelta
# from dotenv import load_dotenv

# load_dotenv()

# API_KEY  = os.getenv("POLYGON_API_KEY")
# BASE_URL = "https://api.polygon.io"

# TF_MAP = {
#     "H4":  ("hour",   4),
#     "H1":  ("hour",   1),
#     "M15": ("minute", 15)
# }

# def get_candles(symbol, granularity, count=300):
#     # Convert EUR/USD → C:EURUSD
#     poly_symbol = "C:" + symbol.replace("/", "")

#     timespan, multiplier = TF_MAP[granularity]

#     # Calculate how far back we need to go to get `count` candles
#     # H4 = 4hrs per candle, need 300 = 1200 hours = 50 days back
#     # H1 = 1hr per candle, need 300 = 300 hours = 13 days back
#     # M15 = 15min per candle, need 200 = 3000 mins = ~3 days back
#     days_back_map = {
#         "H4":  100,   # extra buffer
#         "H1":  30,
#         "M15": 10
#     }
#     days_back = days_back_map.get(granularity, 30)

#     date_to   = datetime.utcnow().strftime("%Y-%m-%d")
#     date_from = (datetime.utcnow() - timedelta(days=days_back)).strftime("%Y-%m-%d")

#     url = (
#         f"{BASE_URL}/v2/aggs/ticker/{poly_symbol}/range"
#         f"/{multiplier}/{timespan}/{date_from}/{date_to}"
#     )

#     params = {
#         "adjusted": "true",
#         "sort":     "asc",
#         "limit":    50000,  # max allowed — we filter down after
#         "apiKey":   API_KEY
#     }

#     response = requests.get(url, params=params)

#     if response.status_code != 200:
#         print(f"   ❌ API error {response.status_code}: {response.text}")
#         return None

#     data = response.json()

#     if "results" not in data or not data["results"]:
#         print(f"   ❌ No results in response: {data}")
#         return None

#     df = pd.DataFrame(data["results"])

#     # Rename Polygon columns to standard names
#     df = df.rename(columns={
#         "t": "time",
#         "o": "open",
#         "h": "high",
#         "l": "low",
#         "c": "close",
#         "v": "volume"
#     })

#     # Keep only the columns we need
#     df = df[["time", "open", "high", "low", "close", "volume"]]

#     df["time"]   = pd.to_datetime(df["time"], unit="ms")
#     df["open"]   = df["open"].astype(float)
#     df["high"]   = df["high"].astype(float)
#     df["low"]    = df["low"].astype(float)
#     df["close"]  = df["close"].astype(float)

#     # Return only the last `count` candles
#     df = df.tail(count).reset_index(drop=True)

#     print(f"   ✅ Got {len(df)} candles for {symbol} {granularity}")

#     return df


import yfinance as yf
import pandas as pd

# Symbol map — yfinance format
SYMBOL_MAP = {
    "EUR/USD": "EURUSD=X",
    "GBP/USD": "GBPUSD=X",
    "USD/JPY": "USDJPY=X",
    "GBP/JPY": "GBPJPY=X",
    "XAU/USD": "GC=F"
}

# Timeframe map — yfinance format
TF_MAP = {
    "H4":  ("60m",  "60d"),   # 60min interval, 60 days history
    "H1":  ("60m",  "60d"),
    "M15": ("15m",  "30d")
}

def get_candles(symbol, granularity, count=300):
    yf_symbol = SYMBOL_MAP.get(symbol)
    if not yf_symbol:
        print(f"   ❌ Unknown symbol: {symbol}")
        return None

    interval, period = TF_MAP[granularity]

    try:
        ticker = yf.Ticker(yf_symbol)
        df = ticker.history(period=period, interval=interval)

        if df is None or df.empty:
            print(f"   ❌ No data returned for {symbol} {granularity}")
            return None

        # Rename columns to standard format
        df = df.rename(columns={
            "Open":   "open",
            "High":   "high",
            "Low":    "low",
            "Close":  "close",
            "Volume": "volume"
        })

        df.index.name = "time"
        df = df.reset_index()
        df["time"] = pd.to_datetime(df["time"])

        # Handle H4 — resample 60min candles into 4H candles
        if granularity == "H4":
            df = df.set_index("time")
            df = df.resample("4h").agg({
                "open":   "first",
                "high":   "max",
                "low":    "min",
                "close":  "last",
                "volume": "sum"
            }).dropna().reset_index()

        df = df[["time", "open", "high", "low", "close", "volume"]]
        df = df.tail(count).reset_index(drop=True)

        print(f"   ✅ Got {len(df)} candles for {symbol} {granularity}")
        return df

    except Exception as e:
        print(f"   ❌ Error fetching {symbol} {granularity}: {e}")
        return None