from data   import get_candles
from bias   import get_bias
from poi    import get_valid_obs
from entry  import price_in_ob_zone, detect_liquidity_sweep
from config import TF_BIAS, TF_POI, TF_ENTRY, CANDLE_COUNT


def run_strategy(symbol):
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

    current_price = df_15m["close"].iloc[-1]
    print(f"   Current price: {current_price:.5f}")

    for ob in reversed(valid_obs[-5:]):
        print(f"   Checking OB → {ob['type']} | Zone: {ob['bottom']:.5f} – {ob['top']:.5f}")

        in_zone = price_in_ob_zone(df_15m, ob)
        print(f"   Price in zone: {in_zone}")

        if not in_zone:
            continue

        sweep = detect_liquidity_sweep(df_15m, ob)
        print(f"   Sweep detected: {sweep['swept']}")

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

    print(f"   ⏳ OBs found but price not at any zone yet")
    return None