
import os
import sqlite3
import tempfile
from pathlib import Path

# ==========================================
# RAREMOTION LABS — DATABASE
# ==========================================

DB_PATH = Path(__file__).resolve().parent / "inventory.db"


def get_connection():
    db_path = DB_PATH
    if os.environ.get("RAREMOTION_DEMO") == "1":
        import streamlit as st

        if "demo_db_path" not in st.session_state:
            # Each visitor gets an empty, disposable database, never business data.
            demo_dir = Path(tempfile.mkdtemp(prefix="raremotion-demo-"))
            st.session_state["demo_db_path"] = demo_dir / "demo.db"
        db_path = st.session_state["demo_db_path"]
    conn = sqlite3.connect(
        db_path,
        timeout=10
    )
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    with get_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                category TEXT,
                quantity INTEGER NOT NULL DEFAULT 0
                    CHECK(quantity >= 0),
                price REAL NOT NULL DEFAULT 0
                    CHECK(price >= 0)
            )
        """)

        conn.execute("""
            CREATE TABLE IF NOT EXISTS sales (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                product_id INTEGER NOT NULL,
                quantity INTEGER NOT NULL
                    CHECK(quantity > 0),
                total REAL NOT NULL
                    CHECK(total >= 0),
                created_at TIMESTAMP
                    DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (product_id)
                    REFERENCES products(id)
            )
        """)

        conn.commit()
