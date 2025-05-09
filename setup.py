from sqlalchemy.orm import sessionmaker
from database import Base, engine
from app.schemas import User, History, Preference
from app.auth import get_password_hash
import argparse


def setup_database():
    """Create database tables and initial data"""
    # Create tables
    Base.metadata.create_all(bind=engine)
    print("Database tables created.")

    # Create session
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()

    # Check if admin user exists
    admin_exists = db.query(User).filter(User.username == "admin").first()

    if not admin_exists:
        # Create admin user
        admin_password = get_password_hash("admin")
        admin_user = User(
            username="admin",
            email="admin@example.com",
            full_name="Admin User",
            password=admin_password
        )
        db.add(admin_user)
        db.commit()
        print("Admin user created.")

    db.close()
    print("Database setup complete.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Setup the Music App database")
    parser.add_argument("--reset", action="store_true", help="Drop and recreate all tables")

    args = parser.parse_args()

    if args.reset:
        # Drop all tables
        Base.metadata.drop_all(bind=engine)
        print("All tables dropped.")

    # Create tables and initial data
    setup_database()