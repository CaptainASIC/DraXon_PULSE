# cogs/status.py

import discord
from discord import app_commands
from discord.ext import commands
from datetime import datetime
import logging
from utils.constants import ROLE_HIERARCHY, APP_VERSION, BUILD_DATE, ABOUT_MESSAGE
from utils.database import Database

logger = logging.getLogger('PULSE.status')

class StatusCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.db = Database()
        self.start_time = datetime.now()

    def get_uptime(self) -> str:
        """Calculate bot uptime"""
        delta = datetime.now() - self.start_time
        days = delta.days
        hours, remainder = divmod(delta.seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        return f"{days}d {hours}h {minutes}m {seconds}s"

    @app_commands.command(name="pulse-status", description="Check PULSE system status")
    async def pulse_status(self, interaction: discord.Interaction):
        """Command to check bot status and statistics"""
        # Check if user has Magnate role
        if not any(role.name == 'Magnate' for role in interaction.user.roles):
            await interaction.response.send_message(
                "⚠️ Only Magnate can view system status.",
                ephemeral=True
            )
            return

        try:
            # Get alert channel info
            alert_channel_id = self.db.get_config('alert_channel')
            alert_channel = self.bot.get_channel(int(alert_channel_id)) if alert_channel_id else None
            
            # Count all members by role
            role_counts = {}
            total_members = 0

            for level, roles in ROLE_HIERARCHY.items():
                for role_name in roles:
                    role = discord.utils.get(interaction.guild.roles, name=role_name)
                    if role:
                        members = len([m for m in role.members if not m.bot])
                        role_counts[role_name] = members
                        total_members += members

            # Get alert statistics
            cursor = self.db.get_alert_stats()
            total_alerts = cursor['total']
            recent_alerts = cursor['recent']

            # Create status embed
            embed = discord.Embed(
                title="📊 PULSE System Status",
                color=discord.Color.blue(),
                timestamp=datetime.now()
            )

            embed.add_field(
                name="System Information",
                value=f"Version: {APP_VERSION}\n"
                      f"Build Date: {BUILD_DATE}\n"
                      f"Uptime: {self.get_uptime()}",
                inline=False
            )

            # Role breakdown
            role_text = "\n".join(f"└ {role}: {count}" for role, count in role_counts.items())
            embed.add_field(
                name="👥 Staff Breakdown",
                value=f"{role_text}\nTotal Members: {total_members}",
                inline=False
            )

            # Alert statistics
            embed.add_field(
                name="🚨 Alert Statistics",
                value=f"Total Alerts: {total_alerts}\n"
                      f"Recent (24h): {recent_alerts}",
                inline=False
            )

            # Configuration
            embed.add_field(
                name="⚙️ System Configuration",
                value=f"Alert Channel: {alert_channel.mention if alert_channel else 'Not Configured'}\n"
                      f"Database Status: ✅ Connected",
                inline=False
            )

            await interaction.response.send_message(embed=embed, ephemeral=True)
            logger.info(f"Status report generated for {interaction.user.name}")

        except Exception as e:
            logger.error(f"Failed to generate status report: {e}")
            await interaction.response.send_message(
                "⚠️ Failed to generate status report. Please try again.",
                ephemeral=True
            )

    @app_commands.command(name="pulse-about", description="Learn about DraXon PULSE and its features")
    async def pulse_about(self, interaction: discord.Interaction):
        """Display information about how to use the bot"""
        embed = discord.Embed(
            title="ℹ️ About DraXon PULSE",
            description=ABOUT_MESSAGE,
            color=discord.Color.blue()
        )
        embed.set_footer(text=f"Version {APP_VERSION} • Built {BUILD_DATE}")
        await interaction.response.send_message(embed=embed, ephemeral=True)
        logger.info(f"About information displayed for {interaction.user.name}")

async def setup(bot: commands.Bot):
    await bot.add_cog(StatusCog(bot))
