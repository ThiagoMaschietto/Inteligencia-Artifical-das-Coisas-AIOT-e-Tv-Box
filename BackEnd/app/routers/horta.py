from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select

from app.database import get_session
from app.models.horta import Horta
from app.models.usuario import Usuario
from app.routers.auth import obter_usuario_atual

router = APIRouter(prefix="/horta",tags=["Gerenciamento da Horta"])

@router.post("/", status_code=status.HTTP_201_CREATED, response_model=Horta)
def criar_horta(horta_dados: Horta, session: Session = Depends(get_session),usuario_atual: Usuario = Depends(obter_usuario_atual) ):
    horta_dados.usuario_id = usuario_atual.id
    
    session.add(horta_dados)
    session.commit()
    session.refresh(horta_dados)
    return horta_dados

@router.get("/", response_model=list[Horta])
def listar_hortas(session: Session = Depends(get_session), usuario_atual: Usuario = Depends(obter_usuario_atual)):
    statement = select(Horta).where(Horta.usuario_id == usuario_atual.id)
    return session.exec(statement).all()

@router.get("/{horta_id}", response_model=Horta)
def obter_horta_por_id(horta_id: int, session: Session = Depends(get_session),usuario_atual: Usuario = Depends(obter_usuario_atual)):
    horta = session.get(Horta, horta_id)
    
    if not horta:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=f"Horta com ID {horta_id} não foi encontrada."
        )
    
    if horta.usuario_id != usuario_atual.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Você não tem permissão para acessar os dados deste canteiro."
        )
        
    return horta