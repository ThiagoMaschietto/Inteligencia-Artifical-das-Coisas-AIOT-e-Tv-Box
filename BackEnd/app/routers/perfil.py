from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select

from app.database import get_session
from app.models.perfil_plantas import PerfilPlanta

router = APIRouter(prefix="/perfil", tags=["Perfil de Plantas"])

@router.post("/", status_code=status.HTTP_201_CREATED, response_model=PerfilPlanta)
def criar_perfil_planta(perfil: PerfilPlanta, session: Session = Depends(get_session)):
    perfil_existente = session.exec(select(PerfilPlanta).where(PerfilPlanta.nome == perfil.nome)).first()
    if perfil_existente:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail=f"O perfil de planta '{perfil.nome}' já existe no sistema."
        )
    
    session.add(perfil)
    session.commit()
    session.refresh(perfil)
    return perfil

@router.get("/", response_model=list[PerfilPlanta])
def listar_perfis_plantas(session: Session = Depends(get_session)):
    perfis = session.exec(select(PerfilPlanta)).all()
    return perfis