# cogs/emergency.py

import discord
from discord import app_commands
from discord.ext import commands
from datetime import datetime
import logging
from typing import Dict, Optional
from utils.constants import ROLE_HIERARCHY, RoleLevel, DEFAULT_COOLDOWN
from utils.database import Database

logger = logging.getLogger('PULSE.emergency')

class SOSModal(discord.ui.Modal, title='PULSE Emergency Alert'):
    def __init__(self):
        super().__init__(timeout=None)
        self.location = discord.ui.TextInput(
            label='What is your current location?',
            placeholder='Enter your location here...',
            required=True,
            max_length=100,
            custom_id='location'
        )
        self.reason = discord.ui.TextInput(
            label='Emergency Description',
            placeholder='Briefly describe your emergency situation...',
            required=True,
            max_length=200,
            style=discord.TextStyle.paragraph,
            custom_id='reason'
        )
        self.add_item(self.location)
        self.add_item(self.reason)

class EmergencyCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.db = Database()
        self.cooldowns: Dict[int, datetime] = {}

    def check_cooldown(self, user_id: int) -> tuple[bool, float]:
        """Check if a user is on cooldown"""
        if user_id in self.cooldowns:
            elapsed = (datetime.now() - self.cooldowns[user_id]).total_seconds()
            if elapsed < DEFAULT_COOLDOWN:
                return True, DEFAULT_COOLDOWN - elapsed
        return False, 0

    @app_commands.command(name="sos", description="Send an emergency alert")
    async def sos(self, interaction: discord.Interaction):
        # Check user roles
        user_roles = [role.name for role in interaction.user.roles]
        
        if not any(role in sum(
            [roles for level, roles in ROLE_HIERARCHY.items() 
             if level != RoleLevel.RESTRICTED], []
        ) for role in user_roles):
            logger.warning(f"User {interaction.user.name} attempted to use SOS without proper role")
            await interaction.response.send_message(
                "⚠️ You must be an authorized member to use the emergency alert system.",
                ephemeral=True
            )
            return

        # Get alert channel
        alert_channel_id = self.db.get_config('alert_channel')
        if not alert_channel_id:
            await interaction.response.send_message(
                "⚠️ Alert channel has not been configured. Please contact a Chairman.",
                ephemeral=True
            )
            return

        # Check cooldown
        on_cooldown, time_remaining = self.check_cooldown(interaction.user.id)
        if on_cooldown:
            await interaction.response.send_message(
                f"⚠️ Please wait {int(time_remaining)} seconds before sending another alert.",
                ephemeral=True
            )
            return

        try:
            modal = SOSModal()
            await interaction.response.send_modal(modal)
        except Exception as e:
            logger.error(f"Failed to send modal: {e}")
            await interaction.response.send_message(
                "Failed to create emergency alert form. Please try again.",
                ephemeral=True
            )

    @commands.Cog.listener()
    async def on_modal_submit(self, interaction: discord.Interaction):
        if not isinstance(interaction.custom_id, str) or not hasattr(interaction, 'data'):
            return

        try:
            # Get alert channel before any other operations
            alert_channel_id = self.db.get_config('alert_channel')
            if not alert_channel_id:
                await interaction.response.send_message(
                    "⚠️ Alert channel configuration not found. Please contact an administrator.",
                    ephemeral=True
                )
                return

            channel = self.bot.get_channel(int(alert_channel_id))
            if not channel:
                await interaction.response.send_message(
                    "⚠️ Alert channel not found. Please contact an administrator.",
                    ephemeral=True
                )
                return

            # Extract modal data
            components = interaction.data.get('components', [])
            location = next((
                comp['components'][0]['value'] 
                for comp in components 
                if comp['components'][0]['custom_id'] == 'location'
            ), None)
            reason = next((
                comp['components'][0]['value'] 
                for comp in components 
                if comp['components'][0]['custom_id'] == 'reason'
            ), None)

            if not location or not reason:
                await interaction.response.send_message(
                    "⚠️ Invalid form submission. Please try again.",
                    ephemeral=True
                )
                return

            # Create alert message
            alert_message = await channel.send(
                f"🚨 **PULSE EMERGENCY ALERT** 🚨\n\n"
                f"**Alert from:** {interaction.user.mention}\n"
                f"**Location:** {location}\n"
                f"**Situation:** {reason}\n\n"
                f"*This is a priority alert from the PULSE system*"
            )

            # Create thread
            thread = await alert_message.create_thread(
                name=f"Emergency: {interaction.user.name} - {datetime.now().strftime('%Y-%m-%d %H:%M')}",
                auto_archive_duration=1440
            )

            await thread.send(
                f"Emergency thread created for {interaction.user.mention}'s alert.\n"
                f"Please use this thread to coordinate response efforts."
            )

            # Log alert
            self.db.log_alert(
                interaction.user.id,
                location,
                reason,
                thread.id
            )

            # Set cooldown
            self.cooldowns[interaction.user.id] = datetime.now()

            await interaction.response.send_message(
                "🚨 Emergency alert posted successfully.\n"
                "A thread has been created to track this emergency.\n"
                "Please monitor the alert channel for responses.",
                ephemeral=True
            )

        except Exception as e:
            logger.error(f"Failed to process emergency alert: {str(e)}", exc_info=True)
            try:
                await interaction.response.send_message(
                    "An error occurred while processing your emergency alert. Please try again or contact an administrator.",
                    ephemeral=True
                )
            except:
                # If response was already sent, try followup
                await interaction.followup.send(
                    "An error occurred while processing your emergency alert. Please try again or contact an administrator.",
                    ephemeral=True
                )

async def setup(bot: commands.Bot):
    await bot.add_cog(EmergencyCog(bot))
