from sqlmodel import Field, SQLModel

class Usuario(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    username: str
    password_hash: str
