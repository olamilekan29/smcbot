from data   import get_candles
from bias   import get_bias
from poi    import get_valid_obs
from entry  import price_in_ob_zone, detect_liquidity_sweep
from config import TF_BIAS, TF_POI, TF_ENTRY, CANDLE_COUNT


def run_strategy(symbol):
    print(f"\n🔍 Scanning {symbol}...")

    # ── STEP 1: 4H Bias ──
    df_4h = get_candles(symbol, TF_BIAS, CANDLE_COUNT)
    if df_4h is None or df_4h.empty:
        return None

    bias = get_bias(df_4h)
    print(f"   4H Bias: {bias.upper()}")

    if bias == "consolidation":
        print(f"   ⏭ Skipping — consolidation")
        return None

    # ── STEP 2: 1H Valid OBs ──
    df_1h = get_candles(symbol, TF_POI, CANDLE_COUNT)
    if df_1h is None or df_1h.empty:
        return None

    valid_obs = get_valid_obs(df_1h, bias)
    print(f"   Valid OBs found: {len(valid_obs)}")

    if not valid_obs:
        return None

    # ── STEP 3: 15M Entry Check ──
    df_15m = get_candles(symbol, TF_ENTRY, 200)
    if df_15m is None or df_15m.empty:
        return None

    # Check most recent OBs first
    for ob in reversed(valid_obs[-5:]):
        if not price_in_ob_zone(df_15m, ob):
            continue

        print(f"   ✅ Price at OB zone — checking for sweep...")
        sweep = detect_liquidity_sweep(df_15m, ob)

        if sweep["swept"]:
            print(f"   🎯 ENTRY FOUND: {sweep['signal']}")
            return {
                **sweep,
                "symbol":  symbol,
                "bias":    bias,
                "ob":      ob,
                "df_15m":  df_15m,
                "df_1h":   df_1h
            }

    return None