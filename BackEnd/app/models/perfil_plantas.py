from typing import Optional, List
from sqlmodel import SQLModel, Field, Relationship

class PerfilPlanta(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    nome: str = Field(index=True, unique=True)
    temp_min: float
    temp_max: float
    umidade_solo_min: int
    umidade_ar_min: int

    hortas: List["Horta"] = Relationship(back_populates="perfil")

from app.models.horta import Horta