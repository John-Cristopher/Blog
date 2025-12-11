from dotenv import load_dotenv
import os
from pathlib import Path

# Garantir que o .env da pasta do projeto seja carregado
here = Path(__file__).resolve().parents[1]
load_dotenv(dotenv_path=here / ".env")

print("SECRET_KEY =", os.getenv("SECRET_KEY"))
print("USUARIO_ADMIN =", os.getenv("USUARIO_ADMIN"))
print("SENHA_ADMIN =", os.getenv("SENHA_ADMIN"))
