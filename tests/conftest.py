from asgi_lifespan import LifespanManager
from httpx import AsyncClient, ASGITransport
from main import app
import pytest_asyncio

@pytest_asyncio.fixture
async def client_test():
    async with LifespanManager(app):
        async with AsyncClient(
            transport=ASGITransport(app=app), 
            base_url="http://test"
        ) as ac:
            yield ac