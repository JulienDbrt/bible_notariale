from fastapi import APIRouter, HTTPException, Depends, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, EmailStr
from typing import Optional, Dict, Any
import jwt
import uuid
from datetime import datetime

from ..core.database import get_supabase_client
from ..models.schemas import UserResponse, UserCreate, APIResponse

router = APIRouter(prefix="/auth", tags=["authentication"])
security = HTTPBearer()

class SignUpRequest(BaseModel):
    email: EmailStr
    password: str
    full_name: Optional[str] = None

class SignInRequest(BaseModel):
    email: EmailStr
    password: str

class AuthResponse(BaseModel):
    user: UserResponse
    access_token: str
    refresh_token: str

class TokenRefreshRequest(BaseModel):
    refresh_token: str

@router.post("/signup", response_model=AuthResponse)
async def sign_up(
    request: SignUpRequest,
    supabase: Any = Depends(get_supabase_client)
) -> AuthResponse:
    """Sign up a new user"""
    try:
        # Sign up with Supabase Auth - bypass email confirmation
        auth_response = supabase.auth.sign_up({
            "email": request.email,
            "password": request.password,
            "options": {
                "data": {
                    "full_name": request.full_name
                },
                "email_confirm": True  # Require email confirmation
            }
        })
        
        if auth_response.user is None:
            raise HTTPException(
                status_code=400, 
                detail="Failed to create user. Email might already be registered."
            )
        
        # Create user record in our users table
        user_data = {
            "id": auth_response.user.id,
            "email": request.email,
            "full_name": request.full_name,
            "created_date": datetime.utcnow().isoformat(),
            "is_active": True,
            "is_admin": False  # Par défaut, les nouveaux utilisateurs ne sont pas admin
        }
        
        # Insert user into our users table
        user_result = supabase.table("users").insert(user_data).execute()
        if not user_result.data:
            raise HTTPException(status_code=500, detail="Failed to create user profile")
        
        user_response = UserResponse(**user_result.data[0])
        
        return AuthResponse(
            user=user_response,
            access_token=auth_response.session.access_token if auth_response.session else "",
            refresh_token=auth_response.session.refresh_token if auth_response.session else ""
        )
        
    except Exception as e:
        error_msg = str(e)
        if "duplicate key" in error_msg.lower():
            raise HTTPException(status_code=400, detail="Email already registered")
        raise HTTPException(status_code=500, detail=f"Authentication error: {error_msg}")

@router.post("/signin", response_model=AuthResponse)
async def sign_in(
    request: SignInRequest,
    supabase: Any = Depends(get_supabase_client)
) -> AuthResponse:
    """Sign in user"""
    try:
        # Sign in with Supabase Auth
        auth_response = supabase.auth.sign_in_with_password({
            "email": request.email,
            "password": request.password
        })
        
        if auth_response.user is None:
            raise HTTPException(status_code=401, detail="Invalid credentials")
        
        # Get user from our users table
        user_result = supabase.table("users").select("*").eq("id", auth_response.user.id).execute()
        if not user_result.data:
            raise HTTPException(status_code=404, detail="User profile not found")
        
        # Update last login
        supabase.table("users").update({
            "last_login": datetime.utcnow().isoformat()
        }).eq("id", auth_response.user.id).execute()
        
        user_response = UserResponse(**user_result.data[0])
        
        return AuthResponse(
            user=user_response,
            access_token=auth_response.session.access_token if auth_response.session else "",
            refresh_token=auth_response.session.refresh_token if auth_response.session else ""
        )
        
    except Exception as e:
        error_msg = str(e)
        if "invalid_credentials" in error_msg.lower() or "invalid login" in error_msg.lower():
            raise HTTPException(status_code=401, detail="Invalid email or password")
        raise HTTPException(status_code=500, detail=f"Authentication error: {error_msg}")

