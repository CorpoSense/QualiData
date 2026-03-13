"""Authentication routes."""

from datetime import datetime, timedelta

import os
from fastapi import APIRouter, Depends, HTTPException, status
import os
from fastapi import Form
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel, EmailStr
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.db.database import get_async_session
from app.db.models import User

settings = get_settings()
router = APIRouter(prefix="/auth", tags=["auth"])

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

# JWT settings
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7  # 7 days


# Pydantic schemas
class UserCreate(BaseModel):
    email: EmailStr
    password: str
    full_name: str | None = None


class UserResponse(BaseModel):
    id: str
    email: str
    name: str | None
    role: str
    is_active: bool
    is_verified: bool
    created_at: datetime | None

    model_config = {"from_attributes": True}


class Token(BaseModel):
    access_token: str
    token_type: str


class PasswordResetRequest(BaseModel):
    email: EmailStr


class PasswordResetConfirm(BaseModel):
    token: str
    new_password: str


class TokenData(BaseModel):
    email: str | None = None


# Utility functions
def verify_password(plain_password: str, password_hash: str) -> bool:
    import hashlib
    try:
        # Try passlib first (bcrypt)
        return pwd_context.verify(plain_password, password_hash)
    except Exception:
        # Fallback: check sha256
        return hashlib.sha256(plain_password.encode()).hexdigest() == password_hash


def get_password_hash(password: str) -> str:
    import hashlib
    return hashlib.sha256(password.encode()).hexdigest()


def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    session: AsyncSession = Depends(get_async_session),
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
        token_data = TokenData(email=email)
    except JWTError:
        raise credentials_exception

    result = await session.execute(select(User).where(User.email == token_data.email))
    user = result.scalar_one_or_none()
    if user is None:
        raise credentials_exception
    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


# Routes
@router.post(
    "/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED
)
async def register(
    email: str = Form(...),
    password: str = Form(...),
    full_name: str | None = Form(None),
    session: AsyncSession = Depends(get_async_session)
):
    """Register a new user."""
    # Check if user exists
    result = await session.execute(select(User).where(User.email == email))
    existing_user = result.scalar_one_or_none()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered"
        )

    # Check if any users exist (first user becomes admin)
    result = await session.execute(select(User))
    user_count = len(result.scalars().all())
    
    # Determine user role: first user becomes admin
    user_role = "user"  # Default role
    if user_count == 0:
        user_role = "admin"
        # Also check if admin env vars were set (they would have created admin on startup)
        admin_email = os.environ.get("ADMIN_USER", "").strip()
        if admin_email and admin_email.lower() != email.lower():
            # Admin already created via env, this is not first user
            user_role = "user"

    # Create new user with enum role
    from app.db.models import UserRole
    password_hash = get_password_hash(password)
    new_user = User(
        email=email,
        password_hash=password_hash,
        name=full_name,
        role=UserRole(user_role),
        is_active=True,
    )
    session.add(new_user)
    await session.commit()
    await session.refresh(new_user)

    return new_user


@router.post("/login", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    session: AsyncSession = Depends(get_async_session),
):
    """Login and get access token."""
    result = await session.execute(select(User).where(User.email == form_data.username))
    user = result.scalar_one_or_none()

    if not user or not verify_password(form_data.password, user.password_hash or ""):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user"
        )

    # Update last login
    user.last_login = datetime.utcnow()
    await session.commit()

    # Create access token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )

    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/debug-login", response_model=Token)
async def debug_login(session: AsyncSession = Depends(get_async_session)):
    """Debug login - only works when DEBUG=true. Returns token for first user (admin)."""
    settings = get_settings()
    if not settings.debug:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Debug login is disabled",
        )

    # Get first user (admin)
    result = await session.execute(select(User).order_by(User.id).limit(1))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No users found",
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="User is inactive"
        )

    # Update last login
    user.last_login = datetime.utcnow()
    await session.commit()

    # Create access token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )

    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/me", response_model=UserResponse)
async def read_users_me(current_user: User = Depends(get_current_active_user)):
    """Get current user info."""
    return current_user


# In-memory store for password reset tokens (use Redis in production)
password_reset_tokens: dict = {}


@router.post("/password-reset-request")
async def request_password_reset(
    request: PasswordResetRequest, session: AsyncSession = Depends(get_async_session)
):
    """Request password reset - sends email with reset token."""
    result = await session.execute(select(User).where(User.email == request.email))
    user = result.scalar_one_or_none()

    # Always return success to prevent email enumeration
    # In production, you'd send an actual email

    if user:
        # Generate reset token
        reset_token = jwt.encode(
            {"sub": user.email, "type": "password_reset"},
            settings.SECRET_KEY,
            algorithm=ALGORITHM,
        )
        password_reset_tokens[reset_token] = user.id

        # In production, send email with reset link:
        # reset_link = f"{settings.FRONTEND_URL}/reset-password?token={reset_token}"
        # await send_email(user.email, "Password Reset", f"Click here: {reset_link}")
        print(f"Password reset token for {user.email}: {reset_token}")

    return {"message": "If the email exists, a password reset link has been sent"}


