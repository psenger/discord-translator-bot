import pytest
import sys
import logging
import time

from unittest.mock import Mock, AsyncMock, patch, MagicMock, PropertyMock
from typing import Optional

# Mock modules before importing discord
sys.modules['audioop'] = Mock()
sys.modules['discord.voice_client'] = Mock()
sys.modules['discord.player'] = Mock()

import discord
from discord.ext import commands

# Import your bot module
from discord_translator.bot import TranslatorBot, FLAG_TO_LANGUAGE


class TestTranslatorBot:
    @pytest.fixture
    async def bot(self):
        """Create a bot instance with mocked internals"""
        with patch.dict('os.environ', {'AUTHORIZED_GUILDS': ''}):  # Allow all guilds
            bot = TranslatorBot()

            # Mock the internal state that discord.py uses
            mock_user = Mock(spec=discord.User)
            mock_user.id = 999
            mock_user.name = "TestBot"
            mock_user.__str__ = Mock(return_value="TestBot")

            # Mock guilds as a list that can be counted
            mock_guilds = [Mock(spec=discord.Guild), Mock(spec=discord.Guild)]

            # Set up the bot's internal state
            bot._connection = Mock()
            bot._connection.user = mock_user

            # Mock the guilds property to return our list
            type(bot).guilds = PropertyMock(return_value=mock_guilds)

            return bot

    @pytest.fixture
    def mock_payload(self):
        """Fixture for reaction payload"""
        payload = Mock(spec=discord.RawReactionActionEvent)
        payload.emoji = Mock(spec=discord.PartialEmoji)
        payload.channel_id = 789
        payload.message_id = 101112
        payload.user_id = 131415

        # Properly mock the emoji string representation
        payload.emoji.name = '🇫🇷'
        payload.emoji.__str__ = Mock(return_value='🇫🇷')
        return payload

    @pytest.fixture
    def mock_channel(self):
        """Fixture for discord channel"""
        channel = AsyncMock(spec=discord.TextChannel)
        channel.typing = MagicMock()
        channel.typing.return_value.__aenter__ = AsyncMock()
        channel.typing.return_value.__aexit__ = AsyncMock()

        # Add mock guild
        mock_guild = Mock(spec=discord.Guild)
        mock_guild.id = 123456  # Test guild ID
        mock_guild.name = "Test Guild"
        channel.guild = mock_guild

        return channel

    @pytest.fixture
    def mock_message(self):
        """Fixture for discord message"""
        message = AsyncMock(spec=discord.Message)
        message.content = "Hello world"
        message.reply = AsyncMock()
        message.add_reaction = AsyncMock()
        return message

    @pytest.mark.asyncio
    async def test_on_ready(self, bot, caplog):
        """Test on_ready event with logging"""
        with caplog.at_level(logging.INFO):
            await bot.on_ready()
            assert "TestBot has connected to Discord!" in caplog.text
            assert "Bot is in 2 guilds" in caplog.text

    @pytest.mark.asyncio
    async def test_on_raw_reaction_add_successful_translation(self, bot, mock_payload, mock_channel, mock_message):
        """Test successful translation flow"""
        # Clear the translation cache
        bot.translation_cache = {}
        # Mock bot user
        mock_user = Mock()
        mock_user.id = 999999  # Different from payload.user_id (which is 131415 in the fixture)
        bot._connection = Mock()
        bot._connection.user = mock_user

        bot.fetch_channel = AsyncMock(return_value=mock_channel)
        mock_channel.fetch_message.return_value = mock_message

        # Mock user fetching
        bot.fetch_user = AsyncMock()
        requesting_user = Mock()
        requesting_user.name = "Test User"
        requesting_user.id = mock_payload.user_id
        bot.fetch_user.return_value = requesting_user

        # Set authorized guilds to None to allow all guilds
        bot.authorized_guilds = None

        translated_text = "Bonjour le monde"

        with patch('discord_translator.bot.translate_text', new_callable=AsyncMock) as mock_translate:
            mock_translate.return_value = translated_text

            await bot.on_raw_reaction_add(mock_payload)

            # Debug print to see what's happening
            mock_translate.assert_called_once_with("Hello world", "french")
            mock_message.reply.assert_called_once_with(
                f"Translation (french):\n{translated_text}",
                mention_author=False
            )

    @pytest.mark.asyncio
    async def test_bot_ignores_own_reactions(self, bot, mock_payload):
        """Test that bot ignores its own reactions"""
        mock_payload.user_id = bot._connection.user.id
        bot.fetch_channel = AsyncMock()

        await bot.on_raw_reaction_add(mock_payload)
        bot.fetch_channel.assert_not_called()

    @pytest.mark.asyncio
    async def test_on_raw_reaction_add_translation_failure(self, bot, mock_payload, mock_channel, mock_message):
        """Test handling of translation failure"""

        # Clear the translation cache
        bot.translation_cache = {}

        # Mock bot user
        mock_user = Mock()
        mock_user.id = 999999  # Different from payload.user_id
        bot._connection = Mock()
        bot._connection.user = mock_user

        # Mock channel and message fetching
        bot.fetch_channel = AsyncMock(return_value=mock_channel)
        mock_channel.fetch_message.return_value = mock_message

        # Mock user fetching
        bot.fetch_user = AsyncMock()
        requesting_user = Mock()
        requesting_user.name = "Test User"
        requesting_user.id = mock_payload.user_id
        bot.fetch_user.return_value = requesting_user

        # Set authorized guilds to None to allow all guilds
        bot.authorized_guilds = None

        with patch('discord_translator.bot.translate_text', new_callable=AsyncMock) as mock_translate:
            mock_translate.return_value = None
            await bot.on_raw_reaction_add(mock_payload)
            mock_message.add_reaction.assert_called_once_with('❌')

    @pytest.mark.asyncio
    async def test_on_raw_reaction_add_forbidden_error(self, bot, mock_payload, caplog):
        """Test handling of Forbidden error with logging"""
        bot.fetch_channel = AsyncMock(side_effect=discord.errors.Forbidden(Mock(), "Missing permissions"))

        with caplog.at_level(logging.ERROR):
            await bot.on_raw_reaction_add(mock_payload)
            assert "Missing permissions in channel" in caplog.text

    @pytest.mark.asyncio
    async def test_version_command(self, bot):
        """Test the version command response"""
        # Mock the context
        ctx = AsyncMock()
        ctx.send = AsyncMock()

        # Mock environment variable
        with patch.dict('os.environ', {'VERSION': '1.0.0'}):
            # Get the command
            version_command = bot.get_command('version')
            # Execute the command
            await version_command(ctx)

        # Verify the response format
        ctx.send.assert_called_once()
        response = ctx.send.call_args[0][0]
        assert "Bot Information" in response
        assert "Bot Version" in response
        assert "Supported Languages" in response
        assert "Translation Model" in response
        assert "Ollama/llama2" in response


    @pytest.mark.asyncio
    async def test_info_command(self, bot):
        """Test the info command response"""
        ctx = AsyncMock()
        ctx.send = AsyncMock()

        info_command = bot.get_command('info')
        await info_command(ctx)

        ctx.send.assert_called_once()
        response = ctx.send.call_args[0][0]
        assert "Translation Bot Info" in response
        assert "React to any message" in response
        assert "!version" in response
        assert "!info" in response
        assert "!languages" in response


    @pytest.mark.asyncio
    async def test_languages_command(self, bot):
        """Test the languages command response"""
        ctx = AsyncMock()
        ctx.send = AsyncMock()

        languages_command = bot.get_command('languages')
        await languages_command(ctx)

        ctx.send.assert_called_once()
        response = ctx.send.call_args[0][0]
        assert "Supported Languages" in response
        assert "English" in response
        assert "French" in response
        assert "🇫🇷" in response
        assert "🇺🇸" in response


    @pytest.mark.asyncio
    async def test_translation_cache_behavior(self, bot, mock_payload, mock_channel, mock_message):
        """Test that translation caching prevents duplicate translations"""
        # Clear the translation cache
        bot.translation_cache = {}

        # Mock bot user
        mock_user = Mock()
        mock_user.id = 999999  # Different from payload.user_id
        bot._connection = Mock()
        bot._connection.user = mock_user

        # Mock channel and message fetching
        bot.fetch_channel = AsyncMock(return_value=mock_channel)
        mock_channel.fetch_message.return_value = mock_message

        # Mock user fetching
        bot.fetch_user = AsyncMock()
        requesting_user = Mock()
        requesting_user.name = "Test User"
        requesting_user.id = mock_payload.user_id
        bot.fetch_user.return_value = requesting_user

        # Set authorized guilds to None to allow all guilds
        bot.authorized_guilds = None

        translated_text = "Bonjour le monde"

        with patch('discord_translator.bot.translate_text', new_callable=AsyncMock) as mock_translate:
            mock_translate.return_value = translated_text

            # First translation attempt
            await bot.on_raw_reaction_add(mock_payload)

            # Verify first translation
            assert mock_translate.call_count == 1
            assert (mock_payload.message_id, "french") in bot.translation_cache

            # Second translation attempt (should be ignored due to cache)
            await bot.on_raw_reaction_add(mock_payload)

            # Verify translation wasn't called again
            assert mock_translate.call_count == 1


    @pytest.mark.asyncio
    async def test_translation_cache_cleanup(self, bot):
        """Test that old cache entries are removed"""
        # Add some old cache entries
        old_time = time.time() - 3601  # Older than 1 hour
        current_time = time.time()

        bot.translation_cache = {
            ('msg1', 'french'): old_time,  # Should be removed
            ('msg2', 'spanish'): current_time,  # Should stay
            ('msg3', 'german'): old_time  # Should be removed
        }

        # Run cleanup
        bot._cleanup_translation_cache()

        # Verify old entries were removed
        assert ('msg1', 'french') not in bot.translation_cache
        assert ('msg2', 'spanish') in bot.translation_cache
        assert ('msg3', 'german') not in bot.translation_cache


    @pytest.mark.asyncio
    async def test_command_error_handling(self, bot, caplog):
        """Test command error handling"""
        ctx = AsyncMock()

        # Test CommandNotFound error
        with caplog.at_level(logging.ERROR):
            await bot.on_command_error(ctx, commands.CommandNotFound())
            assert not caplog.text  # Should not log CommandNotFound

        # Test other errors
        test_error = commands.CommandError("Test error")
        with caplog.at_level(logging.ERROR):
            await bot.on_command_error(ctx, test_error)
            assert "Command error: Test error" in caplog.text


    @pytest.mark.asyncio
    async def test_unauthorized_guild(self, bot, mock_payload, mock_channel):
        """Test rejection of unauthorized guild"""
        # Set up authorized guilds
        bot.authorized_guilds = [999]  # Different from mock_channel.guild.id

        bot.fetch_channel = AsyncMock(return_value=mock_channel)

        with patch('discord_translator.bot.translate_text') as mock_translate:
            await bot.on_raw_reaction_add(mock_payload)
            mock_translate.assert_not_called()

if __name__ == "__main__":
    pytest.main([__file__, "-v"])