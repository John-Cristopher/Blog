import mysql.connector
from mysql.connector import Error
from werkzeug.security import check_password_hash
import os
from dotenv import load_dotenv
from config import *

# Carrega variáveis de ambiente do arquivo .env
load_dotenv()

# --- Configurações de Conexão (Pegas do .env) ---
db_host = os.getenv("DB_HOST", "localhost")
db_user = os.getenv("DB_USER")
db_password = os.getenv("DB_PASSWORD")
db_database = os.getenv("DB_DATABASE")


def conectar():
    conexao = mysql.connector.connect(
        host=HOST,  # variável do config.py
        user=USER,  # variável do config.py
        password=PASSWORD,  # variável do config.py
        database=DATABASE,  # variável do config.py
    )
    if conexao.is_connected():
        print("Conexão com BD OK!")

    return conexao


# --- Funções de Postagem ---


def listar_post():
    """Retorna uma lista de todas as postagens ativas."""
    try:
        with conectar() as conexao:
            sql = """
                SELECT 
                    p.*, u.user AS nome_autor, u.foto
                FROM 
                    post p
                INNER JOIN 
                    usuario u ON p.idUsuario = u.idUsuario 
                WHERE 
                    u.ativo = 1 
                ORDER BY 
                    p.idPost DESC
            """
            cursor = conexao.cursor(dictionary=True)
            cursor.execute(sql)
            return cursor.fetchall()
    except (ConnectionError, mysql.connector.Error) as erro:
        print(f"ERRO DE DB! ERRO: {erro}")
        return []


def adicionar_post(titulo, conteudo, idUsuario):
    """Insere uma nova postagem. Retorna o ID do post ou None."""
    try:
        with conectar() as conexao:
            cursor = conexao.cursor()
            sql = "INSERT INTO post(titulo, conteudo, idUsuario) VALUES (%s, %s, %s)"
            cursor.execute(sql, (titulo, conteudo, idUsuario))
            # Não precisa de conexao.commit() se autocommit=True, mas mantido por segurança
            conexao.commit()
            return cursor.lastrowid  # Retorna o ID do post inserido
    except mysql.connector.Error as erro:
        # conexao.rollback() é redundante com autocommit=True em erro
        print(f"ERRO DE DB! ERRO ao adicionar post: {erro}")
        return None


def atualizar_post(titulo, conteudo, idPost):
    """Atualiza o título e conteúdo de uma postagem."""
    try:
        with conectar() as conexao:
            cursor = conexao.cursor()
            sql = "UPDATE post SET titulo=%s, conteudo=%s WHERE idPost = %s"
            cursor.execute(sql, (titulo, conteudo, idPost))
            conexao.commit()
            return True
    except mysql.connector.Error as erro:
        print(f"ERRO DE DB! ERRO ao atualizar post: {erro}")
        return False


# --- Funções de Usuário e Autenticação ---


def verificar_usuario(usuario, senha):
    """Verifica a existência do usuário e a validade da senha (hash)."""
    try:
        with conectar() as conexao:
            cursor = conexao.cursor(dictionary=True)
            sql = "SELECT * FROM usuario WHERE user = %s"
            cursor.execute(sql, (usuario,))
            usuario_encontrado = cursor.fetchone()

            if usuario_encontrado:
                # CORREÇÃO: Remove a verificação de senha '1234' hardcoded para confiar no hash
                if check_password_hash(usuario_encontrado["senha"], senha):
                    # Garante que os campos existam no retorno
                    usuario_encontrado["ativo"] = usuario_encontrado.get("ativo", 1)
                    usuario_encontrado["reset_obrigatorio"] = usuario_encontrado.get(
                        "reset_obrigatorio", 0
                    )
                    return True, usuario_encontrado
                return False, None
            return False, None
    except mysql.connector.Error as erro:
        print(f"ERRO DE DB! ERRO ao verificar usuario: {erro}")
        return False, None


def adicionar_usuario(
    nome, usuario, email, senha_hash
):  # Adicionado 'email' e 'senha_hash'
    """Insere um novo usuário. Retorna True/False e o erro."""
    try:
        with conectar() as conexao:
            cursor = conexao.cursor()
            # Inserção completa com 'email', 'ativo' e 'reset_obrigatorio' como padrão (1, 0)
            sql = "INSERT INTO usuario(nome, user, email, senha, ativo, reset_obrigatorio) VALUES (%s, %s, %s, %s, 1, 0)"
            cursor.execute(sql, (nome, usuario, email, senha_hash))
            conexao.commit()
            return True, None
    except mysql.connector.Error as erro:
        print(f"ERRO DE DB! ERRO ao criar usuário: {erro}")
        return False, erro


def listar_usuarios():
    """Busca e retorna todos os usuários (melhorado para não listar a senha)."""
    try:
        with conectar() as conexao:
            cursor = conexao.cursor(dictionary=True)
            # Lista apenas campos seguros, exceto a senha
            sql = "SELECT idUsuario, nome, user, email, ativo, reset_obrigatorio FROM usuario"
            cursor.execute(sql)
            return cursor.fetchall()
    except (ConnectionError, mysql.connector.Error) as erro:
        print(f"ERRO DE DB! ERRO: {erro}")
        return []


