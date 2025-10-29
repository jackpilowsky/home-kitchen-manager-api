from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from jose.exceptions import ExpiredSignatureError
from passlib.context import CryptContext
from datetime import datetime, timedelta
from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from config import SECRET_KEY, ALGORITHM
from api.v1.models import User
from api.v1.database import get_db
from api.v1.exceptions import (
    InvalidCredentialsException,
    TokenExpiredException,
    InvalidTokenException,
    InactiveUserException,
    UserNotFoundException,
    DuplicateUsernameException,
    DuplicateEmailException,
    DatabaseException
)

# --- Auth setup ---
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# --- Auth helpers ---
def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain password against its hash"""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Hash a password"""
    return pwd_context.hash(password)

def authenticate_user(username: str, password: str, db: Session) -> Optional[User]:
    """Authenticate a user by username and password"""
    user = db.query(User).filter(User.username == username).first()
    if not user:
        return None
    if not user.is_active:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create a JWT access token"""
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def create_user(username: str, email: str, password: str, db: Session, **kwargs) -> User:
    """Create a new user"""
    try:
        hashed_password = get_password_hash(password)
        user = User(
            username=username,
            email=email,
            hashed_password=hashed_password,
            **kwargs
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        return user
    except IntegrityError as e:
        db.rollback()
        error_msg = str(e.orig) if hasattr(e, 'orig') else str(e)
        
        if "username" in error_msg.lower():
            raise DuplicateUsernameException(username)
        elif "email" in error_msg.lower():
            raise DuplicateEmailException(email)
        else:
            raise DatabaseException("Failed to create user", operation="create_user")
    except Exception as e:
        db.rollback()
        raise DatabaseException(f"Unexpected error creating user: {str(e)}", operation="create_user")

# --- Auth dependency ---
async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    """Get the current authenticated user from JWT token"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise InvalidTokenException("Missing user identifier")
    except ExpiredSignatureError:
        raise TokenExpiredException()
    except JWTError as e:
        raise InvalidTokenException(str(e))
    
    user = db.query(User).filter(User.username == username).first()
    if user is None:
        raise UserNotFoundException(username)
    if not user.is_active:
        raise InactiveUserException()
    return user

async def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    """Get the current active user"""
    if not current_user.is_active:
        raise InactiveUserException()
    return current_user