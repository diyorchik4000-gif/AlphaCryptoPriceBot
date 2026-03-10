import telebot
import requests
import time
from datetime import datetime, timedelta, timezone
import threading
import os
from dotenv import load_dotenv

# .env fayldan tokenni o'qish
load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")
if TOKEN is None or ":" not in TOKEN:
    raise ValueError("BOT_TOKEN .env faylda noto'g'ri yoki mavjud emas!")

bot = telebot.TeleBot(TOKEN)

# Auto update interval: 1 daqiqa
interval = 60  # soniyada

# Kripto valyutalar va Binance symbol
coins = {
    "BTC": "BTCUSDT",
    "ETH": "ETHUSDT",
    "BNB": "BNBUSDT",
    "SOL": "SOLUSDT",
    "LTC": "LTCUSDT",
    "TON": "TONUSDT",
    "TRX": "TRXUSDT",
    "DOGE": "DOGEUSDT"
}

# Emoji ID (Premium foydalanuvchi bo'lsa ishlaydi)
emoji_id = {
    "BTC": "5298576341325618295",
    "ETH": "5296440836341409169",
    "BNB": "5215501052366852398",
    "SOL": "5296561443318046092",
    "LTC": "5298529088095423527",
    "TON": "5298853611529344388",
    "TRX": "5296496924319328479",
    "DOGE": "5296472481660443203"
}

user_messages = {}  # chat_id: message_id
running_chats = set()
tz_tashkent = timezone(timedelta(hours=5))

# Binance narxlarini olish
def get_prices():
    prices = {}
    try:
        r = requests.get("https://api.binance.com/api/v3/ticker/price", timeout=5)
        data = r.json()
        for coin, symbol in coins.items():
            for item in data:
                if item["symbol"] == symbol:
                    prices[coin] = float(item["price"])
                    break
    except:
        pass
    return prices

# Xabarni qurish
def build_message(prices):
    now = datetime.now(tz=tz_tashkent)
    time_str = now.strftime("%H:%M")      # HH:MM
    date_str = now.strftime("%d/%m/%Y")   # DD/MM/YYYY

    text = f"<b>💰 AlphaCryptoPrice</b>\n\n<b>{date_str} {time_str}</b>\n\n"

    for coin in coins:
        price = prices.get(coin, 0)
        icon = f"<tg-emoji emoji-id='{emoji_id[coin]}'>🙂</tg-emoji>"
        text += f"{icon} {coin} | ${price:,.2f} | {time_str}\n\n"

    text += f"🔄 Auto Update: {interval} sec"
    return text

# /start komandasi
@bot.message_handler(commands=['start'])
def start(message):
    chat_id = message.chat.id

    # Agar chat allaqachon ishlayotgan bo'lsa, faqat xabarni edit qilamiz
    if chat_id in running_chats:
        try:
            prices = get_prices()
            msg = build_message(prices)
            bot.edit_message_text(msg, chat_id, user_messages[chat_id], parse_mode="HTML")
        except:
            sent = bot.send_message(chat_id, build_message(get_prices()), parse_mode="HTML")
            user_messages[chat_id] = sent.message_id
        return

    # Yangi chat uchun faqat 1 xabar yuboriladi
    sent = bot.send_message(chat_id, build_message(get_prices()), parse_mode="HTML")
    user_messages[chat_id] = sent.message_id
    running_chats.add(chat_id)

    # Auto update fon thread
    def updater():
        while True:
            start_time = time.time()
            prices = get_prices()
            msg = build_message(prices)
            try:
                bot.edit_message_text(msg, chat_id, user_messages[chat_id], parse_mode="HTML")
            except:
                sent = bot.send_message(chat_id, msg, parse_mode="HTML")
                user_messages[chat_id] = sent.message_id
            elapsed = time.time() - start_time
            time.sleep(max(0, interval - elapsed))

    threading.Thread(target=updater, daemon=True).start()

# Botni ishga tushurish
bot.infinity_polling()
