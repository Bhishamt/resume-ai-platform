"""Repository layer for User database operations.

All database queries for the User model are isolated here.
Business logic belongs in the service layer, not here.
"""

from datetime import datetime, timezone
from typing import Optional
from uuid import UUID

from sqlalchemy.orm import Session

from app.models.user import User


def get_by_id(db: Session, user_id: UUID) -> Optional[User]:
    """Fetch a user by their UUID."""
    return db.query(User).filter(User.id == user_id).first()


def get_by_email(db: Session, email: str) -> Optional[User]:
    """Fetch a user by their email address."""
    return db.query(User).filter(User.email == email).first()


def create(db: Session, *, full_name: str, email: str, password_hash: str) -> User:
    """Create a new user record."""
    user = User(
        full_name=full_name,
        email=email,
        password_hash=password_hash,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def update(db: Session, user: User, update_data: dict) -> User:
    """Update user fields from a dictionary of changes."""
    for field, value in update_data.items():
        if hasattr(user, field) and value is not None:
            setattr(user, field, value)
    user.updated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(user)
    return user


def update_last_login(db: Session, user: User) -> User:
    """Update the user's last login timestamp."""
    user.last_login = datetime.now(timezone.utc)
    user.updated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(user)
    return user
