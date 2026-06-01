from config import SWING_LOOKBACK

def get_swings(df):
    lb = SWING_LOOKBACK
    window = lb * 2 + 1
    highs = df["high"].rolling(window, center=True).max()
    lows  = df["low"].rolling(window, center=True).min()
    df = df.copy()
    df["swing_high"] = df["high"].where(df["high"] == highs)
    df["swing_low"]  = df["low"].where(df["low"] == lows)
    return df


def get_bias(df_4h):
    df = get_swings(df_4h)

    # Get last 3 confirmed swing highs and lows
    swing_highs = df["swing_high"].dropna().values[-3:]
    swing_lows  = df["swing_low"].dropna().values[-3:]

    if len(swing_highs) < 2 or len(swing_lows) < 2:
        return "consolidation"

    hh = swing_highs[-1] > swing_highs[-2]   # Higher High
    hl = swing_lows[-1]  > swing_lows[-2]    # Higher Low
    lh = swing_highs[-1] < swing_highs[-2]   # Lower High
    ll = swing_lows[-1]  < swing_lows[-2]    # Lower Low

    if hh and hl:
        return "bullish"
    if lh and ll:
        return "bearish"

    return "consolidation"