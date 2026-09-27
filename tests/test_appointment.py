import pytest
import pytest_asyncio
from httpx import AsyncClient
import database.user as u
import security.auth as auth

userDataBase = u.UserDatabase()


@pytest_asyncio.fixture
async def create_token(client_test: AsyncClient):
    user = await userDataBase.get_by_login(login='adm.teste.1')
    token = auth.create_token(user)
    return token

@pytest.mark.asyncio
async def test_access_without_token(client_test: AsyncClient): 
    response = await client_test.get("/appointment/") 
    assert response.status_code == 401

@pytest.mark.asyncio
async def test_access_with_valid_token(client_test: AsyncClient, create_token: str): 
    response = await client_test.get("/appointment/", headers={"Authorization": f"Bearer {create_token}"}) 
    assert response.status_code == 200