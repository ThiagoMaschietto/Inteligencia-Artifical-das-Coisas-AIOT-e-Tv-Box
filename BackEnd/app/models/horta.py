from typing import Optional
from sqlmodel import Field, Relationship, SQLModel

class Horta(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    nome: str
    descricao: Optional[str] = None
    
    usuario_id: int = Field(foreign_key="usuario.id") 
    
    perfil_id: Optional[int] = Field(default=None, foreign_key="perfilplanta.id")
    perfil: Optional["PerfilPlanta"] = Relationship(back_populates="hortas")

from app.models.perfil_plantas import PerfilPlanta