@router.post("/refresh", response_model=AuthResponse)
async def refresh_token(
    request: TokenRefreshRequest,
    supabase: Any = Depends(get_supabase_client)
) -> AuthResponse:
    """Refresh access token"""
    try:
        auth_response = supabase.auth.refresh_session(request.refresh_token)
        
        if auth_response.user is None:
            raise HTTPException(status_code=401, detail="Invalid refresh token")
        
        # Get user from our users table
        user_result = supabase.table("users").select("*").eq("id", auth_response.user.id).execute()
        if not user_result.data:
            raise HTTPException(status_code=404, detail="User profile not found")
        
        user_response = UserResponse(**user_result.data[0])
        
        return AuthResponse(
            user=user_response,
            access_token=auth_response.session.access_token if auth_response.session else "",
            refresh_token=auth_response.session.refresh_token if auth_response.session else ""
        )
        
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Token refresh failed: {str(e)}")

@router.post("/signout", response_model=APIResponse)
async def sign_out(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    supabase: Any = Depends(get_supabase_client)
) -> APIResponse:
    """Sign out user"""
    try:
        # Set the access token for this request
        supabase.auth.set_session(credentials.credentials, "")
        supabase.auth.sign_out()
        
        return APIResponse(success=True, message="Successfully signed out")
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Sign out error: {str(e)}")

@router.get("/me", response_model=UserResponse)
async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    supabase: Any = Depends(get_supabase_client)
) -> UserResponse:
    """Get current authenticated user"""
    try:
        # Verify token with Supabase
        user = supabase.auth.get_user(credentials.credentials)
        
        if user.user is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        
        # Get user from our users table
        user_result = supabase.table("users").select("*").eq("id", user.user.id).execute()
        if not user_result.data:
            raise HTTPException(status_code=404, detail="User profile not found")
        
        return UserResponse(**user_result.data[0])
        
    except Exception as e:
        if "invalid_token" in str(e).lower():
            raise HTTPException(status_code=401, detail="Invalid or expired token")
        raise HTTPException(status_code=500, detail=f"Authentication error: {str(e)}")

@router.post("/forgot-password", response_model=APIResponse)
async def forgot_password(
    email: EmailStr,
    request: Request,
    supabase: Any = Depends(get_supabase_client),
    redirect_to: Optional[str] = None,
) -> APIResponse:
    """Send password reset email with an explicit redirect URL.

    If `redirect_to` is not provided, we default to the caller's Origin with
    the path '/reset-password', e.g. 'https://app.example.com/reset-password'.
    This ensures the recovery link lands on the reset form rather than the site root.
    """
    try:
        # Determine redirect target
        target_redirect = redirect_to
        if not target_redirect:
            origin = request.headers.get("origin")
            if not origin:
                # Fallback to scheme + host from the request
                scheme = request.url.scheme
                host = request.headers.get("host") or request.url.netloc
                origin = f"{scheme}://{host}"
            target_redirect = f"{origin}/reset-password"

        # Send reset email via Supabase with redirect
        try:
            # supabase-py v2 expects options dict for redirect
            supabase.auth.reset_password_email(email, options={"redirect_to": target_redirect})
        except TypeError:
            # Some versions accept redirect_to directly
            supabase.auth.reset_password_email(email, redirect_to=target_redirect)
        return APIResponse(
            success=True,
            message="Password reset email sent if account exists",
        )
    except Exception:
        # Always return success to prevent email enumeration
        return APIResponse(
            success=True,
            message="Password reset email sent if account exists",
        )

# Dependency to get current user from token
async def get_current_user_from_token(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    supabase: Any = Depends(get_supabase_client)
) -> UserResponse:
    """Get current user from JWT token - for use as dependency"""
    try:
        user = supabase.auth.get_user(credentials.credentials)
        
        if user.user is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        
        user_result = supabase.table("users").select("*").eq("id", user.user.id).execute()
        if not user_result.data:
            raise HTTPException(status_code=404, detail="User profile not found")
        
        return UserResponse(**user_result.data[0])
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Authentication failed: {str(e)}")
