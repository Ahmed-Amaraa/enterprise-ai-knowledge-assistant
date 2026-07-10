from sqlalchemy.orm import Session
from app.models.user import User


class UserRepository:

    def __init__(self, db: Session):
        self.db = db

    def get_by_email(self, email: str):
        return (
            self.db.query(User)
            .filter(User.email == email)
            .first()
        )

    def get_by_username(self, username: str):
        return (
            self.db.query(User)
            .filter(User.username == username)
            .first()
        )

    def create_user(
        self,
        email: str,
        username: str,
        hashed_password: str,
        full_name: str | None = None,
    ):
        user = User(
            email=email,
            username=username,
            hashed_password=hashed_password,
            full_name=full_name,
        )

        return user
    
    def get_by_id(self, user_id: int):
        try:
            user_id = int(user_id)
        except (TypeError, ValueError):
            return None

        return (
            self.db.query(User)
            .filter(User.id == user_id)
            .first()
        )