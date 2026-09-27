from models.user import User, UserRequestDTO, UserSignInRequestDTO
import security.hash as hs
import uuid
import consts.roles as r
from database.connection import Database
from beanie import PydanticObjectId
from typing import List

class UserDatabase(Database[User]):

    def __init__(self):
        super().__init__(User)

    async def get_by_login(self, login: str) -> User | None:
        return await self.model.find_one(
            User.login == login
        )

    async def get_by_email(self, email: str) -> User | None:
        return await self.model.find_one(
            User.email == email
        )

    async def get_all_by_role(self, role: str) -> List[User]:
        return await self.model.find(User.role == role).to_list()
    
    async def authenticate_user(self, dto: UserSignInRequestDTO) -> User | None:
        user = await self.get_by_login(login = dto.login)

        if user is None:
            return None

        if hs.verify_password(dto.password, user.password_hash):
            return user

        return None

    async def create_user(self, dto: UserRequestDTO) -> User | None:
        if dto is None:
            return None

        existing_user = await self.get_by_login(login = dto.login)

        if existing_user is not None:
            return None

        user = User(
            login = dto.login,
            name = dto.name,
            email = dto.email,
            password_hash = hs.hash_password(dto.password),
            audit_token = str(uuid.uuid4()),
            role = r.PARTICIPANT_ROLE
        )

        return await user.save()

    async def edit_user(self, id: PydanticObjectId, dto: UserRequestDTO) -> User | None:
        if dto is None:
            return None

        user = await self.get(id = id)

        if user is None:
            return None

        if user.login != dto.login:
            existing_user = await self.get_by_login(login = dto.login)

            if existing_user is not None and existing_user.id != id:
                return None

        user.login = dto.login
        user.name = dto.name
        user.email = dto.email
        user.password_hash = hs.hash_password(dto.password)        

        return await self.update(id = id, body = user)