from datetime import datetime, timedelta, timezone
from os import getenv
from passlib.context import CryptContext
import jwt

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

SECRET_KEY = getenv("SECRET_KEY", "chave_padrao_caso_nao_encontre_no_env")
ALGORITHM = getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30))

def gerar_hash_senha(senha_pura: str) -> str:
    return pwd_context.hash(senha_pura)

def verificar_senha(senha_pura: str, senha_criptografada: str) -> bool:
    return pwd_context.verify(senha_pura, senha_criptografada)

def criar_token_acesso(dados: dict) -> str:
    dados_copia = dados.copy()
    tempo_expiracao = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    dados_copia.update({"exp": tempo_expiracao})
    
    token_jwt = jwt.encode(dados_copia, SECRET_KEY, algorithm=ALGORITHM)
    return token_jwt