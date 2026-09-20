import os
import time
import threading
from datetime import datetime, timezone, timedelta
from flask import Flask
import requests

app = Flask(__name__)

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

def send_telegram_message(message):
    if not BOT_TOKEN or not CHAT_ID:
        print("HATA: Telegram Token veya Chat ID bulunamadı!")
        return
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": message,
        "parse_mode": "Markdown"
    }
    try:
        requests.post(url, json=payload, timeout=10)
    except Exception as e:
        print(f"Gönderim hatası: {e}")

def su_hatirlatici_loop():
    # Türkiye Saati (UTC+3)
    turkey_tz = timezone(timedelta(hours=3))
    last_sent_hour = -1

    # İlk Çalışma Mesajı
    send_telegram_message(
        "🥤 *Su Hatırlatıcı Ajanınız Göreve Başladı!*\n\n"
        "📊 *Kişisel Analiz:* 75 kg kilonuza göre günlük su ihtiyacınız **2.6 Litre** (~13 bardak).\n"
        "⏰ Her gün **08:00 – 22:00** saatleri arasında her saat başı size 1 bardak su içmenizi hatırlatacağım!"
    )

    while True:
        now = datetime.now(turkey_tz)
        current_hour = now.hour

        # 08:00 ile 22:00 saatleri arasında her saat başı mesaj at
        if 8 <= current_hour <= 22 and current_hour != last_sent_hour:
            msg = (
                f"💧 *Su Molası Zamanı!* (Saat: {now.strftime('%H:00')})\n\n"
                f"Günlük hedefinize ulaşmak için lütfen şimdi **1 bardak (200 ml)** taze su için. 🥤\n\n"
                f"*(Günlük Toplam Hedef: 2.6 Litre)*"
            )
            send_telegram_message(msg)
            last_sent_hour = current_hour

        time.sleep(30)  # 30 saniyede bir saati kontrol et

@app.route('/')
def home():
    return "Su Hatırlatıcı Ajanı 7/24 Aktif!", 200

if __name__ == "__main__":
    # Arka planda su zamanlayıcısını başlat
    t = threading.Thread(target=su_hatirlatici_loop, daemon=True)
    t.start()

    # Web sunucusunu başlat (Render için)
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)