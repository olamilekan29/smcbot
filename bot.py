import os
from telegram import Bot
from dotenv import load_dotenv

load_dotenv()

bot     = Bot(token=os.getenv("BOT_TOKEN"))
CHAT_ID = os.getenv("CHAT_ID")


async def send_alert(signal, chart_path):
    direction = "🟢 BUY" if signal["signal"] == "BUY" else "🔴 SELL"

    message = f"""
{direction} *{signal['symbol']}*

📊 *4H Bias:* {signal['bias'].upper()}
📍 *Setup:* {signal['reason']}

━━━━━━━━━━━━━━━━━━
💰 *Entry:*      `{signal['entry']:.5f}`
🛑 *Stop Loss:*  `{signal['sl']:.5f}`
🎯 *Take Profit:*`{signal['tp']:.5f}`
📐 *RR Ratio:*   1:{3}
⚡ *Risk (pips):* {signal['risk_pips']}
━━━━━━━━━━━━━━━━━━

✅ Valid OB (Impulse + FVG + Liquidity)
✅ Price returned to OB zone
✅ Liquidity swept at zone
    """

    await bot.send_photo(
        chat_id=CHAT_ID,
        photo=open(chart_path, "rb"),
        caption=message,
        parse_mode="Markdown"
    )


async def send_startup_message():
    await bot.send_message(
        chat_id=CHAT_ID,
        text="🤖 *SMC Forex Bot is now LIVE*\nScanning pairs every 60 seconds...",
        parse_mode="Markdown"
    )