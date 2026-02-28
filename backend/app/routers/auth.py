"""Authentication routes."""

from datetime import datetime, timedelta
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
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
    full_name: Optional[str] = None


class UserResponse(BaseModel):
    id: int
    email: str
    full_name: Optional[str]
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str


class PasswordResetRequest(BaseModel):
    email: EmailStr


class PasswordResetConfirm(BaseModel):
    token: str
    new_password: str


class TokenData(BaseModel):
    email: Optional[str] = None


# Utility functions
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
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
    session: AsyncSession = Depends(get_async_session)
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

    result = await session.execute(
        select(User).where(User.email == token_data.email)
    )
    user = result.scalar_one_or_none()
    if user is None:
        raise credentials_exception
    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


# Routes
@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserCreate, session: AsyncSession = Depends(get_async_session)):
    """Register a new user."""
    # Check if user exists
    result = await session.execute(
        select(User).where(User.email == user_data.email)
    )
    existing_user = result.scalar_one_or_none()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    # Create new user
    hashed_password = get_password_hash(user_data.password)
    new_user = User(
        email=user_data.email,
        hashed_password=hashed_password,
        full_name=user_data.full_name,
        is_active=True,
    )
    session.add(new_user)
    await session.commit()
    await session.refresh(new_user)

    return new_user


@router.post("/login", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    session: AsyncSession = Depends(get_async_session)
):
    """Login and get access token."""
    result = await session.execute(
        select(User).where(User.email == form_data.username)
    )
    user = result.scalar_one_or_none()

    if not user or not verify_password(form_data.password, user.hashed_password or ""):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
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
    request: PasswordResetRequest,
    session: AsyncSession = Depends(get_async_session)
):
    """Request password reset - sends email with reset token."""
    result = await session.execute(
        select(User).where(User.email == request.email)
    )
    user = result.scalar_one_or_none()

    # Always return success to prevent email enumeration
    # In production, you'd send an actual email

    if user:
        # Generate reset token
        reset_token = jwt.encode(
            {"sub": user.email, "type": "password_reset"},
            settings.SECRET_KEY,
            algorithm=ALGORITHM
        )
        password_reset_tokens[reset_token] = user.id

        # In production, send email with reset link:
        # reset_link = f"{settings.FRONTEND_URL}/reset-password?token={reset_token}"
        # await send_email(user.email, "Password Reset", f"Click here: {reset_link}")
        print(f"Password reset token for {user.email}: {reset_token}")

    return {"message": "If the email exists, a password reset link has been sent"}


@router.post("/password-reset-confirm")
async def confirm_password_reset(
    request: PasswordResetConfirm,
    session: AsyncSession = Depends(get_async_session)
):
    """Confirm password reset with token and new password."""
    try:
        payload = jwt.decode(
            request.token,
            settings.SECRET_KEY,
            algorithms=[ALGORITHM]
        )
        if payload.get("type") != "password_reset":
            raise HTTPException(status_code=400, detail="Invalid token")

        email = payload.get("sub")
    except JWTError:
        raise HTTPException(status_code=400, detail="Invalid or expired token")

    # Find user
    result = await session.execute(
        select(User).where(User.email == email)
    )
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Update password
    user.hashed_password = get_password_hash(request.new_password)
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
        redirect_uri = f"{settings.cors_origins[0]}/oauth/callback/google"
        auth_url = (
            "https://accounts.google.com/o/oauth2/v2/auth?"
            f"client_id={settings.google_client_id or ''}&"
            f"redirect_uri={redirect_uri}&"
            "response_type=code&"
            "scope=openid email profile"
        )
    elif provider == "github":
        redirect_uri = f"{settings.cors_origins[0]}/oauth/callback/github"
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
    provider: str,
    code: str,
    session: AsyncSession = Depends(get_async_session)
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
                "redirect_uri": f"{settings.cors_origins[0]}/oauth/callback/google"
            }
        )
        if token_res.status_code != 200:
            raise HTTPException(status_code=400, detail="Failed to exchange code")

        access_token = token_res.json().get("access_token")

        # Get user info
        user_res = await httpx.AsyncClient().get(
            "https://www.googleapis.com/oauth2/v2/userinfo",
            headers={"Authorization": f"Bearer {access_token}"}
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
                "code": code
            },
            headers={"Accept": "application/json"}
        )
        if token_res.status_code != 200:
            raise HTTPException(status_code=400, detail="Failed to exchange code")

        access_token = token_res.json().get("access_token")

        # Get user info
        user_res = await httpx.AsyncClient().get(
            "https://api.github.com/user",
            headers={"Authorization": f"Bearer {access_token}"}
        )
        user_data = user_res.json()
        email = user_data.get("email")
        name = user_data.get("name")

        # Get email if not public
        if not email:
            email_res = await httpx.AsyncClient().get(
                "https://api.github.com/user/emails",
                headers={"Authorization": f"Bearer {access_token}"}
            )
            emails = email_res.json()
            primary = next((e for e in emails if e.get("primary")), None)
            email = primary.get("email") if primary else emails[0].get("email")
    else:
        raise HTTPException(status_code=400, detail="Unsupported provider")

    # Find or create user
    result = await session.execute(
        select(User).where(User.email == email)
    )
    user = result.scalar_one_or_none()

    if not user:
        # Create new user
        user = User(
            email=email,
            hashed_password=get_password_hash(None),  # No password for OAuth
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
