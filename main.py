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
        return False, "HATA: TELEGRAM_BOT_TOKEN veya TELEGRAM_CHAT_ID bulunamadı!"
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": message,
        "parse_mode": "HTML"
    }
    try:
        res = requests.post(url, json=payload, timeout=10)
        if res.status_code == 200:
            return True, "Mesaj başarıyla gönderildi!"
        else:
            return False, f"Telegram Yanıt Hatası ({res.status_code}): {res.text}"
    except Exception as e:
        return False, f"Bağlantı Hatası: {str(e)}"

def su_hatirlatici_loop():
    turkey_tz = timezone(timedelta(hours=3))
    last_sent_hour = -1

    # Açılış Mesajı
    send_telegram_message(
        "🥤 <b>Su Hatırlatıcı Ajanınız Göreve Başladı!</b>\n\n"
        "📊 <b>Kişisel Analiz:</b> 75 kg kilonuza göre günlük su ihtiyacınız <b>2.6 Litre</b> (~13 bardak).\n"
        "⏰ Her gün <b>08:00 – 22:00</b> saatleri arasında her saat başı size 1 bardak su içmenizi hatırlatacağım!"
    )

    while True:
        now = datetime.now(turkey_tz)
        current_hour = now.hour

        if 8 <= current_hour <= 22 and current_hour != last_sent_hour:
            msg = (
                f"💧 <b>Su Molası Zamanı!</b> (Saat: {now.strftime('%H:00')})\n\n"
                f"Günlük hedefinize ulaşmak için lütfen şimdi <b>1 bardak (200 ml)</b> taze su için. 🥤\n\n"
                f"<i>(Günlük Toplam Hedef: 2.6 Litre)</i>"
            )
            send_telegram_message(msg)
            last_sent_hour = current_hour

        time.sleep(30)

@app.route('/')
def home():
    return "Su Hatırlatıcı Ajanı 7/24 Aktif!", 200

# Canlı Test Bağlantısı
@app.route('/test')
def test_msg():
    success, response_text = send_telegram_message(
        "🧪 <b>Test Mesajı:</b> Su botu bağlantısı başarıyla doğrulandı!"
    )
    return f"<h2>Test Sonucu</h2><p>{response_text}</p>", 200

if __name__ == "__main__":
    t = threading.Thread(target=su_hatirlatici_loop, daemon=True)
    t.start()

    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
