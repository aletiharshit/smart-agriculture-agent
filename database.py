"""
Database Module for Smart Agriculture Agent
Handles SQLite database connection, table initialization, record insertion,
and historical queries for agricultural telemetry and recommendation logs.
"""

import sqlite3
import datetime
from typing import Optional, Dict, Any
import pandas as pd

DB_FILE = "smart_agri.db"


def get_connection() -> sqlite3.Connection:
    """Creates and returns a connection to the SQLite database."""
    conn = sqlite3.connect(DB_FILE, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    """
    Initializes the database schema if tables do not already exist.
    Creates the 'farm_readings' table to log field observations and advisories.
    """
    conn = get_connection()
    try:
        with conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS farm_readings (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    crop_type TEXT NOT NULL,
                    growth_stage TEXT NOT NULL,
                    soil_moisture REAL NOT NULL,
                    temperature REAL NOT NULL,
                    status TEXT NOT NULL,
                    action_title TEXT NOT NULL,
                    reasoning TEXT NOT NULL,
                    practical_steps TEXT NOT NULL
                )
                """
            )
    finally:
        conn.close()


def save_reading(
    crop_type: str,
    growth_stage: str,
    soil_moisture: float,
    temperature: float,
    status: str,
    action_title: str,
    reasoning: str,
    practical_steps: str,
    timestamp: Optional[str] = None
) -> int:
    """
    Inserts a newly analyzed field observation and advisory into SQLite.
    Returns the auto-generated row ID.
    """
    if timestamp is None:
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    conn = get_connection()
    try:
        with conn:
            cursor = conn.execute(
                """
                INSERT INTO farm_readings (
                    timestamp, crop_type, growth_stage,
                    soil_moisture, temperature, status,
                    action_title, reasoning, practical_steps
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    timestamp,
                    crop_type,
                    growth_stage,
                    float(soil_moisture),
                    float(temperature),
                    status,
                    action_title,
                    reasoning,
                    practical_steps,
                ),
            )
            return cursor.lastrowid
    finally:
        conn.close()


def get_latest_reading() -> Optional[Dict[str, Any]]:
    """
    Retrieves the most recent field reading and recommendation.
    Returns None if the database table is empty.
    """
    conn = get_connection()
    try:
        cursor = conn.execute(
            """
            SELECT * FROM farm_readings
            ORDER BY id DESC
            LIMIT 1
            """
        )
        row = cursor.fetchone()
        if row:
            return dict(row)
        return None
    finally:
        conn.close()


def get_history(limit: int = 100) -> pd.DataFrame:
    """
    Fetches historical readings up to the given limit as a pandas DataFrame.
    Returns an empty DataFrame if no records exist.
    """
    conn = get_connection()
    try:
        query = """
            SELECT 
                id AS 'Record ID',
                timestamp AS 'Timestamp',
                crop_type AS 'Crop',
                growth_stage AS 'Growth Stage',
                soil_moisture AS 'Soil Moisture (%)',
                temperature AS 'Temperature (°C)',
                status AS 'Status',
                action_title AS 'Advisory Action',
                reasoning AS 'Reasoning',
                practical_steps AS 'Recommended Steps'
            FROM farm_readings
            ORDER BY id DESC
            LIMIT ?
        """
        df = pd.read_sql_query(query, conn, params=(limit,))
        return df
    finally:
        conn.close()


def clear_history() -> None:
    """
    Clears all records from the farm_readings table.
    Useful for demonstration resets in academic capstone presentations.
    """
    conn = get_connection()
    try:
        with conn:
            conn.execute("DELETE FROM farm_readings")
    finally:
        conn.close()
