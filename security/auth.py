import jwt
from jwt.exceptions import InvalidTokenError
from datetime import datetime, timezone, timedelta
from models.user import User
from models.integration import Integration
from models.token_data import TokenData
from fastapi import Depends, HTTPException, Cookie
from fastapi.security import OAuth2PasswordBearer
from typing import Dict
from consts.client_type import USER_CLIENT, M2M_CLIENT
from consts.roles_permissions import ROLE_PERMISSIONS
from consts.roles import INTEGRATION_ROLE
from beanie import PydanticObjectId
from database.connection import settings

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=settings.TOKEN_URL, auto_error= False)

def create_token(user: User) -> str:
    exp = datetime.now(timezone.utc) + timedelta(minutes=30)
    iat = datetime.now(timezone.utc)
    dados = {
        "sub": str(user.id),
        "exp": exp,
        "iat": iat,
        "permissions": ROLE_PERMISSIONS.get(user.role, []),
        "role": user.role,
        "client_type": USER_CLIENT
    }
    token = jwt.encode(payload = dados, key = settings.SECRET_KEY, algorithm = settings.TOKEN_ALGORITHM)
    return token

def create_token_return(user: User) -> Dict:
    token = create_token(user = user)
    return {
        "access_token": token,
        "token_type": settings.TOKEN_TYPE
    }

def create_integration_token(integration: Integration) -> str:
    exp = datetime.now(timezone.utc) + timedelta(minutes=30)
    iat = datetime.now(timezone.utc)
    dados = {
        "sub": str(integration.id),
        "exp": exp,
        "iat": iat,
        "permissions": ROLE_PERMISSIONS.get(INTEGRATION_ROLE, []),
        "role": INTEGRATION_ROLE,
        "client_type": M2M_CLIENT
    }
    token = jwt.encode(payload = dados, key = settings.SECRET_KEY, algorithm = settings.TOKEN_ALGORITHM)
    return token

def create_integration_token_return(integration: Integration) -> Dict:
    token = create_integration_token(integration = integration)
    return {
        "access_token": token,
        "token_type": settings.TOKEN_TYPE
    }

def validate_token(token: str = Depends(oauth2_scheme), access_token: str | None = Cookie(default=None)):
    error = HTTPException(
        status_code=401,
        detail="Token inválido ou expirado",
        headers={"WWW-Authenticate": settings.TOKEN_TYPE}
    )

    try:
        if token is None:
            token = access_token

        if token is None:
            raise error
    
        result = jwt.decode(jwt = token, key = settings.SECRET_KEY, algorithms = [settings.TOKEN_ALGORITHM])
        if result is None:
            raise error

        expiration = result.get('exp')
        if expiration is None :            
            raise error

        expiration = datetime.fromtimestamp(
            expiration,
            tz=timezone.utc
        )

        if expiration < datetime.now(timezone.utc):
            raise error            

        entity_id = result.get('sub')
        permissions = result.get('permissions')
        role = result.get('role')
        client_type = result.get('client_type')

        if entity_id is None:
            raise error

        token_data = TokenData(entity_id = PydanticObjectId(entity_id), permissions = permissions, role = role, client_type = client_type)
        
    except InvalidTokenError as ex:
        print(ex)
        raise error
    except ValueError as ex:
        print(ex)
        raise error

    return token_data