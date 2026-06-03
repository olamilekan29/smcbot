import pandas as pd
from config import IMPULSE_FACTOR


# ── CHECK 1: Impulse move ──────────────────────────────────────────
# def is_impulse(df, index):
#     """
#     The candle after the OB must be significantly 
#     larger than the average candle body.
#     """
#     if index >= len(df):
#         return False
#     body     = abs(df["close"].iloc[index] - df["open"].iloc[index])
#     avg_body = abs(df["close"] - df["open"]).rolling(20).mean().iloc[index]
#     if avg_body == 0:
#         return False
#     return body >= avg_body * IMPULSE_FACTOR


def is_impulse(df, index):
    if index >= len(df):
        return False

    candle = df.iloc[index]
    body   = abs(candle["close"] - candle["open"])
    spread = candle["high"] - candle["low"]  # full candle range

    if spread == 0:
        return False

    # 1. Body must be at least 70% of the full candle range
    #    (eliminates doji and spinning top candles as impulse)
    body_ratio = body / spread
    if body_ratio < 0.70:
        return False

    # 2. Body must be 2x larger than the 20-candle average body
    #    (eliminates small candles dressed as impulse)
    avg_body = abs(df["close"] - df["open"]).rolling(20).mean().iloc[index]
    if avg_body == 0:
        return False
    if body < avg_body * 2.0:
        return False

    # 3. For bullish impulse — must close in top 30% of its range
    #    For bearish impulse — must close in bottom 30% of its range
    is_bullish_candle = candle["close"] > candle["open"]
    close_position    = (candle["close"] - candle["low"]) / spread

    if is_bullish_candle and close_position < 0.70:
        return False  # closed too low — not a strong bullish impulse

    if not is_bullish_candle and close_position > 0.30:
        return False  # closed too high — not a strong bearish impulse

    return True
    


# ── CHECK 2: FVG left behind ───────────────────────────────────────
def find_fvg(df, impulse_index):
    """
    After the impulse candle, check if it left a Fair Value Gap.
    FVG = gap between candle[i-1] and candle[i+1].
    """
    i = impulse_index
    if i < 1 or i + 1 >= len(df):
        return None

    prev_high = df["high"].iloc[i - 1]
    prev_low  = df["low"].iloc[i - 1]
    next_high = df["high"].iloc[i + 1]
    next_low  = df["low"].iloc[i + 1]

    # Bullish FVG: next candle low is above prev candle high
    if next_low > prev_high:
        return {
            "type":   "Bullish FVG",
            "top":    next_low,
            "bottom": prev_high
        }

    # Bearish FVG: next candle high is below prev candle low
    if next_high < prev_low:
        return {
            "type":   "Bearish FVG",
            "top":    prev_low,
            "bottom": next_high
        }

    return None


# ── CHECK 3: Liquidity near OB ─────────────────────────────────────
def has_liquidity_near_ob(df, ob_index, ob_top, ob_bottom, ob_type):
    """
    Liquidity = previous swing highs or equal highs sitting 
    above a bearish OB (buy stops) or swing lows sitting 
    below a bullish OB (sell stops).
    These are what will magnetize price back to the OB.
    """
    # Look at the 40 candles before the OB
    window = df.iloc[max(0, ob_index - 40): ob_index]
    buffer = (ob_top - ob_bottom) * 2  # buffer = 2x OB size

    if ob_type == "Bullish OB":
        # Sell stops sitting below or at the OB bottom
        lows = window["low"][window["low"] <= ob_bottom + buffer]
        return len(lows) >= 2  # at least 2 lows nearby = pool of sell stops

    if ob_type == "Bearish OB":
        # Buy stops sitting above or at the OB top
        highs = window["high"][window["high"] >= ob_top - buffer]
        return len(highs) >= 2

    return False


# ── FULL VALID OB SCANNER ──────────────────────────────────────────
def get_valid_obs(df_1h, bias):
    valid_obs = []

    for i in range(2, len(df_1h) - 3):
        candle = df_1h.iloc[i]
        is_bearish = candle["close"] < candle["open"]
        is_bullish = candle["close"] > candle["open"]

        # ── BULLISH ORDER BLOCK ──
        if bias == "bullish" and is_bearish:
            # Candle after OB must be bullish impulse
            if not is_impulse(df_1h, i + 1):
                continue
            if df_1h["close"].iloc[i + 1] < df_1h["open"].iloc[i + 1]:
                continue  # must close bullish

            fvg = find_fvg(df_1h, i + 1)
            if fvg is None or "Bullish" not in fvg["type"]:
                continue

            ob_top    = candle["open"]
            ob_bottom = candle["close"]

            if not has_liquidity_near_ob(df_1h, i, ob_top, ob_bottom, "Bullish OB"):
                continue

            valid_obs.append({
                "type":   "Bullish OB",
                "top":    ob_top,
                "bottom": ob_bottom,
                "fvg":    fvg,
                "index":  i,
                "time":   candle["time"]
            })

        # ── BEARISH ORDER BLOCK ──
        if bias == "bearish" and is_bullish:
            if not is_impulse(df_1h, i + 1):
                continue
            if df_1h["close"].iloc[i + 1] > df_1h["open"].iloc[i + 1]:
                continue  # must close bearish

            fvg = find_fvg(df_1h, i + 1)
            if fvg is None or "Bearish" not in fvg["type"]:
                continue

            ob_top    = candle["close"]
            ob_bottom = candle["open"]

            if not has_liquidity_near_ob(df_1h, i, ob_top, ob_bottom, "Bearish OB"):
                continue

            valid_obs.append({
                "type":   "Bearish OB",
                "top":    ob_top,
                "bottom": ob_bottom,
                "fvg":    fvg,
                "index":  i,
                "time":   candle["time"]

                
            })

    return valid_obs

def is_ob_mitigated(df_1h, ob):
    """
    An OB is mitigated if price has already traded back 
    into it after it formed — meaning it's been used up.
    """
    ob_index = ob["index"]
    
    # Look at all candles AFTER the OB formed
    future_candles = df_1h.iloc[ob_index + 2:]
    
    if ob["type"] == "Bullish OB":
        # Mitigated if any future candle closed below the OB bottom
        mitigated = (future_candles["close"] < ob["bottom"]).any()
    else:
        # Mitigated if any future candle closed above the OB top
        mitigated = (future_candles["close"] > ob["top"]).any()
    
    return mitigated

