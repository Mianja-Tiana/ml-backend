# app/utils/create_default_admin.py

import os
from sqlmodel import select, Session
from db.database import get_session
from models.model import User, UserRole
from auth.security import get_password_hash


def create_default_admin() -> None:
    """
    Create a default admin user if none exists.
    Reads credentials from environment variables:
    - ADMIN_USERNAME
    - ADMIN_EMAIL
    - ADMIN_PASSWORD

    Raises:
        EnvironmentError: if any required env variable is missing.
    """

    # --- Enforce required environment variables ---
    admin_username = os.getenv("ADMIN_USERNAME")
    admin_email = os.getenv("ADMIN_EMAIL")
    admin_password = os.getenv("ADMIN_PASSWORD")

    if not all([admin_username, admin_email, admin_password]):
        raise EnvironmentError(
            "Missing required environment variables: "
            "ADMIN_USERNAME, ADMIN_EMAIL, ADMIN_PASSWORD"
        )

    # --- Open a session safely ---
    session_generator = get_session()
    session: Session = next(session_generator)

    try:
        # Check if the admin already exists
        existing_admin = session.exec(
            select(User).where(User.username == admin_username)
        ).first()

        if existing_admin:
            print("Admin user already exists.")
            return

        # Create new admin user
        admin_user = User(
            username=admin_username,
            email=admin_email,
            hashed_password=get_password_hash(admin_password),
            role=UserRole.ADMIN,
        )

        session.add(admin_user)
        session.commit()
        session.refresh(admin_user)

        print(f" Default admin created successfully:")
        print(f"   Username: {admin_user.username}")
        print(f"   Password: {admin_password}")
        print(f"   Role: {admin_user.role}")

    except Exception as e:
        session.rollback()
        print("Error creating default admin:", e)

    finally:
        session.close()
        # Close the generator properly
        try:
            next(session_generator)
        except StopIteration:
            pass

# Run manually if script is executed directly
if __name__ == "__main__":
    create_default_admin()