@router.post("/password-reset-confirm")
async def confirm_password_reset(
    request: PasswordResetConfirm, session: AsyncSession = Depends(get_async_session)
):
    """Confirm password reset with token and new password."""
    try:
        payload = jwt.decode(request.token, settings.SECRET_KEY, algorithms=[ALGORITHM])
        if payload.get("type") != "password_reset":
            raise HTTPException(status_code=400, detail="Invalid token")

        email = payload.get("sub")
    except JWTError:
        raise HTTPException(status_code=400, detail="Invalid or expired token")

    # Find user
    result = await session.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Update password
    user.password_hash = get_password_hash(request.new_password)
    await session.commit()

    # Clean up token
    if request.token in password_reset_tokens:
        del password_reset_tokens[request.token]

    return {"message": "Password reset successful"}


# OAuth Routes


@router.get("/oauth/{provider}")
async def oauth_redirect(provider: str):
    """Redirect to OAuth provider."""
    if provider == "google":
        redirect_uri = f"{settings.frontend_url}/oauth/callback/google"
        auth_url = (
            "https://accounts.google.com/o/oauth2/v2/auth?"
            f"client_id={settings.google_client_id or ''}&"
            f"redirect_uri={redirect_uri}&"
            "response_type=code&"
            "scope=openid email profile"
        )
    elif provider == "github":
        redirect_uri = f"{settings.frontend_url}/oauth/callback/github"
        auth_url = (
            f"https://github.com/login/oauth/authorize?"
            f"client_id={settings.github_client_id or ''}&"
            f"redirect_uri={redirect_uri}&"
            "scope=read:user user:email"
        )
    else:
        raise HTTPException(status_code=400, detail="Unsupported provider")

    return {"auth_url": auth_url}


@router.get("/oauth/callback/{provider}", response_model=Token)
async def oauth_callback(
    provider: str, code: str, session: AsyncSession = Depends(get_async_session)
):
    """Handle OAuth callback and return JWT token."""
    if provider == "google":
        # Exchange code for token
        import httpx

        token_res = await httpx.AsyncClient().post(
            "https://oauth2.googleapis.com/token",
            data={
                "client_id": settings.google_client_id or "",
                "client_secret": settings.google_client_secret or "",
                "code": code,
                "grant_type": "authorization_code",
                "redirect_uri": f"{settings.frontend_url}/oauth/callback/google",
            },
        )
        if token_res.status_code != 200:
            raise HTTPException(status_code=400, detail="Failed to exchange code")

        access_token = token_res.json().get("access_token")

        # Get user info
        user_res = await httpx.AsyncClient().get(
            "https://www.googleapis.com/oauth2/v2/userinfo",
            headers={"Authorization": f"Bearer {access_token}"},
        )
        user_data = user_res.json()
        email = user_data.get("email")
        name = user_data.get("name")

    elif provider == "github":
        import httpx

        # Exchange code for token
        token_res = await httpx.AsyncClient().post(
            "https://github.com/login/oauth/access_token",
            data={
                "client_id": settings.github_client_id or "",
                "client_secret": settings.github_client_secret or "",
                "code": code,
            },
            headers={"Accept": "application/json"},
        )
        if token_res.status_code != 200:
            raise HTTPException(status_code=400, detail="Failed to exchange code")

        access_token = token_res.json().get("access_token")

        # Get user info
        user_res = await httpx.AsyncClient().get(
            "https://api.github.com/user",
            headers={"Authorization": f"Bearer {access_token}"},
        )
        user_data = user_res.json()
        email = user_data.get("email")
        name = user_data.get("name")

        # Get email if not public
        if not email:
            email_res = await httpx.AsyncClient().get(
                "https://api.github.com/user/emails",
                headers={"Authorization": f"Bearer {access_token}"},
            )
            emails = email_res.json()
            primary = next((e for e in emails if e.get("primary")), None)
            email = primary.get("email") if primary else emails[0].get("email")
    else:
        raise HTTPException(status_code=400, detail="Unsupported provider")

    # Find or create user
    result = await session.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()

    if not user:
        # Create new user
        user = User(
            email=email,
            password_hash=get_password_hash(None),  # No password for OAuth
            full_name=name,
            is_active=True,
        )
        session.add(user)
        await session.commit()
        await session.refresh(user)

    # Generate JWT
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )

    return {"access_token": access_token, "token_type": "bearer"}
