from sqlmodel import Field, SQLModel

class Horta(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    nome: str
    descricao: str

    usuario_id: int = Field(default=None, foreign_key="usuario.id")
