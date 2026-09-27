from pydantic import BaseModel, Field, ConfigDict, EmailStr, field_serializer
from fastapi import Form
from beanie import Document, PydanticObjectId
from datetime import date

class Patient(Document):
    model_config = ConfigDict(from_attributes=True, extra='forbid')

    # _id é gerado e gerenciado pelo MongoDB/Beanie

    name: str  = Field(
        description = "Nome do paciente",
        examples = ["Paciente 1"]
    )

    cpf: str  = Field(
        description = "CPF do paciente",
        examples = ["000.000.000-00"]
    )

    email: EmailStr  = Field(
        description = "Email do paciente",
        examples = ["paciente.01@email.com.br"]
    )

    
    phone: str  = Field(
        description = "Telefone do paciente",
        examples = ["(19) 99898-5555"]
    )

    address: str | None = Field(
        description = "Endereço do paciente",
        examples = ["Rua XPTO, APT 12"]
    )

    birth_date: date | None  = Field(
        description = "Data de nascimento do paciente"
    )

    audit_token: str  = Field(
            description = "Token de auditoria",
            examples = ["550e8400-e29b-41d4-a716-446655440000"]
    )


    class Settings:
        name = "patients"


class PatientResponseDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True, extra='ignore')

    id: PydanticObjectId = Field(
        description = "Identificador único do usuário",
        examples = ["68c123456789abcdef123456"]
    )

    name: str  = Field(
        description = "Nome do paciente",
        examples = ["Paciente 1"]
    )

    cpf: str  = Field(
        description = "CPF do paciente",
        examples = ["000.000.000-00"]
    )

    email: EmailStr  = Field(
        description = "Email do paciente",
        examples = ["paciente.01@email.com.br"]
    )
    
    phone: str  = Field(
        description = "Telefone do paciente",
        examples = ["(19) 99898-5555"]
    )

    address: str | None = Field(
        description = "Endereço do paciente",
        examples = ["Rua XPTO, APT 12"]
    )

    birth_date: date | None  = Field(
        description = "Data de nascimento do paciente"
    )

    @field_serializer("id")
    def serialize_id(self, value: PydanticObjectId) -> str:
        return str(value)

class PatientRequestDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True, extra='forbid')

    name: str  = Field(
        description = "Nome do paciente",
        examples = ["Paciente 1"]
    )

    cpf: str  = Field(
        description = "CPF do paciente",
        examples = ["000.000.000-00"]
    )

    email: EmailStr  = Field(
        description = "Email do paciente",
        examples = ["paciente.01@email.com.br"]
    )
    
    phone: str  = Field(
        description = "Telefone do paciente",
        examples = ["(19) 99898-5555"]
    )

    address: str | None = Field(
        description = "Endereço do paciente",
        examples = ["Rua XPTO, APT 12"]
    )

    birth_date: date | None  = Field(
        description = "Data de nascimento do paciente"
    )

    @classmethod
    def as_form( cls, name: str = Form(...),  cpf: str = Form(...), email: EmailStr  = Form(...),  phone: str  = Form(...), address: str | None = Form(...), birth_date: str | None = Form(...)):
        return cls(name = name, cpf = cpf,  email = email, phone = phone, address = address, birth_date = birth_date )
