"""
Database Module for Smart Agriculture Agent.
Handles SQLite database connection, safe schema migrations, farmer authentication persistence,
farmer profiles, and multi-tenant isolated historical telemetry queries.
Preserves all legacy records in 'farm_readings'.
"""

import sqlite3
import datetime
from typing import Optional, Dict, Any, List
import pandas as pd
import auth

DB_FILE = "smart_agri.db"


def get_connection() -> sqlite3.Connection:
    """Creates and returns a connection to the SQLite database."""
    conn = sqlite3.connect(DB_FILE, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    """
    Initializes and safely migrates the database schema:
    1. Ensures 'farmers' table exists for authentication and language preferences.
    2. Ensures 'farmer_profiles' table exists for parcel metadata and soil chemistry.
    3. Ensures 'farm_readings' table exists and safely adds 'farmer_id' column if missing.
    4. Ensures a default demo farmer exists and maps legacy unassigned readings.
    """
    conn = get_connection()
    try:
        with conn:
            # 1. Farmers Table
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS farmers (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    phone_number TEXT UNIQUE NOT NULL,
                    full_name TEXT NOT NULL,
                    password_hash TEXT NOT NULL,
                    salt TEXT NOT NULL,
                    preferred_language TEXT DEFAULT 'en',
                    created_at TEXT NOT NULL
                )
                """
            )

            # 2. Farmer Profiles Table
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS farmer_profiles (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    farmer_id INTEGER UNIQUE NOT NULL,
                    farm_name TEXT,
                    location_district TEXT,
                    latitude REAL,
                    longitude REAL,
                    farm_size_acres REAL,
                    soil_type TEXT,
                    primary_crop TEXT,
                    irrigation_system TEXT,
                    soil_ph REAL,
                    nitrogen REAL,
                    phosphorus REAL,
                    potassium REAL,
                    updated_at TEXT,
                    FOREIGN KEY(farmer_id) REFERENCES farmers(id) ON DELETE CASCADE
                )
                """
            )

            # 3. Base Farm Readings Table
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

            # Safe Schema Migration: Check if 'farmer_id' exists in 'farm_readings'
            readings_cols = [row["name"] for row in conn.execute("PRAGMA table_info(farm_readings)").fetchall()]
            if "farmer_id" not in readings_cols:
                conn.execute("ALTER TABLE farm_readings ADD COLUMN farmer_id INTEGER REFERENCES farmers(id)")

            # Safe Schema Migration: Check if 'water_availability' exists in 'farmer_profiles'
            prof_cols = [row["name"] for row in conn.execute("PRAGMA table_info(farmer_profiles)").fetchall()]
            if "water_availability" not in prof_cols:
                conn.execute("ALTER TABLE farmer_profiles ADD COLUMN water_availability TEXT DEFAULT 'Moderate'")

            # 4. Preserve Legacy Records under an Archived Historical Station Account
            cursor = conn.execute("SELECT id FROM farmers WHERE phone_number = '9876543210'")
            legacy_user = cursor.fetchone()
            if not legacy_user:
                archive_hash, archive_salt = auth.hash_password("legacy_archive_locked")
                now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                cursor = conn.execute(
                    """
                    INSERT INTO farmers (phone_number, full_name, password_hash, salt, preferred_language, created_at)
                    VALUES (?, ?, ?, ?, ?, ?)
                    """,
                    ("9876543210", "Archived Historical Station", archive_hash, archive_salt, "en", now_str)
                )
                archive_id = cursor.lastrowid
                conn.execute(
                    """
                    INSERT INTO farmer_profiles (
                        farmer_id, farm_name, location_district, latitude, longitude,
                        farm_size_acres, soil_type, primary_crop, irrigation_system,
                        soil_ph, nitrogen, phosphorus, potassium, water_availability, updated_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        archive_id, "Archived Farm Parcel", "Guntur", 16.3067, 80.4365,
                        3.5, "Clay Loam", "Tomato", "Drip Irrigation",
                        6.8, 140.0, 45.0, 180.0, "Moderate", now_str
                    )
                )
            else:
                archive_id = legacy_user["id"]
                # Ensure name is updated to Archived Historical Station (never demo)
                conn.execute("UPDATE farmers SET full_name = 'Archived Historical Station' WHERE id = ?", (archive_id,))

            # Map any legacy unassigned records to archive_id so they remain preserved and isolated
            conn.execute("UPDATE farm_readings SET farmer_id = ? WHERE farmer_id IS NULL", (archive_id,))
    finally:
        conn.close()


# ==============================================================================
# Farmer Authentication & Account CRUD
# ==============================================================================

def create_farmer(
    full_name: str,
    phone_number: str,
    password: str,
    preferred_language: str = "en"
) -> Any:
    """
    Registers a new farmer account with salted PBKDF2 hash.
    Returns (success: bool, message: str, farmer_dict: Optional[Dict]).
    """
    cleaned_phone = auth.clean_phone_number(phone_number)
    conn = get_connection()
    try:
        with conn:
            # Check for existing phone number
            existing = conn.execute(
                "SELECT id FROM farmers WHERE phone_number = ?", (cleaned_phone,)
            ).fetchone()
            if existing:
                return False, "This mobile number is already registered.", None

            pwd_hash, salt = auth.hash_password(password)
            now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            cursor = conn.execute(
                """
                INSERT INTO farmers (phone_number, full_name, password_hash, salt, preferred_language, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (cleaned_phone, full_name.strip(), pwd_hash, salt, preferred_language, now_str)
            )
            farmer_id = cursor.lastrowid

            # Create an empty profile record for the new farmer
            conn.execute(
                """
                INSERT INTO farmer_profiles (
                    farmer_id, farm_name, location_district, latitude, longitude,
                    farm_size_acres, soil_type, primary_crop, irrigation_system,
                    soil_ph, nitrogen, phosphorus, potassium, water_availability, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    farmer_id, f"{full_name.strip()}'s Farm", "Andhra Pradesh", 16.3067, 80.4365,
                    2.0, "Loamy Soil", "Rice", "Drip Irrigation",
                    6.5, 120.0, 40.0, 150.0, "Moderate", now_str
                )
            )

            farmer_dict = {
                "id": farmer_id,
                "phone_number": cleaned_phone,
                "full_name": full_name.strip(),
                "preferred_language": preferred_language
            }
            return True, "Registration successful!", farmer_dict
    except Exception as e:
        return False, f"Registration failed: {str(e)}", None
    finally:
        conn.close()


def authenticate_farmer(phone_number: str, password: str) -> Optional[Dict[str, Any]]:
    """
    Authenticates a farmer by phone number and password.
    Returns farmer dict if valid, None otherwise.
    """
    cleaned_phone = auth.clean_phone_number(phone_number)
    conn = get_connection()
    try:
        cursor = conn.execute(
            "SELECT * FROM farmers WHERE phone_number = ?", (cleaned_phone,)
        )
        row = cursor.fetchone()
        if not row:
            return None

        if auth.verify_password(password, row["salt"], row["password_hash"]):
            return {
                "id": row["id"],
                "phone_number": row["phone_number"],
                "full_name": row["full_name"],
                "preferred_language": row["preferred_language"] or "en"
            }
        return None
    finally:
        conn.close()


def update_farmer_language(farmer_id: int, new_language: str) -> None:
    """Updates the preferred language for a farmer."""
    conn = get_connection()
    try:
        with conn:
            conn.execute(
                "UPDATE farmers SET preferred_language = ? WHERE id = ?",
                (new_language, farmer_id)
            )
    finally:
        conn.close()


# ==============================================================================
# Farmer Profile CRUD
# ==============================================================================

def get_farmer_profile(farmer_id: int) -> Optional[Dict[str, Any]]:
    """Retrieves farm profile and soil parameters for a farmer."""
    conn = get_connection()
    try:
        cursor = conn.execute(
            "SELECT * FROM farmer_profiles WHERE farmer_id = ?", (farmer_id,)
        )
        row = cursor.fetchone()
        if row:
            return dict(row)
        return None
    finally:
        conn.close()


def upsert_farmer_profile(
    farmer_id: int,
    farm_name: str,
    location_district: str,
    farm_size_acres: float,
    soil_type: str,
    primary_crop: str,
    irrigation_system: str,
    soil_ph: float = 6.5,
    nitrogen: float = 120.0,
    phosphorus: float = 40.0,
    potassium: float = 150.0,
    water_availability: str = "Moderate",
    latitude: Optional[float] = 16.3067,
    longitude: Optional[float] = 80.4365
) -> bool:
    """Creates or updates a farmer's farm profile including water availability."""
    conn = get_connection()
    now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    try:
        with conn:
            conn.execute(
                """
                INSERT INTO farmer_profiles (
                    farmer_id, farm_name, location_district, latitude, longitude,
                    farm_size_acres, soil_type, primary_crop, irrigation_system,
                    soil_ph, nitrogen, phosphorus, potassium, water_availability, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(farmer_id) DO UPDATE SET
                    farm_name = excluded.farm_name,
                    location_district = excluded.location_district,
                    latitude = excluded.latitude,
                    longitude = excluded.longitude,
                    farm_size_acres = excluded.farm_size_acres,
                    soil_type = excluded.soil_type,
                    primary_crop = excluded.primary_crop,
                    irrigation_system = excluded.irrigation_system,
                    soil_ph = excluded.soil_ph,
                    nitrogen = excluded.nitrogen,
                    phosphorus = excluded.phosphorus,
                    potassium = excluded.potassium,
                    water_availability = excluded.water_availability,
                    updated_at = excluded.updated_at
                """,
                (
                    farmer_id, farm_name, location_district, latitude, longitude,
                    float(farm_size_acres), soil_type, primary_crop, irrigation_system,
                    float(soil_ph), float(nitrogen), float(phosphorus), float(potassium),
                    water_availability,
                    now_str
                )
            )
            return True
    finally:
        conn.close()


# ==============================================================================
# Isolated Telemetry & Farm Readings CRUD
# ==============================================================================

def save_reading(
    crop_type: str,
    growth_stage: str,
    soil_moisture: float,
    temperature: float,
    status: str,
    action_title: str,
    reasoning: str,
    practical_steps: str,
    timestamp: Optional[str] = None,
    farmer_id: Optional[int] = None
) -> int:
    """
    Inserts a newly analyzed field observation and advisory into SQLite,
    associating it with the authenticated farmer_id for data isolation.
    """
    if timestamp is None:
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    conn = get_connection()
    try:
        with conn:
            cursor = conn.execute(
                """
                INSERT INTO farm_readings (
                    farmer_id, timestamp, crop_type, growth_stage,
                    soil_moisture, temperature, status,
                    action_title, reasoning, practical_steps
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    farmer_id,
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


def get_latest_reading(farmer_id: Optional[int] = None) -> Optional[Dict[str, Any]]:
    """
    Retrieves the most recent field reading and recommendation.
    If farmer_id is provided, filters strictly for that farmer.
    """
    conn = get_connection()
    try:
        if farmer_id is not None:
            cursor = conn.execute(
                """
                SELECT * FROM farm_readings
                WHERE farmer_id = ?
                ORDER BY id DESC
                LIMIT 1
                """,
                (farmer_id,)
            )
        else:
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


def get_history(farmer_id: Optional[int] = None, limit: int = 100) -> pd.DataFrame:
    """
    Fetches historical readings up to the given limit as a pandas DataFrame.
    Filters strictly by farmer_id when supplied to enforce data isolation.
    """
    conn = get_connection()
    try:
        base_query = """
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
        """
        if farmer_id is not None:
            query = base_query + " WHERE farmer_id = ? ORDER BY id DESC LIMIT ?"
            df = pd.read_sql_query(query, conn, params=(farmer_id, limit))
        else:
            query = base_query + " ORDER BY id DESC LIMIT ?"
            df = pd.read_sql_query(query, conn, params=(limit,))
        return df
    finally:
        conn.close()


get_readings_history = get_history


def clear_history(farmer_id: Optional[int] = None) -> None:
    """
    Clears historical records. If farmer_id is supplied, clears ONLY
    that farmer's private records, leaving all other farmers' data safe.
    """
    conn = get_connection()
    try:
        with conn:
            if farmer_id is not None:
                conn.execute("DELETE FROM farm_readings WHERE farmer_id = ?", (farmer_id,))
            else:
                conn.execute("DELETE FROM farm_readings")
    finally:
        conn.close()
