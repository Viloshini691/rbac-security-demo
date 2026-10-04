import sqlite3
from werkzeug.security import generate_password_hash


DATABASE = "rbac.db"


def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


def initialize_database():
    conn = get_db()

    conn.executescript("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            content TEXT NOT NULL,
            FOREIGN KEY(patient_id) REFERENCES users(id)
        );

        CREATE TABLE IF NOT EXISTS access_control (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            record_id INTEGER NOT NULL,
            doctor_id INTEGER NOT NULL,
            UNIQUE(record_id, doctor_id),
            FOREIGN KEY(record_id) REFERENCES records(id),
            FOREIGN KEY(doctor_id) REFERENCES users(id)
        );

        CREATE TABLE IF NOT EXISTS audit_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            action TEXT NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        );
    """)

    create_demo_users(conn)

    conn.commit()
    conn.close()


def create_demo_users(conn):
    demo_users = [
        ("admin", "Admin123!", "admin"),
        ("patient1", "Patient123!", "patient"),
        ("doctor1", "Doctor123!", "doctor"),
        ("doctor2", "Doctor456!", "doctor"),
    ]

    for username, password, role in demo_users:
        existing = conn.execute(
            "SELECT id FROM users WHERE username = ?",
            (username,),
        ).fetchone()

        if not existing:
            conn.execute(
                """
                INSERT INTO users (username, password, role)
                VALUES (?, ?, ?)
                """,
                (
                    username,
                    generate_password_hash(password),
                    role,
                ),
            )


def log_action(username, action):
    conn = get_db()

    conn.execute(
        """
        INSERT INTO audit_logs (username, action)
        VALUES (?, ?)
        """,
        (username, action),
    )

    conn.commit()
    conn.close()