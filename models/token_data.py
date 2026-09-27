from pydantic import BaseModel, Field, ConfigDict
from typing import List
from consts.permissions import SYSTEM_ADMIN
from consts.client_type import M2M_CLIENT, USER_CLIENT
from consts.roles import ADMIN_ROLE
from beanie import PydanticObjectId

class TokenData(BaseModel):
    model_config = ConfigDict(from_attributes=True, extra='forbid')

    entity_id: PydanticObjectId = Field(
        description = "Identificador único da entidade (usuário/integration)",
        examples =  [20]
    )

    permissions: List[str] = Field(
        description = "Lista de permissões da entidade (usuário/integration)",
        examples =  []
    )

    role: str | None = Field(
        description = "Role da entidade (usuário/integration)",
        examples =  ["participant"]
    )

    client_type: str = Field(
        description = "Tipo do cliente",
        examples =  ["user"]
    )

    def has_role(self, role: str) -> bool:
        if not role:
            return False

        if self.role == ADMIN_ROLE or SYSTEM_ADMIN in self.permissions:
            return True

        return self.role == role

    def has_permission(self, permission: str) -> bool:
        if len(self.permissions) == 0:
            return False

        if SYSTEM_ADMIN in self.permissions:
            return True

        return permission in self.permissions

    def has_any_permission(self, permissions: List[str]) -> bool:
        if len(self.permissions) == 0:
            return False

        if SYSTEM_ADMIN in self.permissions:
            return True

        for permission in permissions:
            if permission in self.permissions:
                return True

        return False

    def has_all_permission(self, permissions: List[str]) -> bool:
        if len(self.permissions) == 0:
            return False

        if SYSTEM_ADMIN in self.permissions:
            return True

        for permission in permissions:
            if permission not in self.permissions:
                return False

        return True

    def has_owner_id(self, resource_owner_id: PydanticObjectId) -> bool:
        if SYSTEM_ADMIN in self.permissions:
            return True

        if self.client_type != USER_CLIENT:
            return False

        return resource_owner_id == self.entity_id
    
