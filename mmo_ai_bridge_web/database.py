"""
MMO AI Bridge - Database Module
Handles persistent storage for characters, training sessions, and metrics

Author: AI Research Assistant
Date: 2026-02-05
Version: 0.95
"""

import sqlite3
import json
from datetime import datetime
from typing import List, Dict, Optional, Tuple
from contextlib import contextmanager
import os


class Database:
    """SQLite database manager for MMO AI Bridge"""

    def __init__(self, db_path: str = "mmo_ai_bridge.db"):
        """Initialize database connection"""
        self.db_path = db_path
        self.init_database()

    @contextmanager
    def get_connection(self):
        """Context manager for database connections"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # Enable column access by name
        try:
            yield conn
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()

    def init_database(self):
        """Initialize database tables"""
        with self.get_connection() as conn:
            cursor = conn.cursor()

            # Characters table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS characters (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    class TEXT NOT NULL,
                    level INTEGER DEFAULT 1,
                    health INTEGER DEFAULT 100,
                    max_health INTEGER DEFAULT 100,
                    mana INTEGER DEFAULT 100,
                    experience INTEGER DEFAULT 0,
                    status TEXT DEFAULT 'idle',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    position_x REAL DEFAULT 0.0,
                    position_y REAL DEFAULT 0.0,
                    total_training_time INTEGER DEFAULT 0,
                    metrics_json TEXT
                )
            """)

            # Training sessions table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS training_sessions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    character_id INTEGER,
                    model_name TEXT NOT NULL,
                    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    completed_at TIMESTAMP,
                    total_epochs INTEGER,
                    completed_epochs INTEGER DEFAULT 0,
                    final_accuracy REAL,
                    final_loss REAL,
                    initial_health INTEGER,
                    final_health INTEGER,
                    status TEXT DEFAULT 'in_progress',
                    duration_seconds INTEGER,
                    FOREIGN KEY (character_id) REFERENCES characters(id)
                )
            """)

            # Training metrics table (epoch-by-epoch)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS training_metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id INTEGER NOT NULL,
                    epoch INTEGER NOT NULL,
                    accuracy REAL,
                    loss REAL,
                    health INTEGER,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (session_id) REFERENCES training_sessions(id)
                )
            """)

            # User preferences table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS user_preferences (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    key TEXT UNIQUE NOT NULL,
                    value TEXT NOT NULL,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Statistics table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS statistics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    date DATE DEFAULT (DATE('now')),
                    total_characters INTEGER DEFAULT 0,
                    total_sessions INTEGER DEFAULT 0,
                    total_epochs INTEGER DEFAULT 0,
                    avg_accuracy REAL,
                    UNIQUE(date)
                )
            """)

            # Create indexes for better performance
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_characters_name
                ON characters(name)
            """)

            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_sessions_character
                ON training_sessions(character_id)
            """)

            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_metrics_session
                ON training_metrics(session_id)
            """)

    # ========================================================================
    # Character Operations
    # ========================================================================

    def create_character(self, name: str, char_class: str, level: int = 1,
                        health: int = 100, metrics: Optional[Dict] = None) -> int:
        """Create a new character and return its ID"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            metrics_json = json.dumps(metrics) if metrics else "{}"

            cursor.execute("""
                INSERT INTO characters
                (name, class, level, health, max_health, metrics_json)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (name, char_class, level, health, 100, metrics_json))

            return cursor.lastrowid

    def get_character(self, character_id: int) -> Optional[Dict]:
        """Get character by ID"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM characters WHERE id = ?
            """, (character_id,))

            row = cursor.fetchone()
            if row:
                return dict(row)
            return None

    def get_character_by_name(self, name: str) -> Optional[Dict]:
        """Get character by name"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM characters WHERE name = ?
                ORDER BY created_at DESC LIMIT 1
            """, (name,))

            row = cursor.fetchone()
            if row:
                return dict(row)
            return None

    def update_character(self, character_id: int, **kwargs):
        """Update character attributes"""
        if not kwargs:
            return

        # Convert metrics dict to JSON if present
        if 'metrics' in kwargs:
            kwargs['metrics_json'] = json.dumps(kwargs.pop('metrics'))

        # Add last_updated timestamp
        kwargs['last_updated'] = datetime.now().isoformat()

        # Build UPDATE query
        set_clause = ", ".join([f"{key} = ?" for key in kwargs.keys()])
        values = list(kwargs.values()) + [character_id]

        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(f"""
                UPDATE characters SET {set_clause}
                WHERE id = ?
            """, values)

    def get_all_characters(self, limit: int = 100, offset: int = 0) -> List[Dict]:
        """Get all characters with pagination"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM characters
                ORDER BY last_updated DESC
                LIMIT ? OFFSET ?
            """, (limit, offset))

            return [dict(row) for row in cursor.fetchall()]

    def get_character_stats(self, character_id: int) -> Dict:
        """Get comprehensive stats for a character"""
        with self.get_connection() as conn:
            cursor = conn.cursor()

            # Basic info
            char = self.get_character(character_id)
            if not char:
                return {}

            # Training history
            cursor.execute("""
                SELECT COUNT(*) as total_sessions,
                       SUM(completed_epochs) as total_epochs,
                       AVG(final_accuracy) as avg_accuracy,
                       MAX(final_accuracy) as best_accuracy,
                       SUM(duration_seconds) as total_time
                FROM training_sessions
                WHERE character_id = ? AND status = 'completed'
            """, (character_id,))

            stats = dict(cursor.fetchone())

            return {
                **char,
                'training_stats': stats
            }

    def delete_character(self, character_id: int):
        """Delete a character and all associated data"""
        with self.get_connection() as conn:
            cursor = conn.cursor()

            # Delete training metrics first
            cursor.execute("""
                DELETE FROM training_metrics
                WHERE session_id IN (
                    SELECT id FROM training_sessions
                    WHERE character_id = ?
                )
            """, (character_id,))

            # Delete training sessions
            cursor.execute("""
                DELETE FROM training_sessions WHERE character_id = ?
            """, (character_id,))

            # Delete character
            cursor.execute("""
                DELETE FROM characters WHERE id = ?
            """, (character_id,))

    # ========================================================================
    # Training Session Operations
    # ========================================================================

    def create_training_session(self, character_id: Optional[int],
                               model_name: str, total_epochs: int,
                               initial_health: int) -> int:
        """Create a new training session"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO training_sessions
                (character_id, model_name, total_epochs, initial_health)
                VALUES (?, ?, ?, ?)
            """, (character_id, model_name, total_epochs, initial_health))

            return cursor.lastrowid

    def update_training_session(self, session_id: int, **kwargs):
        """Update training session"""
        if not kwargs:
            return

        set_clause = ", ".join([f"{key} = ?" for key in kwargs.keys()])
        values = list(kwargs.values()) + [session_id]

        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(f"""
                UPDATE training_sessions SET {set_clause}
                WHERE id = ?
            """, values)

    def complete_training_session(self, session_id: int,
                                  final_accuracy: float, final_loss: float,
                                  final_health: int, duration_seconds: int):
        """Mark training session as completed"""
        self.update_training_session(
            session_id,
            completed_at=datetime.now().isoformat(),
            final_accuracy=final_accuracy,
            final_loss=final_loss,
            final_health=final_health,
            duration_seconds=duration_seconds,
            status='completed'
        )

    def add_training_metric(self, session_id: int, epoch: int,
                          accuracy: float, loss: float, health: int):
        """Add epoch-by-epoch metrics"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO training_metrics
                (session_id, epoch, accuracy, loss, health)
                VALUES (?, ?, ?, ?, ?)
            """, (session_id, epoch, accuracy, loss, health))

    def get_training_session(self, session_id: int) -> Optional[Dict]:
        """Get training session by ID"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM training_sessions WHERE id = ?
            """, (session_id,))

            row = cursor.fetchone()
            if row:
                return dict(row)
            return None

    def get_session_metrics(self, session_id: int) -> List[Dict]:
        """Get all metrics for a training session"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM training_metrics
                WHERE session_id = ?
                ORDER BY epoch ASC
            """, (session_id,))

            return [dict(row) for row in cursor.fetchall()]

    def get_character_sessions(self, character_id: int,
                              limit: int = 10) -> List[Dict]:
        """Get training sessions for a character"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM training_sessions
                WHERE character_id = ?
                ORDER BY started_at DESC
                LIMIT ?
            """, (character_id, limit))

            return [dict(row) for row in cursor.fetchall()]

    def get_recent_sessions(self, limit: int = 20) -> List[Dict]:
        """Get most recent training sessions"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT ts.*, c.name as character_name, c.class as character_class
                FROM training_sessions ts
                LEFT JOIN characters c ON ts.character_id = c.id
                ORDER BY ts.started_at DESC
                LIMIT ?
            """, (limit,))

            return [dict(row) for row in cursor.fetchall()]

    # ========================================================================
    # Statistics Operations
    # ========================================================================

    def update_daily_statistics(self):
        """Update statistics for today"""
        with self.get_connection() as conn:
            cursor = conn.cursor()

            # Calculate today's stats
            cursor.execute("""
                SELECT
                    COUNT(DISTINCT c.id) as total_characters,
                    COUNT(DISTINCT ts.id) as total_sessions,
                    COALESCE(SUM(ts.completed_epochs), 0) as total_epochs,
                    AVG(ts.final_accuracy) as avg_accuracy
                FROM characters c
                LEFT JOIN training_sessions ts ON c.id = ts.character_id
                WHERE DATE(c.created_at) = DATE('now')
                   OR DATE(ts.started_at) = DATE('now')
            """)

            stats = cursor.fetchone()

            # Insert or update
            cursor.execute("""
                INSERT INTO statistics
                (date, total_characters, total_sessions, total_epochs, avg_accuracy)
                VALUES (DATE('now'), ?, ?, ?, ?)
                ON CONFLICT(date) DO UPDATE SET
                    total_characters = excluded.total_characters,
                    total_sessions = excluded.total_sessions,
                    total_epochs = excluded.total_epochs,
                    avg_accuracy = excluded.avg_accuracy
            """, (stats[0], stats[1], stats[2], stats[3]))

    def get_global_statistics(self) -> Dict:
        """Get overall statistics"""
        with self.get_connection() as conn:
            cursor = conn.cursor()

            # Total counts
            cursor.execute("""
                SELECT
                    COUNT(*) as total_characters,
                    COALESCE(SUM(total_training_time), 0) as total_training_time
                FROM characters
            """)
            char_stats = dict(cursor.fetchone())

            cursor.execute("""
                SELECT
                    COUNT(*) as total_sessions,
                    COUNT(CASE WHEN status = 'completed' THEN 1 END) as completed_sessions,
                    COALESCE(SUM(completed_epochs), 0) as total_epochs,
                    AVG(final_accuracy) as avg_accuracy,
                    MAX(final_accuracy) as best_accuracy
                FROM training_sessions
            """)
            session_stats = dict(cursor.fetchone())

            # Most trained character
            cursor.execute("""
                SELECT c.name, c.class, COUNT(ts.id) as session_count
                FROM characters c
                LEFT JOIN training_sessions ts ON c.id = ts.character_id
                GROUP BY c.id
                ORDER BY session_count DESC
                LIMIT 1
            """)
            top_char = cursor.fetchone()

            return {
                **char_stats,
                **session_stats,
                'top_character': dict(top_char) if top_char else None
            }

    def get_statistics_history(self, days: int = 30) -> List[Dict]:
        """Get statistics for the last N days"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM statistics
                WHERE date >= DATE('now', '-' || ? || ' days')
                ORDER BY date DESC
            """, (days,))

            return [dict(row) for row in cursor.fetchall()]

    # ========================================================================
    # User Preferences
    # ========================================================================

    def set_preference(self, key: str, value: str):
        """Set user preference"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO user_preferences (key, value)
                VALUES (?, ?)
                ON CONFLICT(key) DO UPDATE SET
                    value = excluded.value,
                    updated_at = CURRENT_TIMESTAMP
            """, (key, value))

    def get_preference(self, key: str, default: Optional[str] = None) -> Optional[str]:
        """Get user preference"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT value FROM user_preferences WHERE key = ?
            """, (key,))

            row = cursor.fetchone()
            return row[0] if row else default

    def get_all_preferences(self) -> Dict:
        """Get all user preferences"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT key, value FROM user_preferences")

            return {row[0]: row[1] for row in cursor.fetchall()}

    # ========================================================================
    # Export Operations
    # ========================================================================

    def export_to_dict(self) -> Dict:
        """Export entire database to dictionary"""
        return {
            'characters': self.get_all_characters(limit=1000),
            'recent_sessions': self.get_recent_sessions(limit=100),
            'statistics': self.get_global_statistics(),
            'preferences': self.get_all_preferences()
        }

    def export_character_history(self, character_id: int) -> Dict:
        """Export complete history for a character"""
        char = self.get_character_stats(character_id)
        if not char:
            return {}

        sessions = self.get_character_sessions(character_id, limit=1000)

        # Get metrics for each session
        for session in sessions:
            session['metrics'] = self.get_session_metrics(session['id'])

        return {
            'character': char,
            'training_sessions': sessions
        }

    # ========================================================================
    # Utility Operations
    # ========================================================================

    def get_database_size(self) -> int:
        """Get database file size in bytes"""
        if os.path.exists(self.db_path):
            return os.path.getsize(self.db_path)
        return 0

    def vacuum_database(self):
        """Optimize database (reclaim space)"""
        with self.get_connection() as conn:
            conn.execute("VACUUM")

    def backup_database(self, backup_path: str):
        """Create a backup of the database"""
        import shutil
        shutil.copy2(self.db_path, backup_path)

    def clear_old_data(self, days: int = 90):
        """Delete data older than specified days"""
        with self.get_connection() as conn:
            cursor = conn.cursor()

            # Delete old training metrics
            cursor.execute("""
                DELETE FROM training_metrics
                WHERE session_id IN (
                    SELECT id FROM training_sessions
                    WHERE started_at < DATE('now', '-' || ? || ' days')
                )
            """, (days,))

            # Delete old training sessions
            cursor.execute("""
                DELETE FROM training_sessions
                WHERE started_at < DATE('now', '-' || ? || ' days')
            """, (days,))

            # Delete old statistics
            cursor.execute("""
                DELETE FROM statistics
                WHERE date < DATE('now', '-' || ? || ' days')
            """, (days,))


# Singleton instance
_db_instance = None

def get_database() -> Database:
    """Get or create database singleton instance"""
    global _db_instance
    if _db_instance is None:
        _db_instance = Database()
    return _db_instance
