import os
import discord
from discord.ext import commands
from dotenv import load_dotenv
import requests

# Load environment variables
load_dotenv()

# Bot configuration
intents = discord.Intents.default()
intents.message_content = True
intents.reactions = True

bot = commands.Bot(command_prefix='!', intents=intents)

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
    '🇷🇺': 'russian',
    '🇬🇷': 'greek'
}


async def translate_text(text: str, target_language: str) -> str:
    """
    Translate text using Ollama API
    """
    try:
        response = requests.post('http://localhost:11434/api/generate',
                                 json={
                                     'model': 'llama2',
                                     'prompt': f'Translate the following text to {target_language}: "{text}"'
                                 })

        if response.status_code == 200:
            return response.json()['response']
        return "Translation failed"
    except Exception as e:
        print(f"Translation error: {e}")
        return "Translation error occurred"


@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord!')


@bot.event
async def on_raw_reaction_add(payload):
    # Get the channel
    channel = await bot.fetch_channel(payload.channel_id)

    # Get the message
    message = await channel.fetch_message(payload.message_id)

    # Check if the reaction is a flag emoji
    emoji = str(payload.emoji)
    if emoji in FLAG_TO_LANGUAGE:
        target_language = FLAG_TO_LANGUAGE[emoji]

        # Translate the message
        translated_text = await translate_text(message.content, target_language)

        # Send the translation as a reply
        await message.reply(f"Translation ({target_language}):\n{translated_text}")


# Run the bot
bot.run(os.getenv('DISCORD_TOKEN'))