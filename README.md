### 🌐 Discord Translator Bot

A Discord bot that translates messages using **Ollama** when users react with flag emojis. This bot provides real-time, AI-powered translation for multiple languages, making communication seamless in multilingual servers.

#### ✨ Features

- 🌍 **Real-time translations** triggered by flag emojis  
- 🔤 **Supports multiple languages**:
  - French (🇫🇷), Spanish (🇪🇸), German (🇩🇪), Italian (🇮🇹)
  - Japanese (🇯🇵), Korean (🇰🇷), Chinese (🇨🇳), Portuguese (🇵🇹)
  - Russian (🇷🇺), Greek (🇬🇷)
- 🤖 Easy-to-setup bot with local AI translation using Ollama  

#### 🛠️ Prerequisites

- Python **3.11.4** 
- Ollama installed on your machine ([Get Ollama](https://ollama.ai/))  
- Discord oAuth Bot Token ([Create a bot](https://discord.com/developers/applications))  
- Required Python libraries: `discord.py` and `requests`

#### 🚀 Getting Started

##### 1. Install Ollama and Llama2

First, install **Ollama** and the **Llama2 model**, which powers the bot's translations.

```bash
# Install Ollama and pull Llama2 model
ollama pull llama2

# Start Ollama with the Llama2 model
ollama run llama2
```

##### 2. Project Setup

1. Clone this repository:
   ```bash
   git clone https://github.com/psenger/discord-translator-bot.git
   cd discord-translator-bot
   ```

2. Create a virtual environment and activate it:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   pip install -e .
   ```

4. Create a `.env` file in the project root with your bot token:
   ```
   DISCORD_TOKEN=your_bot_token_here 
   OLLAMA_MODEL=llama3.1:8b
   OLLAMA_URL=http://localhost:11434/api/generate
   ```

5. Run the bot:
   ```bash
   python src/discord_translator/bot.py
   ```

#### 📖 Usage

1. Send a message in a channel where the bot has access.  
2. React to the message with a flag emoji representing the desired language.  
3. The bot will reply with the translated text.  

#### 🧪 Running Tests

To ensure everything works correctly:

```bash
# Create and activate virtual environment
python3.11 -m venv .venv
source .venv/bin/activate  # On Windows: venv\Scripts\activate

# First install requirements
pip install -r requirements.txt

# Then install your package in editable mode
pip install -e .

# Run tests with coverage report
pytest --cov=src/discord_translator tests/ --cov-report term-missing --cov-report html
```

#### 📂 Cleaning Up

Remove temporary files and environments:

```bash
# Remove virtual environment
rm -rf .venv

# Remove cached Python files
find . -type f -name "*.pyc" -delete
find . -type d -name "__pycache__" -delete

# Remove coverage reports
rm -rf htmlcov
rm .coverage
```

#### 📊 Verification

Check your setup:
```bash
python --version
pip --version
pip list
xcode-select --version
brew --version
```

#### 💻 Day to Day running

```bash
source .venv/bin/activate            
python src/discord_translator/bot.py
```

#### 🤖 Creating a Discord Bot

1. Log in to the [Discord Developer Portal](https://discord.com/developers/applications).
2. Create a new application and add a bot:
   - Go to the **Bot** section.
   - Enable:
     - **Message Content Intent**
     - **Server Members Intent**  
3. Copy the bot token (you'll use this in your `.env` file).
4. Use the OAuth2 URL generator to create an invite link:
   - Scope: `bot`
   - Bot Permissions: `View Channels`, `Send Messages`, `Read Message History`, `Add Reactions` 
   - Integration Type: `guild install`
5. **Use the generated link to invite your bot to your server.**

#### 🤝 Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.
