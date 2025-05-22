from fastapi import APIRouter, Depends, status, HTTPException, Query, Request
from app.schemas.user import (
    UserCreate, UserOut, PasswordResetRequest, PasswordResetConfirm, EmailVerificationRequest, EmailVerificationConfirm, UserUpdate
)
from app.services.user_service import (
    create_user, authenticate_user, get_user_by_id, update_user,
    initiate_password_reset, confirm_password_reset, initiate_email_verification, confirm_email_verification, has_role
)
from app.api.deps import get_current_user
from fastapi.security import OAuth2PasswordRequestForm
from app.core.config import get_settings
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_session
from app.core.i18n import get_translations
from sqlalchemy import select

router = APIRouter()
settings = get_settings()

# Rate limiting: 100 req/h global, 20 req/min per user
@router.post("/register", response_model=UserOut, status_code=status.HTTP_201_CREATED)
async def register(user_in: UserCreate, session: AsyncSession = Depends(get_session)):
    user = await create_user(session, user_in)
    return user

def get_locale(request: Request) -> str:
    return request.headers.get("accept-language", "en").split(",")[0][:2]

@router.post("/login")
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    session: AsyncSession = Depends(get_session),
    request: Request = None
):
    locale = get_locale(request)
    _ = get_translations(locale).gettext
    token = await authenticate_user(session, form_data.username, form_data.password)
    if not token:
        raise HTTPException(status_code=400, detail=_("Invalid credentials"))
    return {"access_token": token, "token_type": "bearer"}

@router.get("/me", response_model=UserOut)
async def read_users_me(current_user = Depends(get_current_user)):
    return UserOut.model_validate(current_user)

@router.post("/password-reset/request")
async def password_reset_request(data: PasswordResetRequest, session: AsyncSession = Depends(get_session), request: Request = None):
    locale = get_locale(request)
    _ = get_translations(locale).gettext
    await initiate_password_reset(session, data.email)
    return {"msg": _("If the email exists, a reset link has been sent.")}

@router.post("/password-reset/confirm")
async def password_reset_confirm(data: PasswordResetConfirm, session: AsyncSession = Depends(get_session), request: Request = None):
    locale = get_locale(request)
    _ = get_translations(locale).gettext
    ok = await confirm_password_reset(session, data.token, data.new_password)
    if not ok:
        raise HTTPException(status_code=400, detail=_("Invalid or expired token"))
    return {"msg": _("Password updated")}

@router.post("/email-verification/request")
async def email_verification_request(data: EmailVerificationRequest, session: AsyncSession = Depends(get_session), request: Request = None):
    locale = get_locale(request)
    _ = get_translations(locale).gettext
    await initiate_email_verification(session, data.email)
    return {"msg": _("If the email exists, a verification link has been sent.")}

@router.post("/email-verification/confirm")
async def email_verification_confirm(data: EmailVerificationConfirm, session: AsyncSession = Depends(get_session), request: Request = None):
    locale = get_locale(request)
    _ = get_translations(locale).gettext
    ok = await confirm_email_verification(session, data.token)
    if not ok:
        raise HTTPException(status_code=400, detail=_("Invalid or expired token"))
    return {"msg": _("Email verified")}

@router.get("/", response_model=list[UserOut])
async def list_users(
    skip: int = 0,
    limit: int = Query(10, le=100),
    email: str | None = None,
    role: str | None = None,
    current_user = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
    request: Request = None
):
    locale = get_locale(request)
    _ = get_translations(locale).gettext
    if not has_role(current_user, "admin"):
        raise HTTPException(status_code=403, detail=_("Not enough permissions"))
    query = select(type(current_user))
    if email:
        query = query.where(type(current_user).email == email)
    if role:
        query = query.where(type(current_user).role == role)
    query = query.offset(skip).limit(limit)
    result = await session.execute(query)
    users = result.scalars().all()
    return [UserOut.model_validate(u) for u in users]

@router.patch("/{user_id}", response_model=UserOut)
async def update_user_route(
    user_id: int,
    user_in: UserUpdate,
    current_user = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
    request: Request = None
):
    locale = get_locale(request)
    _ = get_translations(locale).gettext
    user = await get_user_by_id(session, user_id)
    if not user:
        raise HTTPException(status_code=404, detail=_("User not found"))
    if not has_role(current_user, "admin") and current_user.id != user_id:
        raise HTTPException(status_code=403, detail=_("Not enough permissions"))
    return await update_user(session, user, user_in)
