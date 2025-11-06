# app/utils/create_default_admin.py

import os
from sqlmodel import select, Session
from db.database import get_session
from models.model import User, UserRole
from controllers.middleware.auth import get_password_hash


def create_default_admin() -> None:
    """
    Create a default admin user if none exists.
    Reads credentials from environment variables:
    - ADMIN_USERNAME
    - ADMIN_EMAIL
    - ADMIN_PASSWORD

    This version includes strict existence checks
    and avoids printing sensitive credentials.
    """

    admin_username = os.getenv("ADMIN_USERNAME")
    admin_email = os.getenv("ADMIN_EMAIL")
    admin_password = os.getenv("ADMIN_PASSWORD")

    if not all([admin_username, admin_email, admin_password]):
        raise EnvironmentError(
            "Missing required environment variables: "
            "ADMIN_USERNAME, ADMIN_EMAIL, ADMIN_PASSWORD"
        )

    session_generator = get_session()
    session: Session = next(session_generator)

    try:
        # Check if user exists already (by username OR email)
        existing_user = session.exec(
            select(User).where(
                (User.username == admin_username) | (User.email == admin_email)
            )
        ).first()

        if existing_user:
            print("Admin user already exists. Skipping creation.")
            return

        admin_user = User(
            username=admin_username,
            email=admin_email,
            hashed_password=get_password_hash(admin_password),
            role=UserRole.ADMIN,
        )

        session.add(admin_user)
        session.commit()
        session.refresh(admin_user)

        print(f"Default admin created successfully: username={admin_username}, role=ADMIN")

    except Exception as e:
        session.rollback()
        print("Error creating default admin:", e)

    finally:
        session.close()
        try:
            next(session_generator)
        except StopIteration:
            pass


if __name__ == "__main__":
    create_default_admin()
