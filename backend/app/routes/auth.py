"""
Authentication Routes - FastAPI Implementation
JWT-based authentication with OAuth2 password flow
"""

from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.extensions import get_db
from app.models import User

router = APIRouter()

# OAuth2 scheme for Bearer token authentication
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


# Pydantic Schemas (used for request validation + auto OpenAPI docs)
class RegisterSchema(BaseModel):
    email: EmailStr
    username: str = Field(min_length=3, max_length=80)
    password: str = Field(min_length=8, max_length=128)


class LoginSchema(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    message: str
    user: dict
    access_token: str


# Dependency: Get current user from JWT token
async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db)
) -> User:
    """
    Validate JWT token and return current user.
    
    Raises:
        401: If token is invalid or expired
        404: If user not found
    """
    from jose import jwt, JWTError
    
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        # Decode JWT token
        payload = jwt.decode(
            token,
            "jwt-dev-secret-change-me-min-32-chars-long",  # TODO: Use settings.JWT_SECRET_KEY
            algorithms=["HS256"]
        )
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    # Fetch user from database
    result = await db.execute(select(User).where(User.id == int(user_id)))
    user = result.scalar_one_or_none()
    
    if user is None:
        raise credentials_exception
    
    return user


@router.post("/register", response_model=TokenResponse, status_code=201)
async def register(
    data: RegisterSchema,
    db: AsyncSession = Depends(get_db)
):
    """Register a new user account"""
    # Check for existing user
    result = await db.execute(
        select(User).where((User.email == data.email) | (User.username == data.username))
    )
    existing = result.scalar_one_or_none()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email or username already exists"
        )
    
    # Create new user
    user = User(email=data.email, username=data.username)
    user.set_password(data.password)
    
    db.add(user)
    await db.commit()
    await db.refresh(user)
    
    # Generate JWT token
    from jose import jwt
    access_token = jwt.encode({"sub": str(user.id)}, "jwt-dev-secret-change-me-min-32-chars-long", algorithm="HS256")
    
    return TokenResponse(
        message="User created successfully",
        user=user.to_dict(),
        access_token=access_token
    )


@router.post("/login", response_model=TokenResponse)
async def login(
    data: LoginSchema,
    db: AsyncSession = Depends(get_db)
):
    """Authenticate user and return JWT token"""
    # Find user by email
    result = await db.execute(select(User).where(User.email == data.email))
    user = result.scalar_one_or_none()
    
    # Validate credentials
    if not user or not user.check_password(data.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is disabled"
        )
    
    # Generate JWT token
    from jose import jwt
    access_token = jwt.encode({"sub": str(user.id)}, "jwt-dev-secret-change-me-min-32-chars-long", algorithm="HS256")
    
    return TokenResponse(
        message="Login successful",
        user=user.to_dict(),
        access_token=access_token
    )


@router.get("/me")
async def get_me(current_user: User = Depends(get_current_user)):
    """Get current authenticated user profile"""
    return current_user.to_dict()
