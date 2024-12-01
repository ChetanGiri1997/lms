from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel
from datetime import timedelta
import os
from models.user import UserRegister, UserInDB, Token, TokenData, UserLogin, UserUpdate, UserOut
from auth import authenticate_user

router = APIRouter()

@router.post("/token", response_model=Token)
async def login_for_access_token(login_request: UserLoginRequest, db=Depends(get_db)):
    user = await authenticate_user(db, login_request.username, login_request.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Generate access token (with a configurable expiration time)
    access_token_expires = timedelta(minutes=int(os.getenv("ACCESS_TOKEN_EXPIRY", 30)))
    access_token = create_access_token(
        data={"sub": user["username"], "role": user.get("role")}, expires_delta=access_token_expires
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
    }