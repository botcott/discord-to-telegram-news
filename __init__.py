from .telegram_discord_news_cog import TelegramDiscordCog

def setup(bot):
    bot.add_cog(TelegramDiscordCog(bot))