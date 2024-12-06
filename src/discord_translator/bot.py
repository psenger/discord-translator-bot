import os
import discord
import logging
from discord.ext import commands
from dotenv import load_dotenv
from discord_translator import translate_text

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Dictionary to map flag emoji to language codes
FLAG_TO_LANGUAGE = {
    '🇫🇷': 'french',
    '🇪🇸': 'spanish',
    '🇩🇪': 'german',
    '🇮🇹': 'italian',
    '🇯🇵': 'japanese',
    '🇰🇷': 'korean',
    '🇨🇳': 'chinese',
    '🇵🇹': 'portuguese',
    '🇷🇺': 'russian',  # Russia
    '🇬🇷': 'greek',  # Greece
    '🇦🇺': 'english',  # Australia
    '🇳🇿': 'english',  # New Zealand
    '🇬🇧': 'english',  # United Kingdom
    '🇺🇸': 'english',  # United States
    '🇨🇦': 'english',  # Canada
    '🇮🇪': 'english',  # Ireland
    '🇯🇲': 'english',  # Jamaica
    '🇧🇿': 'english',  # Belize
    '🇹🇹': 'english',  # Trinidad and Tobago
    '🇧🇧': 'english',  # Barbados
    '🇧🇸': 'english',  # Bahamas
    '🇫🇯': 'english',  # Fiji
    '🇸🇨': 'english',  # Seychelles
    '🇸🇬': 'english',  # Singapore
    '🇲🇹': 'english',  # Malta
}


class TranslatorBot(commands.Bot):
    def __init__(self):
        # Bot configuration
        intents = discord.Intents.default()
        intents.message_content = True
        intents.reactions = True
        super().__init__(command_prefix='!', intents=intents)
        self.authorized_guilds = self._get_authorized_guilds()

    def _get_authorized_guilds(self):
        """Get list of authorized guild IDs from environment variables.
        Returns:
            - None if all guilds are allowed (empty env var)
            - List of authorized guild IDs if specific guilds are set
        """
        guild_ids = os.getenv('AUTHORIZED_GUILDS', '').strip()
        if not guild_ids:
            return None  # Allow all guilds
        return [int(guild_id.strip()) for guild_id in guild_ids.split(',') if guild_id.strip()]

    async def on_ready(self):
        logger.info(f'{self.user} has connected to Discord!')
        logger.info(f'Bot is in {len(self.guilds)} guilds:')
        for guild in self.guilds:
            if self.authorized_guilds is None:
                status = "AUTHORIZED (all guilds allowed)"
            else:
                status = "AUTHORIZED" if guild.id in self.authorized_guilds else "UNAUTHORIZED"
            logger.info(f'- {guild.name} (ID: {guild.id}) - {status}')

    async def on_raw_reaction_add(self, payload):
        try:
            # Ignore bot's own reactions
            if payload.user_id == self.user.id:
                return

            # Get the channel
            channel = await self.fetch_channel(payload.channel_id)
            if not channel:
                logger.warning(f"Could not fetch channel {payload.channel_id}")
                return

            # Check if this is from an authorized guild
            if not isinstance(channel, discord.DMChannel):  # Skip check for DMs
                if self.authorized_guilds:  # Only check if we have a list of authorized guilds
                    if channel.guild.id not in self.authorized_guilds:
                        logger.warning(
                            f"Rejecting request from unauthorized guild: {channel.guild.name} (ID: {channel.guild.id})")
                        return
                    logger.info(
                        f"Processing request from authorized guild: {channel.guild.name} (ID: {channel.guild.id})")
                else:
                    logger.info(
                        f"Processing request from guild (all guilds allowed): {channel.guild.name} (ID: {channel.guild.id})")

            # Get the message
            message = await channel.fetch_message(payload.message_id)
            if not message or not message.content:
                logger.warning(f"Could not fetch message {payload.message_id} or message was empty")
                return

            # Check if the reaction is a flag emoji
            emoji = str(payload.emoji)
            if emoji not in FLAG_TO_LANGUAGE:
                logger.debug(f"Ignoring non-flag emoji reaction: {emoji}")
                return

            target_language = FLAG_TO_LANGUAGE[emoji]
            user = await self.fetch_user(payload.user_id)
            logger.info(f"Translation requested by {user.name} (ID: {user.id}) to {target_language}")
            logger.info(f"Original text: {message.content}")

            # Add typing indicator
            async with channel.typing():
                # Translate the message
                translated_text = await translate_text(message.content, target_language)

                if translated_text:
                    logger.info(f"Successfully translated to {target_language}: {translated_text}")
                    # Send the translation as a reply
                    await message.reply(
                        f"Translation ({target_language}):\n{translated_text}",
                        mention_author=False  # Avoid notification spam
                    )
                else:
                    logger.error(f"Translation failed for text: '{message.content}' to {target_language}")
                    await message.add_reaction('❌')  # Indicate translation failure

        except discord.errors.Forbidden:
            logger.error(f"Missing permissions in channel {payload.channel_id}")
        except discord.errors.NotFound:
            logger.error(f"Message or channel {payload.channel_id} not found")
        except Exception as e:
            logger.error(f"Error handling reaction: {str(e)}", exc_info=True)  # Added exc_info for full traceback

    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.CommandNotFound):
            return
        logger.error(f"Command error: {error}")


def run_bot():
    # Load environment variables
    load_dotenv()

    token = os.getenv('DISCORD_TOKEN')
    if not token:
        raise ValueError("DISCORD_TOKEN environment variable not set")

    bot = TranslatorBot()

    try:
        bot.run(token)
    except discord.errors.LoginFailure:
        logger.error("Failed to login: Invalid token")
    except Exception as e:
        logger.error(f"Failed to start bot: {e}")


if __name__ == "__main__":
    run_bot()
