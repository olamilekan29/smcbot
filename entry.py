from config import SL_BUFFER, RR_RATIO


def price_in_ob_zone(df_15m, ob):
    """Is current price inside the OB zone?"""
    current = df_15m["close"].iloc[-1]
    return ob["bottom"] <= current <= ob["top"]


def detect_liquidity_sweep(df_15m, ob):
    """
    A valid entry requires:
    1. Price enters the OB zone
    2. A candle wicks THROUGH the OB (sweeping liquidity inside)
    3. That candle then CLOSES back in the opposite direction
    This confirms smart money swept the stops before moving.
    """
    # Look at last 6 candles on 15M
    recent = df_15m.tail(6).reset_index(drop=True)

    for i in range(1, len(recent)):
        candle = recent.iloc[i]

        # ── BULLISH: sweep below OB, close above ──
        if ob["type"] == "Bullish OB":
            wick_swept_below = candle["low"] < ob["bottom"]
            closed_above     = candle["close"] > ob["bottom"]

            if wick_swept_below and closed_above:
                entry = candle["close"]
                sl    = candle["low"] - SL_BUFFER
                risk  = entry - sl
                tp    = entry + (risk * RR_RATIO)

                return {
                    "swept":   True,
                    "signal":  "BUY",
                    "entry":   entry,
                    "sl":      sl,
                    "tp":      tp,
                    "risk_pips": round(risk * 10000, 1),
                    "reason":  "Liquidity swept below Bullish OB — price closed back above"
                }

        # ── BEARISH: sweep above OB, close below ──
        if ob["type"] == "Bearish OB":
            wick_swept_above = candle["high"] > ob["top"]
            closed_below     = candle["close"] < ob["top"]

            if wick_swept_above and closed_below:
                entry = candle["close"]
                sl    = candle["high"] + SL_BUFFER
                risk  = sl - entry
                tp    = entry - (risk * RR_RATIO)

                return {
                    "swept":   True,
                    "signal":  "SELL",
                    "entry":   entry,
                    "sl":      sl,
                    "tp":      tp,
                    "risk_pips": round(risk * 10000, 1),
                    "reason":  "Liquidity swept above Bearish OB — price closed back below"
                }

    return {"swept": False}