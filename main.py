import asyncio
from strategy import run_strategy
from chart    import generate_chart
from bot      import send_alert, send_startup_message
from config   import PAIRS

sent_signals = set()

async def scan_all_pairs():
    for symbol in PAIRS:
        try:
            print(f"\n⏳ Scanning {symbol}...")
            signal = run_strategy(symbol)

            if signal:
                key = f"{symbol}_{signal['signal']}_{signal['entry']:.5f}"
                if key not in sent_signals:
                    chart_path = generate_chart(signal)
                    await send_alert(signal, chart_path)
                    sent_signals.add(key)
                    print(f"✅ Alert sent: {symbol} {signal['signal']} @ {signal['entry']:.5f}")

                    if len(sent_signals) > 50:
                        sent_signals.pop()

        except Exception as e:
            print(f"❌ Error on {symbol}: {e}")

        # Wait 30 seconds between each pair
        # 3 calls per pair × 5 pairs = 15 calls total
        # Spreading them 30s apart keeps you under the 8/min limit
        await asyncio.sleep(30)


async def main():
    print("🤖 SMC Forex Bot Starting...")
    await send_startup_message()

    while True:
        print("\n🔍 Starting full scan...")
        await scan_all_pairs()
        print("\n✅ Full scan done. Next scan in 30 minutes...")
        await asyncio.sleep(1800)  # 5 min break between full scans

asyncio.run(main())