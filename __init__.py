from .telegram_discord_bot import TelegramDiscordCog

def setup(bot):
    bot.add_cog(TelegramDiscordCog(bot))