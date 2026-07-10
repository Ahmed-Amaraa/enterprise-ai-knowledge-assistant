from datetime import datetime, timedelta

from app.core.security import hash_password, verify_password
from app.core.jwt import create_access_token, create_refresh_token, decode_token
from app.core.config import REFRESH_TOKEN_EXPIRE_DAYS

from app.repositories.user_repository import UserRepository
from app.models.refresh_token import RefreshToken


class AuthService:
    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo
        self.db = user_repo.db

    def register_user(self, email: str, username: str, password: str, full_name: str | None = None):
        existing_user = self.user_repo.get_by_email(email)
        if existing_user:
            raise ValueError("Email already exists")

        existing_username = self.user_repo.get_by_username(username)
        if existing_username:
            raise ValueError("Username already exists")

        hashed = hash_password(password)

        user = self.user_repo.create_user(
            email=email,
            username=username,
            hashed_password=hashed,
            full_name=full_name
        )

        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user
    
    def login_user(self, email: str, password: str):
        user = self.user_repo.get_by_email(email)

        if not user:
            raise ValueError("Invalid credentials")

        if not verify_password(password, user.hashed_password):
            raise ValueError("Invalid credentials")

        access_token = create_access_token({"sub": str(user.id)})
        refresh_token = create_refresh_token({"sub": str(user.id)})

        self.db.query(RefreshToken).filter(
            RefreshToken.user_id == user.id,
            RefreshToken.is_revoked.is_(False),
        ).update({"is_revoked": True})

        refresh = RefreshToken(
            user_id=user.id,
            token=refresh_token,
            created_at=datetime.utcnow(),
            expires_at=datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS),
        )

        self.db.add(refresh)
        self.db.commit()

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer"
        }
    
    def verify_user(self, email: str, password: str):
        user = self.user_repo.get_by_email(email)

        if not user:
            return None

        if not verify_password(password, user.hashed_password):
            return None

        return user
    
    def refresh_access_token(self, refresh_token: str):

        # Decode the JWT
        payload = decode_token(refresh_token)

        if not payload:
            raise ValueError("Invalid token")

        # Check token type
        if payload.get("type") != "refresh":
            raise ValueError("Wrong token type")

        # Get user ID
        user_id = payload.get("sub")

        # Check user exists
        user = self.user_repo.get_by_id(user_id)
        if not user:
            raise ValueError("User not found")

        stored_refresh = self.db.query(RefreshToken).filter(
            RefreshToken.user_id == user.id,
            RefreshToken.token == refresh_token,
            RefreshToken.is_revoked.is_(False),
        ).first()

        if not stored_refresh:
            raise ValueError("Refresh token not recognized")

        if stored_refresh.expires_at and stored_refresh.expires_at <= datetime.utcnow():
            stored_refresh.is_revoked = True
            self.db.commit()
            raise ValueError("Refresh token expired")

        # Generate new access token
        new_access_token = create_access_token({"sub": str(user_id)})

        return {
            "access_token": new_access_token,
            "token_type": "bearer"
        }
        
    def logout(self, refresh_token: str):
        # Decode the JWT refresh token to extract its payload (user data + metadata)
        payload = decode_token(refresh_token)

        # If decoding fails, the token is either tampered with, expired, or malformed
        if not payload:
            raise ValueError("Invalid token")

        # Ensure the token being used is actually a refresh token
        # This prevents someone from trying to misuse an access token here
        if payload.get("type") != "refresh":
            raise ValueError("Invalid token type")

        # Extract the user ID from the token payload
        # "sub" = subject (standard JWT claim for user identity)
        user_id = payload.get("sub")

        # Fetch the user from the database
        user = self.user_repo.get_by_id(user_id)

        # If the user no longer exists, the token is invalid in practice
        if not user:
            raise ValueError("User not found")

        stored_refresh = self.db.query(RefreshToken).filter(
            RefreshToken.user_id == user.id,
            RefreshToken.token == refresh_token,
            RefreshToken.is_revoked.is_(False),
        ).first()

        if not stored_refresh:
            raise ValueError("Token not recognized")

        stored_refresh.is_revoked = True

        # Persist the change to the database
        self.db.commit()

        # Return a simple confirmation message
        return {"message": "Logged out successfully"}