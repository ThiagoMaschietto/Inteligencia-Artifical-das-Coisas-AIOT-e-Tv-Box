from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
import jwt
from pydantic import BaseModel
from sqlmodel import Session, select

from app.database import get_session
from app.models.usuario import Usuario
from app.core.security import gerar_hash_senha, verificar_senha, criar_token_acesso, SECRET_KEY, ALGORITHM

router = APIRouter(prefix="/auth", tags=["Autenticação e Segurança"])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")

class UsuarioCriar(BaseModel):
    username: str
    password: str

def obter_usuario_atual(token: str = Depends(oauth2_scheme), session: Session = Depends(get_session)) -> Usuario:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token inválido")
    except jwt.PyJWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token inválido ou expirado")
        
    usuario = session.exec(select(Usuario).where(Usuario.username == username)).first()
    if usuario is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Utilizador não encontrado")
        
    return usuario

@router.post("/cadastro", status_code=status.HTTP_201_CREATED)
def cadastrar_usuario(usuario_dados: UsuarioCriar, session: Session = Depends(get_session)):
    usuario_existe = session.exec(select(Usuario).where(Usuario.username == usuario_dados.username)).first()
    if usuario_existe:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Este nome de usuário já está sendo utilizado.")
    
    novo_usuario = Usuario(username=usuario_dados.username, password_hash=gerar_hash_senha(usuario_dados.password))
    
    session.add(novo_usuario)
    session.commit()
    session.refresh(novo_usuario)
    
    return {"mensagem": "Usuário criado com sucesso!", "id": novo_usuario.id, "username": novo_usuario.username}


@router.post("/token")
def login_gerar_token(form_data: OAuth2PasswordRequestForm = Depends(), session: Session = Depends(get_session)):
    usuario = session.exec(select(Usuario).where(Usuario.username == form_data.username)).first()
    
    if not usuario or not verificar_senha(form_data.password, usuario.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Usuário ou senha incorretos.", headers={"WWW-Authenticate": "Bearer"},)
    
    token_acesso = criar_token_acesso(dados={"sub": usuario.username, "id": usuario.id})
    
    return {"access_token": token_acesso, "token_type": "bearer"}