from pydantic import BaseModel, Field, ConfigDict, EmailStr, field_serializer
from fastapi import Form
from beanie import Document, PydanticObjectId

class User(Document):
    model_config = ConfigDict(from_attributes=True, extra='forbid')

    # _id é gerado e gerenciado pelo MongoDB/Beanie
    
    login: str  = Field(
        description = "Login do usuário",
        examples = ["usuario.1"]
    )

    name: str  = Field(
        description = "Nome do usuário",
        examples = ["Usuário 1"]
    )

    email: EmailStr  = Field(
        description = "Email do usuário",
        examples = ["email@email.com.br"]
    )

    password_hash: str  = Field(
        min_length=1,
        description = "Hash da senha do usuário",
        examples = ["550e8400-e29b-41d4-a716-446655440000!"]
    )

    audit_token: str  = Field(
            description = "Token de auditoria",
            examples = ["550e8400-e29b-41d4-a716-446655440000"]
    )

    role: str  = Field(
        description = "Role do usuário",
        examples = ["healthcare_professional"]
    )

    class Settings:
        name = "users"


class UserResponseDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True, extra='ignore')

    id: PydanticObjectId = Field(
        description = "Identificador único do usuário",
        examples = ["68c123456789abcdef123456"]
    )

    login: str  = Field(
        description = "Login do usuário",
        examples = ["usuario.1"]
    )

    name: str  = Field(
        description = "Nome do usuário",
        examples = ["Usuário 1"]
    )

    email: EmailStr  = Field(
        description = "Email do usuário",
        examples = ["email@email.com.br"]
    )

    @field_serializer("id")
    def serialize_id(self, value: PydanticObjectId) -> str:
        return str(value)

class UserRequestDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True, extra='forbid')

    name: str  = Field(
        description = "Nome do usuário",
        examples = ["Usuário 1"]
    )

    login: str  = Field(
        description = "Login do usuário",
        examples = ["usuario.1"]
    )

    email: EmailStr  = Field(
        description = "Email do usuário",
        examples = ["email@email.com.br"]
    )

    password: str  = Field(
        min_length=1,
        description = "Senha do usuário",
        examples = ["strong123Psw!"]
    )

    @classmethod
    def as_form( cls, login: str = Form(...), name: str = Form(...),  email: EmailStr  = Form(...),  password: str = Form(...) ):
        return cls(login = login ,name = name, email = email, password = password )



class UserSignInRequestDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True, extra='forbid')

    login: str  = Field(
        description = "Login do usuário",
        examples = ["usuario.1"]
    )

    password: str  = Field(
        min_length=1,
        description = "Senha do usuário",
        examples = ["strong123Psw!"]
    )

    @classmethod
    def as_form( cls, login: str  = Form(...),  password: str = Form(...) ):
        return cls( login = login, password = password )