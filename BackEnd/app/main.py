from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import SQLModel

from app.database import engine

from app.models.usuario import Usuario
from app.models.horta import Horta
from app.models.dado_horta import DadoHorta

from app.routers import auth, horta, telemetria

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Inicializando o banco de dados local na TV Box...")
    SQLModel.metadata.create_all(engine)
    
    yield 

    print("Desligando o servidor da horta de forma segura...")

app = FastAPI(title = "QuerPlantar", lifespan=lifespan)

app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

app.include_router(auth.router)
app.include_router(horta.router)
app.include_router(telemetria.router)

@app.get("/")
def home():
    return {"status": "Servidor da Horta IoT ativo e operante!"}