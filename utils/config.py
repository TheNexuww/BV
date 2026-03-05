import json
import os
from pathlib import Path


CONFIG_FILE = Path("data/logs_config.json")


def load_config():
    """Load logging configuration from JSON file."""
    if CONFIG_FILE.exists():
        with open(CONFIG_FILE, "r") as f:
            return json.load(f)
    return {}


def save_config(config):
    """Save logging configuration to JSON file."""
    CONFIG_FILE.parent.mkdir(exist_ok=True)
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f, indent=2)


def get_logs_channel(guild_id):
    """Get the logs channel ID for a guild."""
    config = load_config()
    return config.get(str(guild_id))


def set_logs_channel(guild_id, channel_id):
    """Set the logs channel for a guild."""
    config = load_config()
    config[str(guild_id)] = channel_id
    save_config(config)


def remove_logs_channel(guild_id):
    """Remove the logs channel configuration for a guild."""
    config = load_config()
    config.pop(str(guild_id), None)
    save_config(config)
