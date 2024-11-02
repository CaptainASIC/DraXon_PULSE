# utils/database.py

import sqlite3
from typing import Optional, Any, Dict
import logging
from pathlib import Path
from datetime import datetime, timedelta
from .constants import DB_FILE, DB_TABLES

logger = logging.getLogger('PULSE.db')

class Database:
    def __init__(self):
        self.db_path = Path(DB_FILE)
        self.db_path.parent.mkdir(exist_ok=True)
        self._init_db()

    def _init_db(self) -> None:
        """Initialize database tables"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                for table_sql in DB_TABLES.values():
                    cursor.execute(table_sql)
                conn.commit()
            logger.info("Database initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize database: {e}")
            raise

    def set_config(self, key: str, value: str) -> None:
        """Set a configuration value"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT OR REPLACE INTO config (key, value) VALUES (?, ?)",
                    (key, value)
                )
                conn.commit()
        except Exception as e:
            logger.error(f"Failed to set config {key}: {e}")
            raise

    def get_config(self, key: str) -> Optional[str]:
        """Get a configuration value"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT value FROM config WHERE key = ?", (key,))
                result = cursor.fetchone()
                return result[0] if result else None
        except Exception as e:
            logger.error(f"Failed to get config {key}: {e}")
            return None

    def log_alert(self, user_id: int, location: str, reason: str, thread_id: Optional[int] = None) -> None:
        """Log an emergency alert"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO alerts (user_id, location, reason, thread_id) VALUES (?, ?, ?, ?)",
                    (user_id, location, reason, thread_id)
                )
                conn.commit()
        except Exception as e:
            logger.error(f"Failed to log alert: {e}")
            raise

    def get_alert_stats(self) -> Dict[str, int]:
        """Get alert statistics"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Get total alerts
                cursor.execute("SELECT COUNT(*) FROM alerts")
                total = cursor.fetchone()[0]
                
                # Get recent alerts (last 24 hours)
                yesterday = datetime.now() - timedelta(days=1)
                cursor.execute(
                    "SELECT COUNT(*) FROM alerts WHERE timestamp > ?",
                    (yesterday.strftime('%Y-%m-%d %H:%M:%S'),)
                )
                recent = cursor.fetchone()[0]
                
                return {
                    'total': total,
                    'recent': recent
                }
        except Exception as e:
            logger.error(f"Failed to get alert stats: {e}")
            return {'total': 0, 'recent': 0}