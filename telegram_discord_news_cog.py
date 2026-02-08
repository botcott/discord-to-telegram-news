import json
import logging
import os
import re
from dotenv import load_dotenv
from discord.ext import commands
from telethon import TelegramClient

# Загрузка конфига
with open(f"{os.path.dirname(__file__)}/config/config.json", "r", encoding="utf-8") as f:
    cfg = json.load(f)

NOTIF_CHANNEL = int(cfg["notif_channel"])
DS14_CHANGES_CHANNEL = int(cfg["ds14_changes_channel"])
TELEGRAM_CHAT_ID = int(cfg["telegram_chat_id"])

load_dotenv()
API_ID = os.getenv("api_id")
API_HASH = os.getenv("api_hash")

def handle_headers(m):
    hashes = m.group(1)
    text = m.group(2).strip()
    return f'<b>{text}</b>\n' if len(hashes) > 1 else f'<b>{text}</b>'

class TelegramDiscordCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.tg_client = None

    async def cog_load(self):
        # API_ID и API_HASH должны быть числами/строками из вашего конфига
        self.tg_client = TelegramClient('user_session', API_ID, API_HASH)
        
        print("Подключение к Telegram...")
        await self.tg_client.start()
        print("Telegram успешно подключен!")

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.channel.id not in (NOTIF_CHANNEL, DS14_CHANGES_CHANNEL):
            return

        content = message.content

        # Обработка упоминаний каналов
        channel_mentions = re.findall(r'<#(\d+)>', content)
        for ch_id in channel_mentions:
            channel_obj = self.bot.get_channel(int(ch_id))
            ch_name = channel_obj.name if channel_obj else "неизвестный-канал"
            content = content.replace(f'<#{ch_id}>', f'канал "{ch_name}"')

        # Замена эмодзи
        emoji_map = {":hammer_pick:": "🛠️", ":new:": "🆕", ":x:": "❌", ":bug:": "🐛"}
        for code, emoji in emoji_map.items():
            content = content.replace(code, emoji)

        # Очистка и форматирование (как в вашем коде)
        content = re.sub(r'@(everyone|here)', '', content)
        content = re.sub(r'<@!?\d+>', '', content)
        content = re.sub(r'<@&\d+>', '', content)
        content = re.sub(r':\w+:', '', content)
        content = re.sub(r'^(#{1,4})\s+(.*)', handle_headers, content, flags=re.MULTILINE)
        content = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'<a href="\2">\1</a>', content)
        content = re.sub(r'\*\*(.*?)\*\*', r'\1', content)
        content = re.sub(r'(\*|_)(.*?)(\*|_)', r'\2', content)
        content = re.sub(r'~~(.*?)~~', r'\1', content)
        content = re.sub(r'`(.*?)`', r'\1', content)
        content = re.sub(r'```.*?```', '', content, flags=re.DOTALL)
        content = "\n".join(line.strip() for line in content.splitlines() if line.strip())

        prefix = "Из канала \"оповещения\":\n\n" if message.channel.id == NOTIF_CHANNEL else "Из канала \"мк-изменения\":\n\n"
        message_to_telegram = prefix + content

        if not message_to_telegram.strip():
            return

        if self.tg_client and self.tg_client.is_connected():
            await self.tg_client.send_message(
                TELEGRAM_CHAT_ID, 
                message_to_telegram, 
                parse_mode='html',
                link_preview=False
            )