import asyncio
import requests

def send_telegram_message(token, chat_id, message):
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": message,
        "parse_mode": "Markdown",
        "disable_web_page_preview": False
    }
    res = requests.post(url, json=payload)
    return res.status_code == 200

def notify_new_chapters(new_chapters, token, chat_id):
    if not new_chapters:
        print("No hay capítulos nuevos.")
        return
    
    for item in new_chapters:
        message = (
            f"📖 *Nuevo capítulo disponible!*\n\n"
            f"*{item['title']}*\n"
            f" {item['chapter']}\n"
            f" [Leer ahora]({item['url']})"
        )
        success = send_telegram_message(token, chat_id, message)
        if success:
            print(f"Notificación enviada: {item['title']}")
        else:
            print(f" Error enviando: {item['title']}")