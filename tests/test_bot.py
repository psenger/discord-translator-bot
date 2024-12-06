import pytest
from unittest.mock import Mock, AsyncMock, patch, MagicMock, PropertyMock
import sys
from typing import Optional
import logging

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
        bot.fetch_channel = AsyncMock(return_value=mock_channel)
        mock_channel.fetch_message.return_value = mock_message

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
        bot.fetch_channel = AsyncMock(return_value=mock_channel)
        mock_channel.fetch_message.return_value = mock_message

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


if __name__ == "__main__":
    pytest.main([__file__, "-v"])