from typing import Generic, TypeVar, List
from beanie import init_beanie, PydanticObjectId, Document
from motor.motor_asyncio import AsyncIOMotorClient
from bson.codec_options import CodecOptions
from datetime import timezone
from pydantic import BaseModel
from configs.settings import settings
from models.patient import Patient
from models.appointment import Appointment
from models.integration import Integration
from models.user import User

class Connection():

    def __init__(self):
        self.settings = settings

    async def initialize_database(self):
        client = AsyncIOMotorClient(self.settings.DATABASE_URL)
        database = client.get_default_database()
        database = database.with_options(codec_options=CodecOptions(tz_aware=True,tzinfo=timezone.utc))
        await init_beanie(database= database,
                          document_models=[Patient, Appointment, Integration, User ])

connection = Connection()

T = TypeVar("T", bound=Document)
U = TypeVar("U", bound=BaseModel)

class Database(Generic[T]):
    def __init__(self, model: type[T]):
        self.model = model

    async def save(self, document: T) -> T:
        await document.create()
        return document

    async def get(self, id: PydanticObjectId) -> T | None:
        doc = await self.model.get(id)
        if doc:
            return doc
        return None

    async def get_all(self) -> List[T]:
        docs = await self.model.find_all().to_list()
        return docs

    async def update(self, id: PydanticObjectId, body: U)-> T | None:
        doc_id = id
        des_body = body.dict()

        des_body = {k: v for k, v in des_body.items() if v is not None}
        update_query = {"$set": {
            field: value for field, value in des_body.items()
        }}

        doc = await self.get(doc_id)
        if not doc:
            return None
        await doc.update(update_query)
        return doc

    async def delete(self, id: PydanticObjectId) -> bool:
        doc = await self.get(id)
        if not doc:
            return False
        await doc.delete()
        return True

    async def clear(self) -> bool:
        docs = await self.get_all()

        for doc in docs:
            await doc.delete()

        return True