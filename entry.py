# from config import SL_BUFFER, RR_RATIO


# def price_in_ob_zone(df_15m, ob):
#     """Is current price inside the OB zone?"""
#     current = df_15m["close"].iloc[-1]
#     return ob["bottom"] <= current <= ob["top"]


# def detect_liquidity_sweep(df_15m, ob):
#     """
#     A valid entry requires:
#     1. Price enters the OB zone
#     2. A candle wicks THROUGH the OB (sweeping liquidity inside)
#     3. That candle then CLOSES back in the opposite direction
#     This confirms smart money swept the stops before moving.
#     """
#     # Look at last 6 candles on 15M
#     recent = df_15m.tail(6).reset_index(drop=True)

#     for i in range(1, len(recent)):
#         candle = recent.iloc[i]

#         # ── BULLISH: sweep below OB, close above ──
#         if ob["type"] == "Bullish OB":
#             wick_swept_below = candle["low"] < ob["bottom"]
#             closed_above     = candle["close"] > ob["bottom"]

#             if wick_swept_below and closed_above:
#                 entry = candle["close"]
#                 sl    = candle["low"] - SL_BUFFER
#                 risk  = entry - sl
#                 tp    = entry + (risk * RR_RATIO)

#                 return {
#                     "swept":   True,
#                     "signal":  "BUY",
#                     "entry":   entry,
#                     "sl":      sl,
#                     "tp":      tp,
#                     "risk_pips": round(risk * 10000, 1),
#                     "reason":  "Liquidity swept below Bullish OB — price closed back above"
#                 }

#         # ── BEARISH: sweep above OB, close below ──
#         if ob["type"] == "Bearish OB":
#             wick_swept_above = candle["high"] > ob["top"]
#             closed_below     = candle["close"] < ob["top"]

#             if wick_swept_above and closed_below:
#                 entry = candle["close"]
#                 sl    = candle["high"] + SL_BUFFER
#                 risk  = sl - entry
#                 tp    = entry - (risk * RR_RATIO)

#                 return {
#                     "swept":   True,
#                     "signal":  "SELL",
#                     "entry":   entry,
#                     "sl":      sl,
#                     "tp":      tp,
#                     "risk_pips": round(risk * 10000, 1),
#                     "reason":  "Liquidity swept above Bearish OB — price closed back below"
#                 }

#     return {"swept": False}




# def detect_liquidity_sweep(df_15m, ob):
#     recent = df_15m.tail(6).reset_index(drop=True)

#     for i in range(1, len(recent)):
#         candle = recent.iloc[i]

#         if ob["type"] == "Bullish OB":
#             wick_swept   = candle["low"] < ob["bottom"]
#             closed_above = candle["close"] > ob["bottom"]
            
#             # New: close must be in upper 50% of candle body (strong rejection)
#             candle_range = candle["high"] - candle["low"]
#             strong_close = candle_range > 0 and \
#                            (candle["close"] - candle["low"]) / candle_range > 0.5

#             if wick_swept and closed_above and strong_close:
#                 entry = candle["close"]
#                 sl    = candle["low"] - SL_BUFFER
#                 risk  = entry - sl
#                 tp    = entry + (risk * RR_RATIO)

#                 return {
#                     "swept":      True,
#                     "signal":     "BUY",
#                     "entry":      entry,
#                     "sl":         sl,
#                     "tp":         tp,
#                     "risk_pips":  round(risk * 10000, 1),
#                     "reason":     "Liquidity swept below Bullish OB — strong rejection"
#                 }

#         if ob["type"] == "Bearish OB":
#             wick_swept   = candle["high"] > ob["top"]
#             closed_below = candle["close"] < ob["top"]

#             # New: close must be in lower 50% of candle body (strong rejection)
#             candle_range = candle["high"] - candle["low"]
#             strong_close = candle_range > 0 and \
#                            (candle["high"] - candle["close"]) / candle_range > 0.5

#             if wick_swept and closed_below and strong_close:
#                 entry = candle["close"]
#                 sl    = candle["high"] + SL_BUFFER
#                 risk  = sl - entry
#                 tp    = entry - (risk * RR_RATIO)

#                 return {
#                     "swept":      True,
#                     "signal":     "SELL",
#                     "entry":      entry,
#                     "sl":         sl,
#                     "tp":         tp,
#                     "risk_pips":  round(risk * 10000, 1),
#                     "reason":     "Liquidity swept above Bearish OB — strong rejection"
#                 }

#     return {"swept": False}

from config import SL_BUFFER, RR_RATIO

def price_in_ob_zone(df_15m, ob):
    """Is current price inside the OB zone?"""
    current = df_15m["close"].iloc[-1]
    return ob["bottom"] <= current <= ob["top"]

def detect_liquidity_sweep(df_15m, ob):
    recent = df_15m.tail(6).reset_index(drop=True)
    
    # Minimum sweep size — wick must go at least 3 pips beyond zone
    MIN_SWEEP_PIPS = 0.0003

    for i in range(1, len(recent)):
        candle = recent.iloc[i]
        spread = candle["high"] - candle["low"]

        if spread == 0:
            continue

        if ob["type"] == "Bullish OB":
            sweep_depth  = ob["bottom"] - candle["low"]  # how far below OB it went
            closed_above = candle["close"] > ob["bottom"]

            # Wick must go meaningfully below OB — not just tickle it
            real_sweep = sweep_depth >= MIN_SWEEP_PIPS

            # Close must be in upper 60% of candle — strong bullish rejection
            close_position = (candle["close"] - candle["low"]) / spread
            strong_close   = close_position >= 0.60

            # Wick below must be visible but body must close back up
            wick_below = candle["low"] < ob["bottom"]

            if wick_below and real_sweep and closed_above and strong_close:
                entry = candle["close"]
                sl    = candle["low"] - SL_BUFFER
                risk  = entry - sl
                tp    = entry + (risk * RR_RATIO)

                return {
                    "swept":     True,
                    "signal":    "BUY",
                    "entry":     entry,
                    "sl":        sl,
                    "tp":        tp,
                    "risk_pips": round(risk * 10000, 1),
                    "reason":    f"Real sweep below Bullish OB ({sweep_depth*10000:.1f} pips) — strong rejection"
                }

        if ob["type"] == "Bearish OB":
            sweep_depth  = candle["high"] - ob["top"]  # how far above OB it went
            closed_below = candle["close"] < ob["top"]

            real_sweep = sweep_depth >= MIN_SWEEP_PIPS

            # Close must be in lower 60% of candle — strong bearish rejection
            close_position = (candle["high"] - candle["close"]) / spread
            strong_close   = close_position >= 0.60

            wick_above = candle["high"] > ob["top"]

            if wick_above and real_sweep and closed_below and strong_close:
                entry = candle["close"]
                sl    = candle["high"] + SL_BUFFER
                risk  = sl - entry
                tp    = entry - (risk * RR_RATIO)

                return {
                    "swept":     True,
                    "signal":    "SELL",
                    "entry":     entry,
                    "sl":        sl,
                    "tp":        tp,
                    "risk_pips": round(risk * 10000, 1),
                    "reason":    f"Real sweep above Bearish OB ({sweep_depth*10000:.1f} pips) — strong rejection"
                }

    return {"swept": False}