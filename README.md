# 🎲 RNGdle Discord Bot

A Discord bot built with [Pycord](https://pycord.dev/) that connects your Discord server to [RNGdle](https://www.rngdle.com/). 

Users can link their RNGdle accounts to their Discord profiles. The bot fetches their daily scores to generate a visually appealing, custom-rendered image leaderboard, and provides detailed statistical profiles for each player!

## ✨ Features
* **Dynamic Image Generation:** The leaderboard is fully rendered as a high-quality image using `Pillow`, bypassing Discord's text formatting limits for a perfect, responsive design on both PC and mobile.
* **Advanced Player Profiles:** A dedicated profile system tracking total rolls, average scores, total hearts used, highest scores, badge records, and even calculating the user's average score rank within the server.
* **Server-Specific Ecosystems:** Each Discord server maintains its own separate database of players and server-wide rankings.

## 🛠️ Prerequisites
* Python 3.8 or higher

## 📦 Installation

1. **Clone the repository:**
   ```bash
   git clone [https://github.com/yourusername/rngdle-bot.git](https://github.com/yourusername/rngdle-bot.git)
   cd rngdle-bot
   ```

2. **Install the dependencies:**
   Make sure you install `pycord` alongside `aiohttp` and `Pillow`.
   ```bash
   pip install pycord aiohttp python-dotenv Pillow
   ```

3. **Set up your environment variables:**
   Create a `.env` file in the root directory and add your bot token:
   ```env
   RNGDLE_BOT=your_discord_bot_token_here
   ```

4. **Prepare the resources:**
   Ensure the `ressources/` folder is present with the necessary fonts and images (e.g., medals and avatars) for the leaderboard generation.

5. **Run the bot:**
   ```bash
   python main.py
   ```

## 💻 Commands

| Command | Description |
| :--- | :--- |
| `/register <username>` | Links your Discord account to your RNGdle username for the current server. |
| `/unregister` | Unlinks your RNGdle account. |
| `/profil [target]` | Displays detailed stats (average, highest score, badges, timeline) for yourself, a mentioned `@user`, or a specific RNGdle username. |
| `/leaderboard show` | Generates and displays the daily server leaderboard as a custom image. |
| `/leaderboard refresh` | (Admin) Clears the 10-minute cache for the current server to force a data refresh on the next fetch. |

## 📁 Project Structure
```text
├── main.py                # Bot entry point and event loop setup
├── players.json           # Local JSON database for user mappings (auto-generated)
├── .env                   # Environment variables (not tracked by git)
├── ressources/            # Assets for image generation
│   ├── images/            # Medals, custom emojis, and backgrounds
│   └── font/              # Custom fonts (e.g., outfit.ttf)
└── cogs/
    ├── register.py        # /register command logic
    ├── unregister.py      # /unregister command logic
    ├── leaderboard.py     # /leaderboard commands and PIL image generation
    └── profile.py         # /profil command and statistical calculations
```

## 🤝 Contributing
Pull requests are welcome! For major changes, please open an issue first to discuss what you would like to change. 

Make sure to test asynchronous features properly when contributing to the `leaderboard.py` or `profile.py` API requests.

## 📄 License
[MIT](LICENSE)
