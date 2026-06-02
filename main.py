import json
import schedule
import time
import os
import sys
from tracker import check_new_chapters
from bot import notify_new_chapters
from dotenv import load_dotenv
load_dotenv()

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN", "")
CHAT_ID = os.environ.get("CHAT_ID", "")

if not TELEGRAM_TOKEN or not CHAT_ID:
    print("❌ ERROR: Faltan variables de entorno TELEGRAM_TOKEN y CHAT_ID")
    sys.exit(1)

def load_novels():
    with open("novels.json", "r") as f:
        return json.load(f)["novels"]

def run_check():
    print("\n🔍 Chequeando capítulos nuevos...")
    novels = load_novels()
    new_chapters = check_new_chapters(novels)
    notify_new_chapters(new_chapters, TELEGRAM_TOKEN, CHAT_ID)

run_check()

if "--once" not in sys.argv:
    schedule.every(2).hours.do(run_check)
    print("🤖 Bot activo. Chequeando cada 2 horas...")
    while True:
        schedule.run_pending()
        time.sleep(60)