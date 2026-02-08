import json
import logging
import os

from discord.ext import commands

with open(f"{os.path.dirname(__file__)}/config/config.json", "r", encoding="utf-8") as f:
    cfg = json.load(f)

logger = logging.getLogger(__name__)

class TelegramDiscordCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.logger = logging.getLogger(__name__)