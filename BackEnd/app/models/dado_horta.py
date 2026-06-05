from datetime import datetime, timezone, timedelta
from sqlmodel import Field, SQLModel

"""
Retorna a data/hora atual no fuso de Brasília (UTC-3),
arredondando os minutos para o bloco de 30 minutos mais próximo.
"""
def obter_hora_absoluta_brt() -> datetime:
    fuso_brt = timezone(timedelta(hours=-3))
    agora = datetime.now(fuso_brt)
    
    if agora.minute < 15:
        minutos_redondos = 0
    elif agora.minute < 45:
        minutos_redondos = 30
    else:
        minutos_redondos = 30 if agora.minute >= 30 else 0
        
    return agora.replace(minute=minutos_redondos, second=0, microsecond=0)

class DadoHorta(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    data_hora: datetime = Field(default_factory=obter_hora_absoluta_brt, index=True)
    temperatura: float
    umidade: float
    luz: float

    horta_id: int = Field(default=None, foreign_key="horta.id")