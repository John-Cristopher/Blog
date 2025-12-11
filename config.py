SECRET_KEY = "Chicken"
USUARIO_ADMIN = "Amazon_platt"
SENHA_ADMIN = "Umamusume123"

# Variável de controle de ambiente, poderá ser "local" ou "produção"
ambiente = "local"

if ambiente == "local":
    # ------ INFORMAÇÕES VINDAS DO DATABASE DO PYTHON ANYWHERE
    HOST = "link python anywhere"
    USER = "user python anywhere"
    PASSWORD = "senha database python anywhere"
    DATABASE = "nome do database python anywhere"
else:
    # ------ INFORMAÇÕES DO SEU BLOG LOCAL, DEIXE COMO ESTÁ
    HOST = "localhost"
    USER = "root"
    PASSWORD = "senai"
    DATABASE = "blog_john"
