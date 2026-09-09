from datetime import datetime, timezone, timedelta
from sqlmodel import Field, SQLModel

"""
Retorna a data/hora atual no fuso de Brasília (UTC-3),
arredondando os minutos para o bloco de 30 minutos mais próximo.
"""
def obter_hora_absoluta_brt() -> datetime:
    fuso_brt = timezone(timedelta(hours=-3))
    
    return datetime.now(fuso_brt).replace(microsecond=0)

class DadoHorta(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    data_hora: datetime = Field(default_factory=obter_hora_absoluta_brt, index=True)
    temperatura: float
    umidade_ar: float
    umidade_solo: int
    luz: float

    status_anomalia: bool = Field(default=False)
    causa_raiz: str = Field(default="Nenhuma")

    horta_id: int = Field(default=None, foreign_key="horta.id")