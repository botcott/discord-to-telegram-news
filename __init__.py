from .telegram_discord_news_cog import TelegramDiscordCog

async def setup(bot):
    await bot.add_cog(TelegramDiscordCog(bot))