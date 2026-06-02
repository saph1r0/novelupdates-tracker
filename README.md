# 📚 NovelUpdates Chapter Tracker Bot

A Python bot that monitors your favorite web novels on NovelUpdates 
and sends instant Telegram notifications when a new chapter drops.

Built by a CS student who got tired of refreshing NovelUpdates 
every hour for BL/danmei updates.

## Features

- Tracks multiple novels simultaneously
- Sends formatted Telegram notifications with direct chapter links
- Runs every 2 hours automatically
- Saves state between runs (no duplicate notifications)
- Easy to add/remove novels via JSON config

## Tech Stack

- Python 3.10+
- BeautifulSoup4 for HTML parsing
- python-telegram-bot for notifications
- schedule for task automation

## Setup

### 1. Clone the repo
git clone https://github.com/TUUSUARIO/novelupdates-tracker
cd novelupdates-tracker

### 2. Install dependencies
pip install requests beautifulsoup4 python-telegram-bot schedule

### 3. Create your Telegram bot
- Open Telegram and search for @BotFather
- Send /newbot and follow the steps
- Copy your bot TOKEN

### 4. Get your chat ID
- Search for @userinfobot on Telegram
- Send any message — it replies with your chat ID

### 5. Configure
Open main.py and fill in:
TELEGRAM_TOKEN = "your_token_here"
CHAT_ID = "your_chat_id_here"

### 6. Add your novels
Edit novels.json with the slugs from NovelUpdates URLs.
Example: novelupdates.com/series/heaven-officials-blessing/
→ slug is: heaven-officials-blessing

### 7. Run
python main.py

## Notification Preview

The bot sends messages like this to your Telegram:

📖 New chapter available!
Heaven Official's Blessing
📌 Chapter 244
🔗 Read now → [link]

## Roadmap

- [ ] Web interface to manage novel list
- [ ] Support for MangaDex (manga tracking)
- [ ] Daily digest mode (one summary instead of per-chapter alerts)
- [ ] AniList integration for anime adaptations

## Why I built this

I read danmei and BL novels obsessively and kept missing chapter 
releases. As a CS student I thought — why refresh manually 
when Python exists?

## License
MIT