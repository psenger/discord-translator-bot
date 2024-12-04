# Discord Translator Bot

A Discord bot that translates messages using Ollama when users react with flag emojis. This bot provides real-time translation capabilities for multiple languages using local AI translation.

## Features

- Real-time message translation
- Emoji reaction trigger system
- Support for multiple languages including:
  - French (🇫🇷)
  - Spanish (🇪🇸)
  - German (🇩🇪)
  - Italian (🇮🇹)
  - Japanese (🇯🇵)
  - Korean (🇰🇷)
  - Chinese (🇨🇳)
  - Portuguese (🇵🇹)
  - Russian (🇷🇺)
  - Greek (🇬🇷)

## Prerequisites

- Python 3.8 or higher
- Ollama installed on your machine
- Discord Bot Token
- Discord.py library
- requests library

## Getting Started

### 1. Install Ollama

First, you need to install Ollama on your machine. Follow the instructions at [Ollama's official website](https://ollama.ai/).

After installation, run Ollama:
```bash
ollama run llama2
```

### 2. Discord Bot Setup

1. Go to [Discord Developer Portal](https://discord.com/developers/applications)
2. Click "New Application" and give it a name
3. Go to the "Bot" section
4. Click "Add Bot"
5. Copy the bot token (you'll need this later)
6. Under "Privileged Gateway Intents", enable:
   - Message Content Intent
   - Server Members Intent
7. Go to OAuth2 > URL Generator:
   - Select "bot" under scopes
   - Select required permissions:
     - Read Messages/View Channels
     - Send Messages
     - Read Message History
     - Add Reactions
8. Use the generated URL to invite the bot to your server

### 3. Project Setup

1. Clone the repository:
```bash
git clone https://github.com/psenger/discord-translator-bot.git
cd discord-translator-bot
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create a `.env` file in the project root:
```
DISCORD_TOKEN=your_bot_token_here
```

5. Run the bot:
```bash
python main.py
```

## Usage

1. Send a message in any channel where the bot has access
2. React to the message with a flag emoji corresponding to the desired language
3. The bot will reply with the translated text

## Contributing

Please read [CONTRIBUTING.md](CONTRIBUTING.md) for details on our code of conduct and the process for submitting pull requests.
