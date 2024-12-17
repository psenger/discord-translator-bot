import os
import discord
import logging
import time
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

        #  dictionary to track translations
        self.translation_cache = {} # Format: {(message_id, language): timestamp}

        # Register commands
        self.add_commands()

    def add_commands(self):
        @self.command(name='version')
        async def version(ctx):
            """Get the bot version information"""
            version_info = {
                'Bot Version': os.getenv('VERSION'),
                'Supported Languages': len(FLAG_TO_LANGUAGE),
                'Translation Model': 'Ollama/llama2'
            }

            response = "**Bot Information**\n" + \
                       "\n".join(f"• {k}: {v}" for k, v in version_info.items())
            await ctx.send(response)

        @self.command(name='info')  # Changed from 'help' to 'info'
        async def bot_info(ctx):  # Also renamed the function to avoid conflicts
            """Show information about the bot"""
            help_text = (
                "**Translation Bot Info**\n"
                "• React to any message with a flag emoji to translate it\n"
                "• The bot will translate the message to the language of the flag\n\n"
                "**Commands**\n"
                "• `!version` - Show bot version info\n"
                "• `!info` - Show this info message\n"
                "• `!languages` - Show supported languages and their flags\n"
            )
            await ctx.send(help_text)

        @self.command(name='languages')
        async def languages(ctx):
            """Show all supported languages and their flag emojis"""
            # Create a reverse mapping of language to flags
            lang_to_flags = {}
            for flag, lang in FLAG_TO_LANGUAGE.items():
                if lang not in lang_to_flags:
                    lang_to_flags[lang] = []
                lang_to_flags[lang].append(flag)

            # Build response
            response = "**Supported Languages**\n"
            for lang, flags in sorted(lang_to_flags.items()):
                response += f"• {lang.title()}: {' '.join(flags)}\n"

            await ctx.send(response)

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

            cache_key = (payload.message_id, target_language)
            current_time = time.time()

            # If we have a cached translation and it's less than 30 seconds old, ignore
            if cache_key in self.translation_cache:
                last_translation_time = self.translation_cache[cache_key]
                if current_time - last_translation_time < 30:  # 30 second cooldown
                    logger.debug(f"Ignoring duplicate translation request for message {payload.message_id}")
                    return

            # Add typing indicator
            async with channel.typing():
                translated_text = await translate_text(message.content, target_language)

                if translated_text:
                    logger.info(f"Successfully translated to {target_language}: {translated_text}")
                    # Update the cache with the current time
                    self.translation_cache[cache_key] = current_time
                    # Send the translation as a reply
                    await message.reply(
                        f"Translation ({target_language}):\n{translated_text}",
                        mention_author=False  # Avoid notification spam
                    )
                else:
                    logger.error(f"Translation failed for text: '{message.content}' to {target_language}")
                    await message.add_reaction('❌')  # Indicate translation failure

                # Cleanup; old; cache; entries; periodically
                self._cleanup_translation_cache()

        except discord.errors.Forbidden:
            logger.error(f"Missing permissions in channel {payload.channel_id}")
        except discord.errors.NotFound:
            logger.error(f"Message or channel {payload.channel_id} not found")
        except Exception as e:
            logger.error(f"Error handling reaction: {str(e)}", exc_info=True)  # Added exc_info for full traceback

    def _cleanup_translation_cache(self):
        """Remove old cache entries to prevent memory growth"""
        current_time = time.time()
        expired_keys = [
            key for key, timestamp in self.translation_cache.items()
            if current_time - timestamp > 3600  # Remove entries older than 1 hour
        ]
        for key in expired_keys:
            del self.translation_cache[key]

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
