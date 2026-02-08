import json
import logging
import os
import re
import subprocess
from urllib.parse import quote

from discord.ext import commands

with open(f"{os.path.dirname(__file__)}/config/config.json", "r", encoding="utf-8") as f:
    cfg = json.load(f)

logger = logging.getLogger(__name__)

# config.json
NOTIF_CHANNEL = int(cfg["notif_channel"])
DS14_CHANGES_CHANNEL = int(cfg["ds14_changes_channel"])
TELEGRAM_CHAT_ID = cfg.get("telegram_chat_id")

# .env
from dotenv import load_dotenv
load_dotenv()
TELEGRAM_BOT_TOKEN = os.getenv("token") 

class TelegramDiscordCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.logger = logging.getLogger(__name__)

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.channel.id not in (NOTIF_CHANNEL, DS14_CHANGES_CHANNEL):
            return

        if message.channel.id == NOTIF_CHANNEL:
            prefix = "Из канала \"оповещения\": "
        elif message.channel.id == DS14_CHANGES_CHANNEL:
            prefix = "Из канала \"мк-изменения\": "
        else:
            prefix = ""

        content = message.content
        
        content = re.sub(r'<@!?\d+>', '', content) # Упоминания 
        content = re.sub(r'<a?:\w+:\d+>', '', content) # Дискордз эмодзи
        content = re.sub(r'[^\x00-\x7F\u0400-\u04FF\s\w\d\p{P}]', '', content) # Юникод эмодзи
        content = ' '.join(content.split()) # Лишние пробелы

        message_to_telegram = prefix + content

        if not message_to_telegram.strip():
            return

        try:
            escaped_message = quote(message_to_telegram)

            curl_cmd = (
                f'curl -s -X POST '
                f'"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage" '
                f'-d "chat_id={TELEGRAM_CHAT_ID}&text={escaped_message}"'
            ); result = subprocess.run(curl_cmd, shell=True, capture_output=True, text=True)

            if result.returncode != 0:
                self.logger.error(f"Ошибка curl: {result.stderr}")
            else:
                self.logger.info(f"Отправлено в Telegram: {message_to_telegram}")
        except Exception as e:
            self.logger.error(e)
