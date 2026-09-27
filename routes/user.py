from fastapi import APIRouter, HTTPException, status, Depends
from models.user import *
from models.token_data import TokenData
import database.user as u
import security.auth as auth
from typing import Dict, List
import consts.permissions as perm
from beanie import PydanticObjectId

user_router = APIRouter(
    tags=["User"]
)

userDatabase = u.UserDatabase()

@user_router.get("/", response_model=List[UserResponseDTO])
async def get_all_users(token: TokenData = Depends(auth.validate_token)) -> List[UserResponseDTO]:
    if not token.has_permission(perm.USER_READ): 
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Can't access user's data.") 

    return await userDatabase.get_all()

@user_router.get("/{id}", response_model=UserResponseDTO)
async def get_user(id: PydanticObjectId, token: TokenData = Depends(auth.validate_token)) -> UserResponseDTO:
    if not token.has_permission(perm.USER_READ): 
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Can't access user's data.") 

    user = await userDatabase.get(id = id)

    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.") 

    return user

@user_router.post("/new", status_code  = status.HTTP_201_CREATED,  response_model=UserResponseDTO)
async def create_user(body: UserRequestDTO, token: TokenData = Depends(auth.validate_token)) -> UserResponseDTO:
    if not token.has_permission(perm.USER_CREATE): 
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Can't create user's data.") 

    user = await userDatabase.create_user(dto = body)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Couldn't create user's data.") 
    
    return  user

@user_router.put("/edit/{id}", response_model=UserResponseDTO)
async def edit_user(id:PydanticObjectId , body: UserRequestDTO, token: TokenData = Depends(auth.validate_token)) -> UserResponseDTO:
    if not token.has_permission(perm.USER_UPDATE): 
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Can't update user's data.") 

    user = await userDatabase.get(id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.") 

    user = await userDatabase.edit_user(id = id, dto = body)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Couldn't update user's data.") 

    return user

@user_router.delete("/{id}")
async def delete_user(id: PydanticObjectId, token: TokenData = Depends(auth.validate_token)) -> Dict:
    if not token.has_permission(perm.USER_DELETE): 
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Can't delete user's data.") 

    delete_success = await userDatabase.delete(id = id)
    if not delete_success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Error on user's data delete")
    
    return {
        "message": "User deleted successfully."
    }