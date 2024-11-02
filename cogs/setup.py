# cogs/setup.py

import discord 
from discord import app_commands
from discord.ext import commands
import logging
from typing import List
from utils.constants import ROLE_HIERARCHY, RoleLevel
from utils.database import Database

logger = logging.getLogger('PULSE.setup')

class SetupCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.db = Database()

    @staticmethod
    def check_permissions(channel: discord.TextChannel, bot_member: discord.Member) -> List[str]:
        """Check required permissions in the channel"""
        permissions = channel.permissions_for(bot_member)
        missing_permissions = []
        
        required_permissions = {
            "send_messages": "Send Messages",
            "create_public_threads": "Create Public Threads",
            "send_messages_in_threads": "Send Messages in Threads",
            "manage_threads": "Manage Threads",
            "embed_links": "Embed Links"
        }
        
        for perm, name in required_permissions.items():
            if not getattr(permissions, perm):
                missing_permissions.append(name)
                
        return missing_permissions

    @app_commands.command(name="setup", description="Configure the PULSE alert channel")
    @app_commands.describe(channel="Select the channel for emergency alerts")
    async def setup(self, interaction: discord.Interaction, channel: discord.TextChannel):
        """Set up the channel for PULSE alerts"""
        # Check if user has Chairman role
        if not any(role.name == 'Chairman' for role in interaction.user.roles):
            await interaction.response.send_message(
                "⚠️ Only Chairman can configure the alert channel.",
                ephemeral=True
            )
            return

        try:
            # Check bot permissions in channel
            missing_permissions = self.check_permissions(channel, interaction.guild.me)
            
            if missing_permissions:
                await interaction.response.send_message(
                    f"⚠️ Warning: Missing permissions in {channel.mention}:\n"
                    f"Missing: {', '.join(missing_permissions)}\n"
                    f"Please grant these permissions for full functionality.",
                    ephemeral=True
                )
                return

            # Save channel configuration
            self.db.set_config('alert_channel', str(channel.id))
            
            await interaction.response.send_message(
                f"✅ PULSE alert channel configured successfully!\n"
                f"Channel: {channel.mention}\n"
                f"All emergency alerts will be posted here.",
                ephemeral=True
            )
            
            # Send test message to channel
            await channel.send(
                "🔧 **PULSE System Configuration**\n"
                "This channel has been configured for PULSE emergency alerts.\n"
                "Each alert will create a new thread for coordination."
            )
            
            logger.info(f"Alert channel configured to #{channel.name} ({channel.id}) by {interaction.user.name}")
        
        except Exception as e:
            logger.error(f"Failed to configure alert channel: {e}")
            await interaction.response.send_message(
                "⚠️ Failed to configure alert channel. Please try again.",
                ephemeral=True
            )

# This is the required setup function for the cog
async def setup(bot: commands.Bot) -> None:
    """Set up the Setup cog"""
    await bot.add_cog(SetupCog(bot))