import telebot
import requests
import time
from datetime import datetime, timedelta, timezone
import threading

# TOKENni to'g'ridan-to'g'ri yozish
TOKEN = "8134986426:AAECKwFDVrFqeN9gH9Z6f_ZddOhZ6Ukw7ss"

bot = telebot.TeleBot(TOKEN)

# Auto update interval: 1 daqiqa
interval = 60  # soniyada

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

emoji_id = {
    "BTC": "5298576341325618295",
    "ETH": "5296624321639259043",
    "BNB": "5215501052366852398",
    "SOL": "5296561443318046092",
    "LTC": "5298529088095423527",
    "TON": "5298853611529344388",
    "TRX": "5296496924319328479",
    "DOGE": "5296472481660443203"
}

user_messages = {}  
running_chats = set()
tz_tashkent = timezone(timedelta(hours=5))

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

def build_message(prices):
    now = datetime.now(tz=tz_tashkent)
    time_str = now.strftime("%H:%M")
    date_str = now.strftime("%d/%m/%Y")

    text = f"<b>💰 AlphaCryptoPrice</b>\n\n<b>{date_str} {time_str}</b>\n\n"
    for coin in coins:
        price = prices.get(coin, 0)
        icon = f"<tg-emoji emoji-id='{emoji_id[coin]}'>🙂</tg-emoji>"
        text += f"{icon} {coin} | ${price:,.2f} | {time_str}\n\n"
    text += f"🔄 Auto Update: {interval} sec"
    return text

@bot.message_handler(commands=['start'])
def start(message):
    chat_id = message.chat.id
    if chat_id in running_chats:
        return
    sent = bot.send_message(chat_id, build_message(get_prices()), parse_mode="HTML")
    user_messages[chat_id] = sent.message_id
    running_chats.add(chat_id)

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

bot.infinity_polling()
