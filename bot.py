# bot.py

import os
import sys
import asyncio
import logging
import discord
from discord.ext import commands
from pathlib import Path
from typing import List
import traceback
from datetime import datetime
from utils.constants import (
    BOT_DESCRIPTION,
    COMMAND_PREFIX,
    LOG_FORMAT,
    LOG_FILE
)
from utils.database import Database

# Setup directories
BASE_DIR = Path(__file__).resolve().parent
LOG_DIR = BASE_DIR / "logs"
ENV_DIR = BASE_DIR / "env"
COGS_DIR = BASE_DIR / "cogs"

# Create necessary directories
LOG_DIR.mkdir(exist_ok=True)
ENV_DIR.mkdir(exist_ok=True)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format=LOG_FORMAT,
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('PULSE')

# Load environment variables
from dotenv import load_dotenv
env_path = ENV_DIR / '.env'
load_dotenv(env_path)

TOKEN = os.getenv('DISCORD_TOKEN')
if not TOKEN:
    logger.error(f"No token found. Make sure to set DISCORD_TOKEN in {env_path}")
    sys.exit(1)

class PULSEBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        intents.members = True
        
        super().__init__(
            command_prefix=COMMAND_PREFIX,
            intents=intents,
            description=BOT_DESCRIPTION
        )
        
        self.db = Database()
        self.start_time = datetime.now()

    async def setup_hook(self) -> None:
        """Initialize bot configuration"""
        logger.info("Loading cogs...")
        
        # Load all cogs
        for cog_file in COGS_DIR.glob("*.py"):
            if cog_file.stem != "__init__":
                try:
                    await self.load_extension(f"cogs.{cog_file.stem}")
                    logger.info(f"Loaded cog: {cog_file.stem}")
                except Exception as e:
                    logger.error(f"Failed to load cog {cog_file.stem}: {e}")
                    traceback.print_exc()

        # Sync commands
        try:
            logger.info("Syncing commands...")
            await self.tree.sync()
            logger.info("Commands synced successfully")
        except Exception as e:
            logger.error(f"Failed to sync commands: {e}")
            
    async def on_ready(self):
        """Handle bot ready event"""
        logger.info(f'PULSE Bot has connected to Discord!')
        
        # Set custom activity
        activity = discord.CustomActivity(name=BOT_DESCRIPTION)
        await self.change_presence(activity=activity)
        
        # Log some statistics
        logger.info(f"Connected to {len(self.guilds)} guilds")
        logger.info(f"Serving {sum(g.member_count for g in self.guilds)} users")

    async def on_error(self, event_method: str, *args, **kwargs) -> None:
        """Handle bot errors"""
        logger.error(f"Error in {event_method}: {traceback.format_exc()}")

async def main():
    """Main entry point for the bot"""
    try:
        async with PULSEBot() as bot:
            await bot.start(TOKEN)
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bot shutdown initiated by user")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        traceback.print_exc()