import os  
import asyncio
import requests

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN", "")
CHAT_ID = os.environ.get("CHAT_ID", "")

def send_telegram_message(token, chat_id, message):
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": message,
        "parse_mode": "Markdown",
        "disable_web_page_preview": False
    }
    try:
        res = requests.post(url, json=payload, timeout=10)
        return res.status_code == 200
    except Exception as e:
        print(f" ❌ Error enviando a Telegram: {e}")
        return False

def notify_new_chapters(new_chapters):
    if not TELEGRAM_TOKEN or not CHAT_ID:
        print(" ⚠️ ERROR: TELEGRAM_TOKEN o CHAT_ID no configurados en el panel de Render.")
        return

    if not new_chapters:
        print("No hay capítulos nuevos.")
        return
    
    for item in new_chapters:
        message = (
            f"📖 *Nuevo capítulo disponible!*\n\n"
            f"*{item['title']}*\n"
            f" {item['chapter']}\n\n"
            f"🔗 [Leer ahora]({item['url']})"
        )
        success = send_telegram_message(TELEGRAM_TOKEN, CHAT_ID, message)
        if success:
            print(f"Notificación enviada: {item['title']}", flush=True)
        else:
            print(f" ❌ Error enviando: {item['title']}", flush=True)