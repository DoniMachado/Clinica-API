from fastapi import APIRouter, HTTPException, status, Depends, Request
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from models.integration import *
import database.integration as i
import security.auth as auth
from typing import Dict
from security.rate_limit import limiter

integration_router = APIRouter(
    tags=["Integration"]
)

basic_scheme = HTTPBasic()
integrationDatabase = i.IntegrationDatabase()

# Criação de integração será restrita
# @integration_router.post('/new', status_code  = status.HTTP_201_CREATED,  response_model=IntegrationResponseDTO)
# @limiter.limit("5/minute")
# async def signup(request: Request, body: IntegrationRequestDTO) -> IntegrationResponseDTO:
#     integration = await integrationDatabase.create_integration(body)    
#     if integration is None:
#         raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Integration already exists")
#     return integration 

@integration_router.post('/token')
@limiter.limit("5/minute")
async def token(request: Request, grant_type: str = Form(...), credentials: HTTPBasicCredentials = Depends(basic_scheme)) -> Dict:
    if grant_type != "client_credentials":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Unsupported grant type")

    dto = IntegrationAuthenticationRequestDTO(client_id = credentials.username, client_secret =  credentials.password)    
    integration = await integrationDatabase.authenticate_integration(dto) 

    if integration is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials!")
    
    return auth.create_integration_token_return(integration)