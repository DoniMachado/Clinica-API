from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from database.connection import connection
from security.rate_limit import limiter
from slowapi.errors import RateLimitExceeded
from slowapi import _rate_limit_exceeded_handler
from routes.auth import auth_router
from routes.integration import integration_router
from routes.appointment import appointment_router
from routes.patient import patient_router
from routes.user import user_router
import time
import uvicorn

origins = [
    "http://localhost",
    "http://localhost:8080",
    "https://localhost",
    "https://localhost:8080",
    "https://example.com",
    "https://www.example.com",
    "http://localhost:3000",
]

app = FastAPI()
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET, PUT, POST, DELETE"],
    allow_headers=["*"],
)

@app.middleware("http")
async def add_headers(request: Request, call_next):
    start_time = time.perf_counter()
    response = await call_next(request)
    process_time = time.perf_counter() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"

    return response

@app.on_event("startup")
async def init_db():
    await connection.initialize_database()

@app.get("/")
async def home() -> dict:
    return RedirectResponse(url="/docs")

@app.get("/hello")
async def hello() -> dict:
    return {
        "message": "Hello World!"
    }

@app.get("/health")
async def health() -> dict:
    return {
        "message": "O Servidor está FUNCIONANDO!!"
    }

app.include_router(auth_router, prefix = "/auth")
app.include_router(user_router, prefix = "/user")
app.include_router(integration_router, prefix = "/integration")
app.include_router(patient_router, prefix = "/patient")
app.include_router(appointment_router, prefix = "/appointment")

if __name__ == "__main__":
    print("Iniciando o Projeto Agenda-Consultório-API...")
    uvicorn.run("main:app", host="localhost", port=8080, reload=True)