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
async def test_extra_fields_forbidden(client_test: AsyncClient, get_doctors: List[User]): 
    doctor_1 = get_doctors[0]
    token = auth.create_token(doctor_1)

    response = await client_test.post(f"/appointment/new", headers={"Authorization": f"Bearer {token}"},
                                      json={
                                            "extra_field": "teste",
                                            "patient_id": "68d2a1b4c5e6f78901234567",
                                            "doctor_id": "68d2a1b4c5e6f78901234568",
                                            "start_at": "2026-09-27T14:00:00",
                                            "end_at": "2026-09-27T15:00:00"
                                            }) 
    assert response.status_code == 422