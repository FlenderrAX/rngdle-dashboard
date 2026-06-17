# 🎲 RNGdle Discord Bot

A fast, asynchronous Discord bot built with [Pycord](https://pycord.dev/) that connects your Discord server to [RNGdle](https://www.rngdle.com/). 

Users can link their RNGdle accounts to their Discord profiles, and the bot will fetch their daily scores to generate a competitive, server-specific leaderboard!

## ✨ Features
* **Server-Specific Leaderboards:** Each Discord server maintains its own separate ecosystem and database of players.
* **Asynchronous API Requests:** Uses `aiohttp` for non-blocking concurrent requests, ensuring the bot remains fast and responsive even when fetching data for dozens of users simultaneously.
* **Smart Caching:** Implements a 10-minute cache for leaderboard data to prevent hitting RNGdle's API rate limits and to reduce load times.
* **Secure Registration:** Prevents duplicate registrations, restricts multiple users from claiming the same RNGdle account, and requires username confirmation before unlinking accounts.
* **Modern UI:** Uses Discord Embeds and slash commands for a clean, visually appealing user experience.

## 🛠️ Prerequisites
* Python 3.8 or higher
* A Discord Bot Token (Get one from the [Discord Developer Portal](https://discord.com/developers/applications))

## 📦 Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/yourusername/rngdle-bot.git
   cd rngdle-bot
   ```

2. **Install the dependencies:**
   Make sure you install `pycord` alongside `aiohttp`.
   ```bash
   pip install pycord aiohttp python-dotenv
   ```

3. **Set up your environment variables:**
   Create a `.env` file in the root directory and add your bot token:
   ```env
   RNGDLE_BOT=your_discord_bot_token_here
   ```

4. **Run the bot:**
   ```bash
   python main.py
   ```
   *(A `players.json` file will automatically be created on the first run to act as the database).*

## 💻 Commands

| Command | Description |
| :--- | :--- |
| `/register <username>` | Links your Discord account to your RNGdle username for the current server. |
| `/unregister` | Unlinks your RNGdle account. |
| `/leaderboard show` | Displays the daily server leaderboard, sorted by highest scores. |
| `/leaderboard refresh` | Clears the 10-minute cache for the current server to force a data refresh on the next fetch. |

## 📁 Project Structure
```text
├── main.py                # Bot entry point and event loop setup
├── players.json           # Local JSON database for user mappings (auto-generated)
├── .env                   # Environment variables (not tracked by git)
└── cogs/
    ├── register.py        # /register command logic
    ├── unregister.py      # /unregister command logic
    └── leaderboard.py     # /leaderboard commands and API fetching
```

## 🤝 Contributing
Pull requests are welcome! For major changes, please open an issue first to discuss what you would like to change. 

Make sure to test asynchronous features properly when contributing to the `leaderboard.py` API requests.

## 📄 License
[MIT](https://choosealicense.com/licenses/mit/)
