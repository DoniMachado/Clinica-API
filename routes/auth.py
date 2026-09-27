from fastapi import APIRouter, HTTPException, status, Depends, Request
from fastapi.security import OAuth2PasswordRequestForm
from models.user import *
import database.user as u
import security.auth as auth
from typing import Dict
from security.rate_limit import limiter

auth_router = APIRouter(
    tags=["Auth"]
)

userDatabase = u.UserDatabase()

# Criação de usuários será restrita
# @auth_router.post('/signup', status_code  = status.HTTP_201_CREATED,  response_model=UserResponseDTO)
# @limiter.limit("5/minute")
# async def signup(request: Request, body: UserRequestDTO) -> UserResponseDTO:
#     user = await userDatabase.create_user(body)    
#     if user is None:
#         raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="User already exists")
#     return user 

@auth_router.post('/signin')
@limiter.limit("5/minute")
async def signin(request: Request, dto: UserSignInRequestDTO) -> Dict:
    user = await userDatabase.authenticate_user(dto) 
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials!")
    return auth.create_token_return(user)

@auth_router.post('/token')
@limiter.limit("5/minute")
async def token(request: Request, form_data:  OAuth2PasswordRequestForm = Depends(OAuth2PasswordRequestForm)) -> Dict:
    dto = UserSignInRequestDTO(login = form_data.username, password = form_data.password)
    user = await userDatabase.authenticate_user(dto) 
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials!")
    return auth.create_token_return(user)