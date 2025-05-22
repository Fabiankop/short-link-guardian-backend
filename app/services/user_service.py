from app.db.models.user import User
from app.schemas.user import (
    UserCreate, UserUpdate, UserOut
)
from app.core.security import hash_password, verify_password, create_access_token
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import Optional
import secrets
from app.services.email_service import send_email_background

# Email/SMS stubs
async def send_verification_email(email: str, token: str):
    subject = "Verify your email"
    body = f"Click the link to verify: https://yourdomain.com/verify?token={token}"
    await send_email_background(email, subject, body)

async def send_password_reset_email(email: str, token: str):
    subject = "Reset your password"
    body = f"Click the link to reset: https://yourdomain.com/reset?token={token}"
    await send_email_background(email, subject, body)

async def send_sms(phone: str, message: str):
    # Integración real: Twilio
    print(f"[Twilio] Send SMS to {phone}: {message}")

# CRUD y lógica de usuario
async def get_user_by_email(session: AsyncSession, email: str) -> Optional[User]:
    result = await session.execute(select(User).where(User.email == email))
    return result.scalars().first()

async def get_user_by_id(session: AsyncSession, user_id: int) -> Optional[User]:
    result = await session.execute(select(User).where(User.id == user_id))
    return result.scalars().first()

async def create_user(session: AsyncSession, user_in: UserCreate) -> UserOut:
    hashed = hash_password(user_in.password)
    token = secrets.token_urlsafe(32)
    user = User(
        email=user_in.email,
        hashed_password=hashed,
        is_active=True,
        is_verified=False,
        verification_token=token,
        role=user_in.role or "user",
    )
    session.add(user)
    await session.commit()
    await session.refresh(user)
    await send_verification_email(user.email, token)
    return UserOut.model_validate(user)

async def authenticate_user(session: AsyncSession, email: str, password: str) -> Optional[str]:
    user = await get_user_by_email(session, email)
    if not user or not verify_password(password, user.hashed_password):
        return None
    if not user.is_active:
        return None
    access_token = create_access_token({"sub": str(user.id), "role": user.role})
    return access_token

async def update_user(session: AsyncSession, user: User, user_in: UserUpdate) -> UserOut:
    for field, value in user_in.model_dump(exclude_unset=True).items():
        setattr(user, field, value)
    await session.commit()
    await session.refresh(user)
    return UserOut.model_validate(user)

async def initiate_password_reset(session: AsyncSession, email: str):
    user = await get_user_by_email(session, email)
    if not user:
        return
    token = secrets.token_urlsafe(32)
    user.reset_token = token
    await session.commit()
    await send_password_reset_email(user.email, token)

async def confirm_password_reset(session: AsyncSession, token: str, new_password: str):
    result = await session.execute(select(User).where(User.reset_token == token))
    user = result.scalars().first()
    if not user:
        return False
    user.hashed_password = hash_password(new_password)
    user.reset_token = None
    await session.commit()
    return True

async def initiate_email_verification(session: AsyncSession, email: str):
    user = await get_user_by_email(session, email)
    if not user:
        return
    token = secrets.token_urlsafe(32)
    user.verification_token = token
    await session.commit()
    await send_verification_email(user.email, token)

async def confirm_email_verification(session: AsyncSession, token: str):
    result = await session.execute(select(User).where(User.verification_token == token))
    user = result.scalars().first()
    if not user:
        return False
    user.is_verified = True
    user.verification_token = None
    await session.commit()
    return True

# Protección por rol
def has_role(user: User, role: str) -> bool:
    return user.role == role or user.is_superuser
