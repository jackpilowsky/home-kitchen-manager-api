from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from jose.exceptions import ExpiredSignatureError
from passlib.context import CryptContext
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from config import SECRET_KEY, ALGORITHM
from api.v1.models import User
from api.v1.database import get_db

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

def authenticate_user(username: str, password: str, db: Session) -> User | None:
    """Authenticate a user by username and password"""
    user = db.query(User).filter(User.username == username).first()
    if not user:
        return None
    if not user.is_active:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user

def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    """Create a JWT access token"""
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def create_user(username: str, email: str, password: str, db: Session, **kwargs) -> User:
    """Create a new user"""
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

# --- Auth dependency ---
async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    """Get the current authenticated user from JWT token"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except JWTError:
        raise credentials_exception
    
    user = db.query(User).filter(User.username == username).first()
    if user is None:
        raise credentials_exception
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Inactive user",
        )
    return user

async def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    """Get the current active user"""
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user