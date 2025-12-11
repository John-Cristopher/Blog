SECRET_KEY = "Chicken"
USUARIO_ADMIN = "Amazon_platt"
SENHA_ADMIN = "Umamusume123"

# Variável de controle de ambiente, poderá ser "local" ou "produção"
ambiente = "produção"

if ambiente == "local":
    # ------ INFORMAÇÕES DO SEU BLOG LOCAL, DEIXE COMO ESTÁ
    HOST = "localhost"
    USER = "root"
    PASSWORD = "senai"
    DATABASE = "blog_john"
elif ambiente == "produção":
    # ------ INFORMAÇÕES VINDAS DO DATABASE DO PYTHON ANYWHERE
    HOST = "JohnCristopher.mysql.pythonanywhere-services.com"
    USER = "JohnCristopher"
    PASSWORD = "GYMkhanaSuBaru8r477"
    DATABASE = "JohnCristopher$MidnightBlog"
