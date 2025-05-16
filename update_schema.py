from app.session import engine
from sqlalchemy import text
import sqlite3


def update_schema():
    print("Starting database schema update...")

    try:
        # Method 1: Try direct ALTER TABLE approach
        with engine.connect() as connection:
            try:
                print("Attempting to add created_at column...")
                connection.execute(text("ALTER TABLE users ADD COLUMN created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP"))
                connection.commit()
                print("Column added successfully!")
                return True
            except Exception as e:
                print(f"Direct ALTER TABLE failed: {e}")
                print("Trying alternate approach...")

        # Method 2: If ALTER TABLE fails, recreate the table with backup
        # Connect directly with sqlite3 for more control
        db_path = engine.url.database  # Get SQLite database path from engine

        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        print("Creating backup of users table...")
        cursor.execute("""
        CREATE TABLE users_backup (
            id INTEGER PRIMARY KEY,
            username VARCHAR UNIQUE,
            email VARCHAR UNIQUE,
            hashed_password VARCHAR,
            is_active BOOLEAN DEFAULT 1
        )
        """)

        # Copy existing data
        print("Copying existing data...")
        cursor.execute("INSERT INTO users_backup SELECT id, username, email, hashed_password, is_active FROM users")

        # Drop original table
        print("Dropping original table...")
        cursor.execute("DROP TABLE users")

        # Create new table with correct schema
        print("Creating new users table with correct schema...")
        cursor.execute("""
        CREATE TABLE users (
            id INTEGER PRIMARY KEY,
            username VARCHAR UNIQUE,
            email VARCHAR UNIQUE,
            hashed_password VARCHAR,
            is_active BOOLEAN DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)

        # Copy data back
        print("Restoring data...")
        cursor.execute("""
        INSERT INTO users (id, username, email, hashed_password, is_active)
        SELECT id, username, email, hashed_password, is_active FROM users_backup
        """)

        # Drop backup table
        print("Cleaning up...")
        cursor.execute("DROP TABLE users_backup")

        # Commit changes
        conn.commit()
        conn.close()

        print("Schema update completed successfully!")
        return True

    except Exception as e:
        print(f"Error updating schema: {e}")
        return False


if __name__ == "__main__":
    update_schema()