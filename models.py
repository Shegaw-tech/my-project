import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import os

# Database file path
DB_PATH = os.path.join("instance", "app.sqlite")

# ----------------- Database Connection ----------------- #
def _conn():
    """Create a new SQLite connection with Row support."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

# ----------------- Initialize Database ----------------- #
def init_db():
    with _conn() as conn:
        cur = conn.cursor()
        # Create admin users table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS admin_users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                role TEXT NOT NULL DEFAULT 'admin'
            )
        """)
        # Create contents table with creator_id
        cur.execute("""
            CREATE TABLE IF NOT EXISTS contents (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                body TEXT,
                image_filename TEXT,
                is_published INTEGER NOT NULL DEFAULT 1,
                created_at TEXT NOT NULL,
                creator_id INTEGER,
                FOREIGN KEY(creator_id) REFERENCES admin_users(id)
            )
        """)
        conn.commit()

# ------------------ Admin Functions ------------------ #
def create_admin(username, password, role="admin"):
    with _conn() as conn:
        conn.execute(
            "INSERT INTO admin_users (username, password_hash, role) VALUES (?, ?, ?)",
            (username, generate_password_hash(password), role)
        )
        conn.commit()

def get_admin_by_username(username):
    with _conn() as conn:
        cur = conn.execute("SELECT * FROM admin_users WHERE username = ?", (username,))
        return cur.fetchone()

def get_admin_by_id(admin_id):
    with _conn() as conn:
        cur = conn.execute("SELECT * FROM admin_users WHERE id = ?", (admin_id,))
        return cur.fetchone()

def verify_password(stored_hash, password):
    """Verify a plaintext password against a stored hash."""
    return check_password_hash(stored_hash, password)

# ------------------ Content Functions ------------------ #
def list_contents(include_unpublished=False):
    """Return all contents; optionally include unpublished ones."""
    q = """
        SELECT c.*, a.username AS creator_name
        FROM contents c
        LEFT JOIN admin_users a ON c.creator_id = a.id
    """
    if not include_unpublished:
        q += " WHERE is_published = 1"
    q += " ORDER BY datetime(created_at) DESC"
    with _conn() as conn:
        return conn.execute(q).fetchall()

def get_content(item_id):
    """Get a single content item by ID."""
    with _conn() as conn:
        cur = conn.execute("SELECT * FROM contents WHERE id = ?", (item_id,))
        return cur.fetchone()

def create_content(title, body, image_filename=None, is_published=True, creator_id=None):
    """Create a new content entry."""
    with _conn() as conn:
        conn.execute(
            "INSERT INTO contents (title, body, image_filename, is_published, created_at, creator_id) VALUES (?, ?, ?, ?, ?, ?)",
            (title, body, image_filename, 1 if is_published else 0, datetime.utcnow().isoformat(), creator_id)
        )
        conn.commit()

def update_content(item_id, title, body, image_filename=None, is_published=True):
    """Update an existing content entry."""
    with _conn() as conn:
        conn.execute(
            "UPDATE contents SET title=?, body=?, image_filename=?, is_published=? WHERE id=?",
            (title, body, image_filename, 1 if is_published else 0, item_id)
        )
        conn.commit()

def delete_content(item_id):
    """Delete a content entry."""
    with _conn() as conn:
        conn.execute("DELETE FROM contents WHERE id = ?", (item_id,))
        conn.commit()
