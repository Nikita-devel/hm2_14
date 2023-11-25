from typing import Optional
import pickle

import redis.asyncio as redis
from jose import JWTError, jwt
from fastapi import HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from src.db.db_connect import get_db
from src.repository import users as repository_users
from src.conf.config import settings


class Auth:
    """
    Authentication service class for handling user authentication and authorization.

    Attributes:
        pwd_context (CryptContext): The password hashing context.
        SECRET_KEY (str): The secret key used for token encryption.
        ALGORITHM (str): The encryption algorithm used for token encoding.
        oauth2_scheme (OAuth2PasswordBearer): The OAuth2 password bearer scheme.
        r (redis.Redis): The Redis client for caching user data.
    """

    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    SECRET_KEY = settings.secret_key
    ALGORITHM = settings.algorithm
    oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")
    r = redis.Redis(host=settings.redis_host, port=settings.redis_port, db=0)

    def verify_password(self, plain_password, hashed_password):
        """
        Verify a plaintext password against a hashed password

        Args:
            plain_password (str): The plaintext password.
            hashed_password (str): The hashed password

        Returns:
            bool: True if the passwords match, False otherwise.
        """
        return self.pwd_context.verify(plain_password, hashed_password)

    def get_password_hash(self, password: str):
        """
        Generate a password hash for a given plaintext password

        Args:
            password (str): The plaintext password

        Returns:
            str: The hashed password.
        """
        return self.pwd_context.hash(password)

    async def create_access_token(self, data: dict, expires_delta: Optional[float] = None):
        """
        Create an access token

        Args:
            data (dict): The data to include in the token payload.
            expires_delta (float, optional): The token expiration time in seconds

        Returns:
            str: The encoded access token.
        """
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + timedelta(seconds=expires_delta)
        else:
            expire = datetime.utcnow() + timedelta(minutes=15)
        to_encode.update({"iat": datetime.utcnow(), "exp": expire, "scope": "access_token"})
        encoded_access_token = jwt.encode(to_encode, self.SECRET_KEY, algorithm=self.ALGORITHM)
        return encoded_access_token

    async def create_refresh_token(self, data: dict, expires_delta: Optional[float] = None):
        """
        Create a refresh token

        Args:
            data (dict): The data to include in the token payload.
            expires_delta (float, optional): The token expiration time in seconds

        Returns:
            str: The encoded refresh token.
        """
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + timedelta(seconds=expires_delta)
        else:
            expire = datetime.utcnow() + timedelta(days=7)
        to_encode.update({"iat": datetime.utcnow(), "exp": expire, "scope": "refresh_token"})
        encoded_refresh_token = jwt.encode(to_encode, self.SECRET_KEY, algorithm=self.ALGORITHM)
        return encoded_refresh_token

    async def decode_refresh_token(self, refresh_token: str):
        """
        Decode and validate a refresh token

        Args:
            refresh_token (str): The refresh token to decode

        Returns:
            str: The email associated with the token

        Raises:
            HTTPException: If the token is invalid or has an invalid scope.
        """
        try:
            payload = jwt.decode(refresh_token, self.SECRET_KEY, algorithms=[self.ALGORITHM])
            if payload['scope'] == 'refresh_token':
                email = payload['sub']
                return email
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid scope for token')
        except JWTError:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Could not validate credentials')

    async def get_current_user(self, token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
        """
        Get the current user based on the access token

        Args:
            token (str): The access token to decode.
            db (Session): The database session

        Returns:
            User: The current user

        Raises:
            HTTPException: If the token is invalid or the user cannot be found.
        """
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

        try:
            payload = jwt.decode(token, self.SECRET_KEY, algorithms=[self.ALGORITHM])
            if payload['scope'] == 'access_token':
                email = payload["sub"]
                if email is None:
                    raise credentials_exception
            else:
                raise credentials_exception
        except JWTError as e:
            raise credentials_exception
        user = await self.r.get(f"user:{email}")
        if user is None:
            user = await repository_users.get_user_by_email(email, db)
            if user is None:
                raise credentials_exception
            await self.r.set(f"user:{email}", pickle.dumps(user))
            await self.r.expire(f"user:{email}", 900)
        else:
            user = pickle.loads(user)
        return user

    def create_email_token(self, data: dict):
        """
        Create an email verification token

        Args:
            data (dict): The data to include in the token payload

        Returns:
            str: The encoded email verification token.
        """
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(days=2)
        to_encode.update({"iat": datetime.utcnow(), "exp": expire})
        token = jwt.encode(to_encode, self.SECRET_KEY, algorithm=self.ALGORITHM)
        return token

    async def get_email_from_token(self, token: str):
        """
        Get the email associated with an email verification token

        Args:
            token (str): The email verification token to decode

        Returns:
            str: The email address

        Raises:
            HTTPException: If the token is invalid.
        """
        try:
            payload = jwt.decode(token, self.SECRET_KEY, algorithms=[self.ALGORITHM])
            email = payload["sub"]
            return email
        except JWTError as e:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                                detail="Invalid token for email verification")


auth_service = Auth()
