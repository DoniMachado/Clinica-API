import pytest
import pytest_asyncio
from httpx import AsyncClient
import database.user as u
from models.user import * 
import security.auth as auth
from typing import List
import consts.roles as r

userDatabase = u.UserDatabase()

@pytest_asyncio.fixture
async def get_doctors(client_test: AsyncClient):
    doctors = await userDatabase.get_all_by_role(r.HEALTHCARE_PROFESSIONAL_ROLE)
    return doctors

@pytest.mark.asyncio
async def test_bfla_forbidden(client_test: AsyncClient, get_doctors: List[User]): 
    doctor_1 = get_doctors[0]
    token = auth.create_token(doctor_1)

    response = await client_test.get(f"/user/", headers={"Authorization": f"Bearer {token}"}) 
    assert response.status_code == 403