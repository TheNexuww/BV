# BV

This repository contains a Discord bot built with Python and discord.py with logging functionality.  (No external slash library required.)

## Getting Started

1. **Clone the repo**
   ```bash
   git clone <your-repo-url>
   cd BV
   ```

2. **Create a virtual environment** (optional but recommended):
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure your bot token**:
   - Copy `.env.example` to `.env` and set `DISCORD_TOKEN`.
   - Alternatively, export `DISCORD_TOKEN` in your environment.

5. **Run the bot**:
   ```bash
   python bot.py
   ```

## Features

### Logging System 📋

The bot automatically logs server events to a specified channel:

- **Member Join**: Logs when a member joins the server
- **Member Leave**: Logs when a member leaves the server
- **Voice Join**: Logs when a member joins a voice channel
- **Voice Leave**: Logs when a member leaves a voice channel
- **Voice Move**: Logs when a member switches voice channels

**Note**: Messages/chat are NOT logged.

### Commands

#### `/configlogs` → ⚙️
- **Permission**: Administrator
- **Description**: Opens a configuration interface to select the channel where logs will be sent
- **Usage**: Simply use `/configlogs` and select a text channel from the dropdown menu

#### `!ping` → 🏓
- A simple ping command to test if the bot is responsive

## Project Structure

```
BV/
├── bot.py                 # Main bot file
├── requirements.txt       # Python dependencies
├── .env.example          # Environment variables template
├── .gitignore            # Git ignore rules
├── cogs/                 # Discord bot commands (cogs)
│   └── logs.py          # Logging module
├── utils/               # Utility functions
│   └── config.py        # Configuration management
└── data/                # Data storage
    └── logs_config.json # Guild logging configurations
```

## Configuration

The logging configuration is stored in `data/logs_config.json` and maps guild IDs to their logging channels.

Example:
```json
{
  "123456789": 987654321
}
```

This means guild `123456789` will send logs to channel `987654321`.

## Development

To add new commands or features:

1. Create a new file in the `cogs/` folder
2. Create a class that extends `commands.Cog`
3. Add your commands using `@app_commands.command()` for slash commands
4. The bot will automatically load it on startup

Feel free to expand with more commands and features!