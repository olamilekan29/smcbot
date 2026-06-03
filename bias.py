# from config import SWING_LOOKBACK

# def get_swings(df):
#     lb = SWING_LOOKBACK
#     window = lb * 2 + 1
#     highs = df["high"].rolling(window, center=True).max()
#     lows  = df["low"].rolling(window, center=True).min()
#     df = df.copy()
#     df["swing_high"] = df["high"].where(df["high"] == highs)
#     df["swing_low"]  = df["low"].where(df["low"] == lows)
#     return df


# def get_bias(df_4h):
#     df = get_swings(df_4h)

#     # Get last 3 confirmed swing highs and lows
#     swing_highs = df["swing_high"].dropna().values[-3:]
#     swing_lows  = df["swing_low"].dropna().values[-3:]

#     if len(swing_highs) < 2 or len(swing_lows) < 2:
#         return "consolidation"

#     hh = swing_highs[-1] > swing_highs[-2]   # Higher High
#     hl = swing_lows[-1]  > swing_lows[-2]    # Higher Low
#     lh = swing_highs[-1] < swing_highs[-2]   # Lower High
#     ll = swing_lows[-1]  < swing_lows[-2]    # Lower Low

#     if hh and hl:
#         return "bullish"
#     if lh and ll:
#         return "bearish"

#     return "consolidation"



# from config import SWING_LOOKBACK

# def get_swings(df, lookback=5):
#     """
#     Find swing highs and lows by checking if a candle's high/low
#     is the highest/lowest in the surrounding candles.
#     More reliable than rolling center method.
#     """
#     df = df.copy()
#     df["swing_high"] = None
#     df["swing_low"]  = None

#     for i in range(lookback, len(df) - lookback):
#         # Swing High: highest high in the window
#         window_highs = df["high"].iloc[i - lookback: i + lookback + 1]
#         if df["high"].iloc[i] == window_highs.max():
#             df.loc[df.index[i], "swing_high"] = df["high"].iloc[i]

#         # Swing Low: lowest low in the window
#         window_lows = df["low"].iloc[i - lookback: i + lookback + 1]
#         if df["low"].iloc[i] == window_lows.min():
#             df.loc[df.index[i], "swing_low"] = df["low"].iloc[i]

#     return df


# def get_bias(df_4h):
#     df = get_swings(df_4h, lookback=SWING_LOOKBACK)

#     # Get last confirmed swing highs and lows
#     swing_highs = df["swing_high"].dropna().values
#     swing_lows  = df["swing_low"].dropna().values

#     print(f"   Swing highs found: {len(swing_highs)}")
#     print(f"   Swing lows found:  {len(swing_lows)}")

#     if len(swing_highs) < 2 or len(swing_lows) < 2:
#         # Not enough swings detected — lower the lookback and retry
#         df = get_swings(df_4h, lookback=3)
#         swing_highs = df["swing_high"].dropna().values
#         swing_lows  = df["swing_low"].dropna().values
#         print(f"   Retrying with lookback=3 → highs: {len(swing_highs)}, lows: {len(swing_lows)}")

#     if len(swing_highs) < 2 or len(swing_lows) < 2:
#         return "consolidation"

#     # Use last 3 swings for more reliable reading
#     recent_highs = swing_highs[-3:]
#     recent_lows  = swing_lows[-3:]

#     # Bullish conditions
#     hh = recent_highs[-1] > recent_highs[-2]   # Higher High
#     hl = recent_lows[-1]  > recent_lows[-2]    # Higher Low

#     # Bearish conditions
#     lh = recent_highs[-1] < recent_highs[-2]   # Lower High
#     ll = recent_lows[-1]  < recent_lows[-2]    # Lower Low

#     print(f"   HH: {hh} | HL: {hl} | LH: {lh} | LL: {ll}")
#     print(f"   Last 2 highs: {recent_highs[-2]:.5f} → {recent_highs[-1]:.5f}")
#     print(f"   Last 2 lows:  {recent_lows[-2]:.5f} → {recent_lows[-1]:.5f}")

#     # Strong bias — both conditions must be true
#     if hh and hl:
#         return "bullish"
#     if lh and ll:
#         return "bearish"

#     # Partial bias — at least one condition true
#     # This prevents everything collapsing into consolidation
#     if hh or hl:
#         return "bullish"
#     if lh or ll:
#         return "bearish"

#     return "consolidation"


from config import SWING_LOOKBACK

def get_swings(df, lookback=3):
    df = df.copy()
    df["swing_high"] = None
    df["swing_low"]  = None

    for i in range(lookback, len(df) - lookback):
        window_highs = df["high"].iloc[i - lookback: i + lookback + 1]
        if df["high"].iloc[i] == window_highs.max():
            df.loc[df.index[i], "swing_high"] = df["high"].iloc[i]

        window_lows = df["low"].iloc[i - lookback: i + lookback + 1]
        if df["low"].iloc[i] == window_lows.min():
            df.loc[df.index[i], "swing_low"] = df["low"].iloc[i]

    return df


def get_bias(df_4h):
    # ── FIRST: print raw data info so we can see what came in ──
    print(f"   DataFrame rows: {len(df_4h)}")
    print(f"   Columns: {list(df_4h.columns)}")
    print(f"   Last 3 closes: {df_4h['close'].tail(3).values}")
    print(f"   Any NaN in close: {df_4h['close'].isna().any()}")

    if df_4h.empty or len(df_4h) < 10:
        print("   ❌ Not enough data")
        return "consolidation"

    df = get_swings(df_4h, lookback=3)

    swing_highs = df["swing_high"].dropna().values
    swing_lows  = df["swing_low"].dropna().values

    print(f"   Swing highs found: {len(swing_highs)}")
    print(f"   Swing lows found:  {len(swing_lows)}")

    if len(swing_highs) > 0:
        print(f"   Last swing high: {swing_highs[-1]:.5f}")
    if len(swing_lows) > 0:
        print(f"   Last swing low: {swing_lows[-1]:.5f}")

    # Retry with lookback=2 if still not enough
    if len(swing_highs) < 2 or len(swing_lows) < 2:
        print("   Retrying with lookback=2...")
        df = get_swings(df_4h, lookback=2)
        swing_highs = df["swing_high"].dropna().values
        swing_lows  = df["swing_low"].dropna().values
        print(f"   After retry → highs: {len(swing_highs)}, lows: {len(swing_lows)}")

    if len(swing_highs) < 2 or len(swing_lows) < 2:
        print("   ❌ Still not enough swings — returning consolidation")
        return "consolidation"

    recent_highs = swing_highs[-3:]
    recent_lows  = swing_lows[-3:]

    hh = recent_highs[-1] > recent_highs[-2]
    hl = recent_lows[-1]  > recent_lows[-2]
    lh = recent_highs[-1] < recent_highs[-2]
    ll = recent_lows[-1]  < recent_lows[-2]

    print(f"   HH:{hh} HL:{hl} LH:{lh} LL:{ll}")
    print(f"   Highs: {recent_highs[-2]:.5f} → {recent_highs[-1]:.5f}")
    print(f"   Lows:  {recent_lows[-2]:.5f} → {recent_lows[-1]:.5f}")

    if hh and hl: return "bullish"
    if lh and ll: return "bearish"
    if hh or hl:  return "bullish"
    if lh or ll:  return "bearish"

    return "consolidation"