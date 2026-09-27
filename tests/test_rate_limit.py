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
async def test_rate_limite_unauthorized_json(client_test: AsyncClient, get_doctors: List[User]): 
    doctor_1 = get_doctors[0]
    token = auth.create_token(doctor_1)

    for index in range(6):
        response = await client_test.post(f"/auth/signin", headers={"Authorization": f"Bearer {token}"},
                                      json={
                                          "login": "teste",
                                          "password": "teste"
                                      }) 
        if index != 5:
            assert response.status_code == 401
        else:
            assert response.status_code == 429

@pytest.mark.asyncio
async def test_rate_limite_unauthorized_form(client_test: AsyncClient, get_doctors: List[User]): 
    doctor_1 = get_doctors[0]
    token = auth.create_token(doctor_1)

    for index in range(6):
        response = await client_test.post(f"/auth/token", headers={"Authorization": f"Bearer {token}"},
                                      data={
                                          "username": "teste",
                                          "password": "teste"
                                      }) 
        if index != 5:
            assert response.status_code == 401
        else:
            assert response.status_code == 429