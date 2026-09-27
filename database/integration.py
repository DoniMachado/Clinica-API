from models.integration import Integration, IntegrationRequestDTO, IntegrationAuthenticationRequestDTO
import security.hash as hs
import uuid
from database.connection import Database
from beanie import PydanticObjectId

class IntegrationDatabase(Database[Integration]):

    def __init__(self):
        super().__init__(Integration)

    async def get_by_client_id(self, client_id: str) -> Integration | None:
        return await self.model.find_one(
            Integration.client_id == client_id
        )
    
    async def authenticate_integration(self, dto: IntegrationAuthenticationRequestDTO) -> Integration | None:
        integration = await self.get_by_client_id(dto.client_id)

        if integration is None:
            return None

        if hs.verify_password(dto.client_secret, integration.client_secret_hash):
            return integration

        return None
    
    async def delete_by_client_id(self, client_id: str) -> bool:
        integration = await self.get_by_client_id(client_id)

        if not integration:
            return False
        
        await integration.delete()
        return True

    async def create_integration(self, dto: IntegrationRequestDTO) -> Integration | None:
        if dto is None:
            return None

        existing_integration = await self.get_by_client_id(dto.client_id)

        if existing_integration is not None:
            return None

        integration = Integration(
            client_name = dto.client_name,
            client_id = dto.client_id,
            client_secret_hash = hs.hash_password(dto.client_secret),
            audit_token = str(uuid.uuid4())
        )

        return await integration.save()


    async def edit_integration(self, id: PydanticObjectId, dto: IntegrationRequestDTO) -> Integration | None:
        if dto is None:
            return None
        
        integration = await self.get(id = id)

        if integration is None:
            return None

        if integration.client_id != dto.client_id:
            existing_integration = self.get_by_client_id(dto.client_id)

            if existing_integration is not None and existing_integration.id != id:
                return None

        integration.client_name = dto.client_name
        integration.client_id = dto.client_id
        integration.client_secret_hash = hs.hash_password(dto.client_secret)

        return await self.update(id = id, body = integration)