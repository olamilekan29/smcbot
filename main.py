import asyncio
from strategy import run_strategy
from chart    import generate_chart
from bot      import send_alert, send_startup_message
from config   import PAIRS

# Tracks sent signals to avoid duplicate alerts
sent_signals = set()


async def scan_all_pairs():
    for symbol in PAIRS:
        try:
            signal = run_strategy(symbol)

            if signal:
                # Create unique key for this signal
                key = f"{symbol}_{signal['signal']}_{signal['entry']:.5f}"

                if key not in sent_signals:
                    chart_path = generate_chart(signal)
                    await send_alert(signal, chart_path)
                    sent_signals.add(key)
                    print(f"✅ Alert sent: {symbol} {signal['signal']} @ {signal['entry']:.5f}")

                    # Stop tracking old signals after 50 to keep memory clean
                    if len(sent_signals) > 50:
                        sent_signals.pop()

        except Exception as e:
            print(f"❌ Error on {symbol}: {e}")


async def main():
    print("🤖 SMC Forex Bot Starting...")
    await send_startup_message()

    while True:
        print("\n⏳ Scanning all pairs...")
        await scan_all_pairs()
        print("✅ Scan complete. Waiting 60 seconds...")
        await asyncio.sleep(60)


asyncio.run(main())