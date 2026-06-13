import sqlite3

DB_NAME = "chat.db"


def get_connection():
    return sqlite3.connect(DB_NAME)


def create_tables():

    conn = get_connection()
    cursor = conn.cursor()

    # Chat Sessions
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS chat_sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Chat Messages
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS chat_messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id INTEGER,
            role TEXT,
            content TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(session_id)
                REFERENCES chat_sessions(id)
        )
    """)

    conn.commit()
    conn.close()


# ------------------------------------
# Session Functions
# ------------------------------------

def create_session(title):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO chat_sessions(title)
        VALUES(?)
        """,
        (title,)
    )

    session_id = cursor.lastrowid

    conn.commit()
    conn.close()

    return session_id


def get_sessions():

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            id,
            title,
            created_at
        FROM chat_sessions
        ORDER BY id DESC
    """)

    rows = cursor.fetchall()

    conn.close()

    return rows


def update_session_title(session_id, title):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        UPDATE chat_sessions
        SET title = ?
        WHERE id = ?
        """,
        (title, session_id)
    )

    conn.commit()
    conn.close()


def delete_session(session_id):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        DELETE FROM chat_messages
        WHERE session_id = ?
        """,
        (session_id,)
    )

    cursor.execute(
        """
        DELETE FROM chat_sessions
        WHERE id = ?
        """,
        (session_id,)
    )

    conn.commit()
    conn.close()


# ------------------------------------
# Message Functions
# ------------------------------------

def save_message(
    session_id,
    role,
    content
):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO chat_messages
        (
            session_id,
            role,
            content
        )
        VALUES (?, ?, ?)
        """,
        (
            session_id,
            role,
            content
        )
    )

    conn.commit()
    conn.close()


def get_messages(session_id):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT
            role,
            content,
            created_at
        FROM chat_messages
        WHERE session_id = ?
        ORDER BY id
        """,
        (session_id,)
    )

    rows = cursor.fetchall()

    conn.close()

    return rows


def get_session(session_id):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT
            id,
            title,
            created_at
        FROM chat_sessions
        WHERE id = ?
        """,
        (session_id,)
    )

    row = cursor.fetchone()

    conn.close()

    return row