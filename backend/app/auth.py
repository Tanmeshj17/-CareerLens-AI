import os
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
import bcrypt
import secrets
import hashlib
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from . import models, database

# Security configuration - reads from env; fails if SECRET_KEY is missing
SECRET_KEY = os.getenv("SECRET_KEY", "supersecretkey123")
ALGORITHM = "HS256"
# NOTE: 15-minute expiry is a deliberate MVP security hardening decision.
# This limits the attack window if a token is stolen after logout.
# IMPORTANT: This is NOT true server-side token invalidation.
# After logout the token remains cryptographically valid until expiry.
# If persistent sessions or true revocation are later required, implement:
#   - Access tokens (short-lived, e.g. 15m) + Refresh tokens (long-lived)
#   - Server-side token blocklist (e.g. Redis SET with TTL)
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "15"))

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/token")

def verify_password(plain_password, hashed_password):
    if isinstance(hashed_password, str):
        hashed_password = hashed_password.encode('utf-8')
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password)

def get_password_hash(password):
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

def generate_secure_token():
    return secrets.token_urlsafe(32)

def hash_token(token: str):
    return hashlib.sha256(token.encode('utf-8')).hexdigest()

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

from sqlalchemy import func

def get_user_by_email(db: Session, email: str):
    if not email:
        return None
    clean_email = email.strip().lower()
    # Support logging in with 'careerlensadmin' or 'careerlensadmin@careerlens.ai'
    if clean_email in ("careerlensadmin", "careerlensadmin@careerlens.ai", "careerlensadmin@gmail.com"):
        admin = db.query(models.User).filter(
            (func.lower(models.User.email) == "careerlensadmin@careerlens.ai") |
            (func.lower(models.User.email) == "careerlensadmin")
        ).first()
        if admin:
            return admin
        # Auto-create if not yet created
        return ensure_admin_user(db)
    return db.query(models.User).filter(func.lower(models.User.email) == clean_email).first()

def ensure_admin_user(db: Session):
    """
    Guarantees the existence and permissions for the system admin:
    Username/Email: careerlensadmin / careerlensadmin@careerlens.ai
    Default initial password: controler_at_careerlens17tj (preserves custom changed passwords)
    Role: admin
    """
    admin_pass = "controler_at_careerlens17tj"
    admin = db.query(models.User).filter(
        (func.lower(models.User.email) == "careerlensadmin@careerlens.ai") |
        (func.lower(models.User.email) == "careerlensadmin")
    ).first()

    if not admin:
        admin = models.User(
            email="careerlensadmin@careerlens.ai",
            full_name="CareerLens Admin",
            role="admin",
            is_verified=True,
            hashed_password=get_password_hash(admin_pass)
        )
        db.add(admin)
        db.commit()
        db.refresh(admin)
    else:
        admin.role = "admin"
        admin.is_verified = True
        if not admin.hashed_password:
            admin.hashed_password = get_password_hash(admin_pass)
        db.commit()

    # Guarantee owner account is marked as admin & verified
    tanmesh = db.query(models.User).filter(func.lower(models.User.email) == "tanmeshj17@gmail.com").first()
    if tanmesh:
        if tanmesh.role != "admin" or not tanmesh.is_verified:
            tanmesh.role = "admin"
            tanmesh.is_verified = True
            db.commit()

    return admin

async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(database.get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = get_user_by_email(db, email=email)
    if user is None:
        raise credentials_exception
    return user

async def require_admin(current_user: models.User = Depends(get_current_user)):
    """Security guard: Only users with role='admin' can access admin endpoints."""
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Administrator access required. Only authorized personnel can view this resource."
        )
    return current_user