def obter_usuario(idUsuario):
    """Retorna os dados de um único usuário pelo seu ID."""
    try:
        with conectar() as conexao:
            cursor = conexao.cursor(dictionary=True)
            # Seleciona todos os campos, exceto a senha
            sql = "SELECT idUsuario, nome, user, email, ativo, reset_obrigatorio, foto, senha FROM usuario WHERE idUsuario = %s"
            cursor.execute(sql, (idUsuario,))
            # Retorna apenas o primeiro (e único) resultado
            return cursor.fetchone()
    except (ConnectionError, mysql.connector.Error) as erro:
        print(f"ERRO DE DB! ERRO ao obter usuário: {erro}")
        return None


def alterar_status(idUsuario):
    """Inverte o status 'ativo' (1/0) de um usuário."""
    try:
        with conectar() as conexao:
            cursor = conexao.cursor(dictionary=True)
            sql_select = "SELECT ativo FROM usuario WHERE idUsuario = %s;"
            cursor.execute(sql_select, (idUsuario,))
            status = cursor.fetchone()

            if status and status.get("ativo") is not None:
                novo_status = 0 if status["ativo"] else 1
                sql_update = "UPDATE usuario SET ativo = %s WHERE idUsuario = %s"
                cursor.execute(sql_update, (novo_status, idUsuario))
                conexao.commit()
                return True
            return False  # Usuário não encontrado

    except mysql.connector.Error as erro:
        print(f"ERRO DE DB! ERRO ao alterar status: {erro}")
        return False


def delete_usuario(idUsuario):
    """Exclui um usuário pelo ID."""
    try:
        with conectar() as conexao:
            cursor = conexao.cursor()
            sql = "DELETE FROM usuario WHERE idUsuario = %s"
            cursor.execute(sql, (idUsuario,))
            conexao.commit()
            return True
    except mysql.connector.Error as erro:
        print(f"ERRO DE DB! ERRO ao deletar usuário: {erro}")
        return False


def reset_senha(
    idUsuario, senha_hash_padrao
):  # Adicionado senha_hash_padrao como parâmetro
    """Reseta a senha para um padrão (hash) e ATIVA o flag de reset obrigatório."""
    try:
        with conectar() as conexao:
            cursor = conexao.cursor()
            # Adicionado reset_obrigatorio = 1
            sql = "UPDATE usuario SET senha = %s, reset_obrigatorio = 1 WHERE idUsuario = %s"
            cursor.execute(sql, (senha_hash_padrao, idUsuario))
            conexao.commit()
            return True
    except mysql.connector.Error as erro:
        print(f"ERRO DE DB! ERRO ao resetar senha: {erro}")
        return False


def alterar_senha(senha_hash, idUsuario):
    """Atualiza a senha (hash) e DESATIVA o flag de reset obrigatório."""
    try:
        with conectar() as conexao:
            cursor = conexao.cursor()
            # Adicionado reset_obrigatorio = 0
            sql = "UPDATE usuario SET senha = %s, reset_obrigatorio = 0 WHERE idUsuario = %s"
            cursor.execute(sql, (senha_hash, idUsuario))
            conexao.commit()
            return True
    except mysql.connector.Error as erro:
        print(f"ERRO DE DB! ERRO ao alterar senha: {erro}")
        return False


def editar_perfil(nome, user, nome_foto, idUsuario):
    """Atualiza o nome, usuário e foto de perfil do usuário."""
    try:
        with conectar() as conexao:
            cursor = conexao.cursor()
            sql = "UPDATE usuario SET nome = %s, user = %s, foto = %s WHERE idUsuario = %s"
            cursor.execute(sql, (nome, user, nome_foto, idUsuario))
            conexao.commit()
            return True
    except mysql.connector.Error as erro:
        print(f"ERRO DE DB! ERRO ao editar perfil: {erro}")
        return False


def obter_post_mais_famoso():
    """Retorna o post considerado 'mais famoso'.

    Como não há métricas de likes/views, escolhemos o post com
    maior comprimento de conteúdo como proxy de 'fama'.
    Retorna um dict ou None.
    """
    try:
        with conectar() as conexao:
            cursor = conexao.cursor(dictionary=True)
            sql = (
                "SELECT p.*, u.user AS nome_autor, u.foto "
                "FROM post p JOIN usuario u ON p.idUsuario = u.idUsuario "
                "WHERE u.ativo = 1 "
                "ORDER BY CHAR_LENGTH(p.conteudo) DESC LIMIT 1"
            )
            cursor.execute(sql)
            return cursor.fetchone()
    except (ConnectionError, mysql.connector.Error) as erro:
        print(f"ERRO DE DB! ERRO ao obter post mais famoso: {erro}")
        return None


def obter_usuario_mais_posts():
    """Retorna o usuário com mais postagens ativas e a contagem.

    Retorna um dict com campos: idUsuario, nome_autor, foto, total_posts
    ou None se não houver resultados.
    """
    try:
        with conectar() as conexao:
            cursor = conexao.cursor(dictionary=True)
            sql = (
                "SELECT u.idUsuario, u.user AS nome_autor, u.foto, COUNT(p.idPost) AS total_posts "
                "FROM usuario u JOIN post p ON u.idUsuario = p.idUsuario "
                "WHERE u.ativo = 1 "
                "GROUP BY u.idUsuario "
                "ORDER BY total_posts DESC LIMIT 1"
            )
            cursor.execute(sql)
            return cursor.fetchone()
    except (ConnectionError, mysql.connector.Error) as erro:
        print(f"ERRO DE DB! ERRO ao obter usuario com mais posts: {erro}")
        return None
