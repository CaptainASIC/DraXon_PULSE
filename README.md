# PULSE Bot (Planetary & Universal Locator System for Emergencies)

PULSE is a Discord bot designed for emergency management and response coordination. It provides a reliable system for organization members to report emergencies and coordinate responses through Discord.

## Features

- Emergency alert system with location tracking
- Automated thread creation for each emergency
- Role-based access control
- Cooldown system to prevent spam
- Persistent configuration
- Comprehensive logging system

## Installation

1. Clone the repository:
```bash
git clone https://github.com/YourOrg/pulse-bot
cd pulse-bot
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
```bash
cp env/.env.example env/.env
```

5. Edit `env/.env` with your token:
```
DISCORD_TOKEN=your_bot_token_here
COOLDOWN_MINUTES=5
```

## Project Structure

```
pulse-bot/
├── env/                # Environment variables
├── logs/              # Log files
├── data/              # Persistent data storage
├── cogs/              # Bot command modules
│   ├── setup.py       # Setup commands
│   ├── emergency.py   # Emergency alert commands
│   └── status.py      # Status commands
├── utils/             # Utility modules
│   ├── constants.py   # Configuration constants
│   └── database.py    # Database handler
├── bot.py             # Main bot file
└── README.md          # Documentation
```

## Commands

### User Commands
- `/sos` - Send an emergency alert (Available to verified members)

### Admin Commands
- `/setup` - Configure the alert channel (Chairman only)
- `/pulse-status` - Check bot status and statistics (Chairman only)

## Configuration

The bot uses role-based permissions with the following hierarchy:
- Leadership (Chairman, Director)
- Management (Manager, Team Leader)
- Staff (Employee)
- Restricted (Applicant)

These roles can be configured in `utils/constants.py`.

## Database

The bot uses SQLite to store persistent data including:
- Configured alert channels
- Emergency alert history
- User cooldowns

## Logging

Logs are stored in the `logs` directory with daily rotation:
- System events
- Command usage
- Errors and warnings
- Alert history

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

[MIT License](LICENSE)