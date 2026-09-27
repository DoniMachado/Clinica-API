from pydantic import BaseModel, Field, ConfigDict, field_serializer
from fastapi import Form
from beanie import Document, PydanticObjectId

class Integration(Document):
    model_config = ConfigDict(from_attributes=True, extra='forbid')

    # _id é gerado e gerenciado pelo MongoDB/Beanie
    
    client_name: str  = Field(
        description = "Nome do Cliente",
        examples = ["Parceiro Teste 1"]
    )

    client_id: str  = Field(
        description = "Identificador do Cliente",
        examples = ["partner-test-1"]
    )

    client_secret_hash: str  = Field(
        description = "Hash do Secret do Cliente",
        examples = ["550e8400-e29b-41d4-a716-446655440000!"]
    )

    audit_token: str  = Field(
            description = "Token de auditoria",
            examples = ["550e8400-e29b-41d4-a716-446655440000"]
    )

    class Settings:
        name = "integrations"


class IntegrationRequestDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True, extra='forbid')

    client_name: str  = Field(
        description = "Nome do Cliente",
        examples = ["Parceiro Teste 1"]
    )

    client_id: str  = Field(
        description = "Identificador do Cliente",
        examples = ["partner-test-1"]
    )

    client_secret: str  = Field(
        description = "Secret do Cliente",
        examples = ["123456"]
    )

    @classmethod
    def as_form( cls, client_name: str = Form(...), client_id: str = Form(...), client_secret: str = Form(...)):
        return cls(client_name = client_name, client_id = client_id ,client_secret = client_secret)


class IntegrationAuthenticationRequestDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True, extra='forbid')

    client_id: str  = Field(
        description = "Identificador do Cliente",
        examples = ["partner-test-1"]
    )

    client_secret: str  = Field(
        description = "Secret do Cliente",
        examples = ["123456"]
    )

    @classmethod
    def as_form( cls, client_id: str = Form(...), client_secret: str = Form(...)):
        return cls(client_id = client_id ,client_secret = client_secret)


class IntegrationResponseDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True, extra='ignore')

    id: PydanticObjectId = Field(
        description = "Identificador único da integração",
        examples = ["68c123456789abcdef123456"]
    )

    client_name: str  = Field(
        description = "Nome do Cliente",
        examples = ["Parceiro Teste 1"]
    )

    @field_serializer("id")
    def serialize_id(self, value: PydanticObjectId) -> str:
        return str(value)