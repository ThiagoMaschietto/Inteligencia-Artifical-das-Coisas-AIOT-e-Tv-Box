from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from sqlmodel import Session, select, desc
import csv
import io

from app.database import get_session
from app.models.dado_horta import DadoHorta
from app.models.horta import Horta

router = APIRouter(prefix="/telemetria", tags=["Telemetria da Horta"])

def checar_limites_sensores(temperatura, umidade_solo, umidade_ar):
    alertas = []
    if umidade_solo < 30:
        alertas.append("💧 Solo seco! Regue a horta imediatamente.")
    if temperatura > 35:
        alertas.append("🔥 Temperatura muito alta! Risco de desidratação.")
    elif temperatura < 10:
        alertas.append("❄️ Temperatura criticamente baixa.")
    if umidade_ar < 20:
        alertas.append("🍂 Ar extremamente seco no ambiente.")
    
    return {"status": "ALERTA" if alertas else "OK","mensagens": alertas if alertas else ["Dados salvos e horta saudável!"]}

@router.post("/", status_code=status.HTTP_201_CREATED)
def receber_dados_sensores(dados_entrada: DadoHorta, session: Session = Depends(get_session)):
    horta_existe = session.get(Horta, dados_entrada.horta_id)
    if not horta_existe:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Horta com ID {dados_entrada.horta_id} não encontrada no sistema.")
    session.add(dados_entrada)
    session.commit()
    session.refresh(dados_entrada)

    return checar_limites_sensores(dados_entrada.temperatura, dados_entrada.umidade_solo, dados_entrada.umidade_ar)

@router.get("/{horta_id}", response_model=list[DadoHorta])
def obter_historico_telemetria(horta_id: int, limite: int = 20, session: Session = Depends(get_session)):
    horta_existe = session.get(Horta, horta_id)
    if not horta_existe:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Horta com ID {horta_id} não existe no sistema.")

    statement = (select(DadoHorta).where(DadoHorta.horta_id == horta_id).order_by(desc(DadoHorta.data_hora)).limit(limite))
    
    historico = session.exec(statement).all()
    
    return historico

@router.get("/atual/{horta_id}")
def obter_telemetria_atual(horta_id: int, session: Session = Depends(get_session)):
    horta_existe = session.get(Horta, horta_id)
    if not horta_existe:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Horta não encontrada.")

    statement = select(DadoHorta).where(DadoHorta.horta_id == horta_id).order_by(desc(DadoHorta.data_hora)).limit(1)
    ultimo_dado = session.exec(statement).first()
    
    if not ultimo_dado:
        return {"status": "SEM_DADOS", "mensagens": ["Nenhum dado encontrado para esta horta."]}

    alertas = []
    perfil = horta_existe.perfil
    
    if perfil:
        if ultimo_dado.umidade_solo < perfil.umidade_solo_min:
            alertas.append(f"💧 Solo seco para {perfil.nome}! Regue imediatamente.")
        if ultimo_dado.temperatura > perfil.temp_max:
            alertas.append(f"🔥 {perfil.nome} está com muito calor! Risco de desidratação.")
        elif ultimo_dado.temperatura < perfil.temp_min:
            alertas.append(f"❄️ {perfil.nome} está no frio extremo!")
        if ultimo_dado.umidade_ar < perfil.umidade_ar_min:
            alertas.append("🍂 Ar muito seco para este cultivo.")
    else:
        if ultimo_dado.umidade_solo < 30:
            alertas.append("💧 Solo seco! Regue a horta.")
        if ultimo_dado.temperatura > 35:
            alertas.append("🔥 Temperatura muito alta!")

    return {"temperatura": ultimo_dado.temperatura, "umidade_ar": ultimo_dado.umidade_ar, "umidade_solo": ultimo_dado.umidade_solo, "luz": ultimo_dado.luz, "status": "ALERTA" if alertas else "OK", "mensagens": alertas if alertas else ["Horta saudável!"]}

@router.get("/exportar/{horta_id}")
def exportar_relatorio_csv(horta_id: int, session: Session = Depends(get_session)):
    horta_existe = session.get(Horta, horta_id)
    if not horta_existe:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Horta não encontrada.")

    statement = select(DadoHorta).where(DadoHorta.horta_id == horta_id).order_by(desc(DadoHorta.data_hora))
    historico = session.exec(statement).all()

    output = io.StringIO()
    writer = csv.writer(output, delimiter=';')

    writer.writerow(["Data e Hora", "Temperatura (°C)", "Umidade do Ar (%)", "Umidade do Solo (%)", "Luminosidade"])

    for dado in historico:
        data_formatada = dado.data_hora.strftime("%d/%m/%Y %H:%M:%S") if hasattr(dado.data_hora, 'strftime') else dado.data_hora
        
        writer.writerow([
            data_formatada,
            dado.temperatura,
            dado.umidade_ar,
            dado.umidade_solo,
            dado.luz
        ])

    output.seek(0)

    nome_ficheiro = f"relatorio_{horta_existe.nome.lower().replace(' ', '_')}.csv"

    return StreamingResponse(io.BytesIO(output.getvalue().encode('utf-8-sig')), media_type="text/csv", headers={"Content-Disposition": f"attachment; filename={nome_ficheiro}"})