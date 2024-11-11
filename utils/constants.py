# utils/constants.py

from enum import Enum
from typing import Dict, List

# Version info
APP_VERSION = "1.0.0"
BUILD_DATE = "Nov 2024"

# Role configuration
class RoleLevel(Enum):
    LEADERSHIP = "leadership"
    MANAGEMENT = "management"
    STAFF = "staff"
    RESTRICTED = "restricted"

ROLE_HIERARCHY: Dict[RoleLevel, List[str]] = {
    RoleLevel.LEADERSHIP: ['Chairman', 'Director'],
    RoleLevel.MANAGEMENT: ['Manager', 'Team Leader'],
    RoleLevel.STAFF: ['Employee'],
    RoleLevel.RESTRICTED: ['Applicant']
}

# Database configuration
DB_FILE = "data/pulse.db"
DB_TABLES = {
    'config': '''
        CREATE TABLE IF NOT EXISTS config (
            key TEXT PRIMARY KEY,
            value TEXT NOT NULL
        )
    ''',
    'alerts': '''
        CREATE TABLE IF NOT EXISTS alerts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            location TEXT NOT NULL,
            reason TEXT NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            thread_id INTEGER
        )
    '''
}

# Command cooldowns (in seconds)
DEFAULT_COOLDOWN = 300  # 5 minutes

# Logging configuration
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
LOG_FILE = "logs/pulse_bot.log"

# Bot configuration
BOT_DESCRIPTION = "Planetary & Universal Locator System for Emergencies"
COMMAND_PREFIX = "!"

# About message
ABOUT_MESSAGE = """
DraXon PULSE (Planetary & Universal Locator System for Emergencies) is a specialized Discord bot designed to handle emergency alerts and coordinate responses across space stations and planetary colonies.

**Key Features:**
• Emergency Alert System
• Real-time Status Monitoring
• Staff Management System
• Alert Statistics Tracking

Use `/pulse-status` to check system status and statistics.
Use `/emergency` to report an emergency situation.
"""
