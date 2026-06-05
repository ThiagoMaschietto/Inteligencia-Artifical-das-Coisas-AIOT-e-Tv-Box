from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select, desc

from app.database import get_session
from app.models.dado_horta import DadoHorta
from app.models.horta import Horta

router = APIRouter(prefix="/telemetria", tags=["Telemetria da Horta"])

@router.post("/", status_code=status.HTTP_201_CREATED, response_model=DadoHorta)
def receber_dados_sensores(dados_entrada: DadoHorta, session: Session = Depends(get_session)):
    horta_existe = session.get(Horta, dados_entrada.horta_id)
    if not horta_existe:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Horta com ID {dados_entrada.horta_id} não encontrada no sistema.")
    session.add(dados_entrada)
    session.commit()
    session.refresh(dados_entrada)

    return dados_entrada

@router.get("/{horta_id}", response_model=list[DadoHorta])
def obter_historico_telemetria(horta_id: int, limite: int = 20, session: Session = Depends(get_session)):
    horta_existe = session.get(Horta, horta_id)
    if not horta_existe:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Horta com ID {horta_id} não existe no sistema.")

    statement = (select(DadoHorta).where(DadoHorta.horta_id == horta_id).order_by(desc(DadoHorta.data_hora)).limit(limite))
    
    historico = session.exec(statement).all()
    
    return historico