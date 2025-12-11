import os

SECRET_KEY = os.getenv("SECRET_KEY", "Chicken")
USUARIO_ADMIN = os.getenv("USUARIO_ADMIN", "Amazon_platt")
SENHA_ADMIN = os.getenv("SENHA_ADMIN", "Umamusume123")

# Variável de controle de ambiente: 'local' ou 'produção'.
ambiente = os.getenv("AMBIENTE", "local")

if ambiente == "produção":
    # Em produção, leia as credenciais do ambiente (defina no PythonAnywhere)
    HOST = os.getenv("DB_HOST")
    USER = os.getenv("DB_USER")
    PASSWORD = os.getenv("DB_PASSWORD")
    DATABASE = os.getenv("DB_DATABASE")
else:
    # Defaults locais (usados no desenvolvimento)
    HOST = os.getenv("DB_HOST", "localhost")
    USER = os.getenv("DB_USER", "root")
    PASSWORD = os.getenv("DB_PASSWORD", "senai")
    DATABASE = os.getenv("DB_DATABASE", "blog_john")
