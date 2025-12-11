from flask import Flask, render_template, request, redirect, flash, session
from db import *
from werkzeug.security import generate_password_hash, check_password_hash
import mysql.connector
import os
from config import *


# --- Configuração ---

secret_key = SECRET_KEY
usuario_admin = USUARIO_ADMIN
senha_admin = SENHA_ADMIN


app = Flask(__name__)

app.secret_key = secret_key

app.config["UPLOAD_FOLDER"] = os.path.join(app.root_path, "static/uploads")

MAX_TITULO_LEN = 60

app.jinja_env.globals.update(obter_usuario=obter_usuario)

# Variável global não utilizada na versão final, mantida para compatibilidade
mensagem = ""

# --- Tratamento de Erros ---


@app.errorhandler(404)
def page_not_found(e):
    """Rota de tratamento de erro 404.
    Exibe a página de erro personalizada quando uma URL não é encontrada.
    """
    return render_template("e404.html"), 404


# --- Rotas Principais ---


@app.route("/")
def index():
    """Página inicial do blog. Busca as postagens via `listar_post()`.
    Renderiza o template principal, exibindo todas as postagens.
    """
    postagens = listar_post()
    # Busca o post mais "famoso" e o usuário com mais posts para a coluna direita
    try:
        post_mais_famoso = obter_post_mais_famoso()
    except Exception:
        post_mais_famoso = None

    try:
        usuario_mais_posts = obter_usuario_mais_posts()
    except Exception:
        usuario_mais_posts = None

    return render_template(
        "index.html",
        postagens=postagens,
        post_mais_famoso=post_mais_famoso,
        usuario_mais_posts=usuario_mais_posts,
    )


@app.route("/novopost", methods=["GET", "POST"])
def novopost():
    """Processa a criação de novas postagens.
    Requer autenticação e verifica se o usuário não está banido. No método POST, valida os dados e salva a nova postagem no banco.
    """
    # Requer que o usuário esteja logado
    if "idUsuario" not in session:
        flash("Você precisa estar logado para criar um novo post.")
        return redirect("/login")

    # Verifica se o usuário está banido
    usuario = obter_usuario(session["idUsuario"])
    if usuario and usuario.get("ativo", 1) == 0:
        flash("Você está banido e não pode postar.")
        return redirect("/")

    if request.method == "GET":
        return redirect("/")

    if request.method == "POST":
        try:
            titulo = request.form.get("titulo", "").strip()
            conteudo = request.form.get("conteudo", "").strip()

            if not titulo or not conteudo:
                flash("Por favor, preencha título e conteúdo antes de publicar.")
                return redirect("/")

            # Validação do tamanho do título
            if len(titulo) > MAX_TITULO_LEN:
                flash(
                    f"Título maior que {MAX_TITULO_LEN} caracteres. Por favor, reduza."
                )
                return redirect("/")

            idUsuario = session.get("idUsuario")

            post = adicionar_post(titulo, conteudo, idUsuario)
            if post:
                flash("Post realizado com sucesso!")
            else:
                flash("ERRO! Falha ao postar!")
        except Exception as e:
            print(f"Erro ao publicar post: {e}")
            flash("Erro inesperado ao postar. Verifique o servidor.")
        return redirect("/")


@app.route("/editarpost/<int:idPost>", methods=["GET", "POST"])
def editarpost(idPost):
    """Permite ao autor logado editar o conteúdo de sua postagem.
    Faz a checagem de autoria e, se for o autor, permite visualizar (GET) ou salvar (POST) as alterações.
    """
    # Requer que o usuário esteja logado
    if "idUsuario" not in session:
        flash("Você precisa estar logado para editar um post.")
        return redirect("/login")

    # Verifica se o usuário está banido
    usuario_logado = obter_usuario(session["idUsuario"])
    if usuario_logado and usuario_logado.get("ativo", 1) == 0:
        flash("Você está banido e não pode editar posts.")
        return redirect("/")

    """Permite ao autor editar sua postagem, checando a autoria."""
    idUsuario_logado = session.get("idUsuario")

    # Checagem de autoria
    with conectar() as conexao:
        cursor = conexao.cursor(dictionary=True)
        # Busca o ID do autor da postagem.
        cursor.execute("SELECT idUsuario FROM post WHERE idPost = %s", (idPost,))
        autor = cursor.fetchone()

        # Bloqueia se o post não existir ou o usuário logado não for o autor.
        if not autor or autor["idUsuario"] != idUsuario_logado:
            flash("Você não tem permissão para editar esta postagem.")
            return redirect("/")

    # Rota GET: carrega o post para o formulário de edição.
    if request.method == "GET":
        try:
            with conectar() as conexao:
                cursor = conexao.cursor(dictionary=True)
                cursor.execute("SELECT * FROM post WHERE idPost = %s", (idPost,))
                post = cursor.fetchone()
                postagens = listar_post()
                return render_template("index.html", postagens=postagens, post=post)
        except mysql.connector.Error as erro:
            print(f"ERRO DE BD! Erro: {erro}")
            flash("Houve um erro! Tente mais tarde!")
            return redirect("/")

    # Rota POST: salva as alterações no banco.
    if request.method == "POST":
        titulo = request.form["titulo"].strip()
        conteudo = request.form["conteudo"].strip()
        if not titulo or not conteudo:
            flash("Preencha todos os campos")
            return redirect(f"/editarpost/{idPost}")
        try:
            with conectar() as conexao:
                cursor = conexao.cursor()
                sql = "UPDATE post SET titulo = %s, conteudo = %s WHERE idPost = %s"
                cursor.execute(sql, (titulo, conteudo, idPost))
                conexao.commit()
                flash("Post editado com sucesso!")
                return redirect("/")
        except mysql.connector.Error as erro:
            print(f"ERRO DE DATABASE!! Erro: {erro}")
            conexao.rollback()
            flash("Erro ao atualizar o post! Tente novamente mais tarde.")
            return redirect(f"/")


@app.route("/excluirpost/<int:idPost>")
def excluirpost(idPost):
    """Rota para exclusão de post.
    Verifica se o usuário logado é o autor da postagem OU se é um administrador. Realiza a exclusão física do post.
    """
    # Bloqueia se não houver usuário logado
    if not session:
        return redirect("/")

    try:
        with conectar() as conexao:
            cursor = conexao.cursor(dictionary=True)

            # Lógica para usuário COMUM (não admin)
            if "admin" not in session:
                # Busca o autor para checar se é o usuário logado.
                cursor.execute(f"SELECT idUsuario FROM post WHERE idPost = {idPost}")
                autor_post = cursor.fetchone()

                # Impede a exclusão se não for o autor.
                if not autor_post or autor_post["idUsuario"] != session.get(
                    "idUsuario"
                ):
                    flash("Tentativa de exclusão inválida!")
                    return redirect("/")

            # Executa a exclusão (autor ou admin)
            cursor.execute(f"DELETE FROM post WHERE idPost = {idPost}")
            conexao.commit()
            flash("Post excluído com sucesso!")

            # Redirecionamento condicional
            if "admin" in session:
                return redirect("/dashboard")
            else:
                return redirect("/")

    except mysql.connector.Error as erro:
        print(f"ERRO DE DATABASE!! Erro: {erro}")
        conexao.rollback()
        flash("Erro ao excluir post. Tente novamente.")
        return redirect("/")


@app.route("/login", methods=["GET", "POST"])
def login():
    """Rota de autenticação de usuários e admin.
    Verifica as credenciais do administrador (via .env) e dos usuários comuns (via banco de dados).
    Cria a sessão e checa por status de banimento ou necessidade de reset de senha.
    """
    if request.method == "GET":
        return render_template("login.html")

    elif request.method == "POST":
        usuario = request.form["username"].strip().lower()
        senha = request.form["password"].strip()

        # 1. Checagem do Admin (via variáveis de ambiente)
        env_admin = (usuario_admin or "").strip().lower()
        if usuario == env_admin and senha == (senha_admin or ""):
            session["admin"] = True
            return redirect("/dashboard")

        # 2. Checagem do Usuário Comum (via banco de dados)
        resultado, usuario_encontrado = verificar_usuario(usuario, senha)
        if resultado:
            # Verifica se o usuário está banido
            if usuario_encontrado.get("ativo", 1) == 0:
                flash(
                    "Sua conta está banida. Você pode visualizar o conteúdo mas não pode postar ou editar informações."
                )
                return redirect("/login")

            session["idUsuario"] = usuario_encontrado["idUsuario"]
            session["usuario"] = usuario_encontrado["user"]
            session["foto"] = usuario_encontrado["foto"]

            # Lógica de alteração de senha padrão (reset obrigatório)
            if usuario_encontrado.get("reset_obrigatorio", 0) == 1:
                flash(
                    "Por motivos de segurança, altere sua senha que está como padrão '1234'."
                )
                return redirect("/reset_password")

            return redirect("/")

        flash("Usuário ou senha incorretos!")
        return redirect("/login")


@app.route("/reset_password", methods=["GET", "POST"])
def reset_password():
    """Permite ao usuário logado alterar sua própria senha.
    Requer a senha atual, a menos que o flag `reset_obrigatorio` esteja ativo (pós-reset de admin).
    Atualiza a senha no banco com novo hash e desativa o flag de reset obrigatório.
    """

    if "idUsuario" not in session:
        flash("Você precisa estar logado para alterar sua senha.")
        return redirect("/login")

    idUsuario = session["idUsuario"]
    usuario = obter_usuario(idUsuario)

    if not usuario:
        flash("Erro ao carregar informações do usuário.")
        return redirect("/logout")

    reset_obrigatorio = usuario.get("reset_obrigatorio", 0)

    if request.method == "GET":
        return render_template(
            "reset_password.html", usuario=usuario, reset_obrigatorio=reset_obrigatorio
        )

    if request.method == "POST":
        senha_atual = request.form.get("current_password", "").strip()
        nova_senha = request.form.get("new_password", "").strip()
        confirmar_senha = request.form.get("confirm_new_password", "").strip()

        if not nova_senha or not confirmar_senha:
            flash("Por favor, preencha a nova senha e a confirmação.")
            return redirect("/reset_password")

        if nova_senha != confirmar_senha:
            flash("A nova senha e a confirmação não coincidem.")
            return redirect("/reset_password")

        if len(nova_senha) < 4:
            flash("A nova senha deve ter no mínimo 4 caracteres.")
            return redirect("/reset_password")

        if not reset_obrigatorio:
            if not senha_atual:
                flash("Por favor, preencha a senha atual para alteração.")
                return redirect("/reset_password")

            if not check_password_hash(usuario["senha"], senha_atual):
                flash("A senha atual fornecida está incorreta.")
                return redirect("/reset_password")

        nova_senha_hash = generate_password_hash(nova_senha)

        # Atualiza a senha no banco (deve zerar o flag reset_obrigatorio)
        sucesso = alterar_senha(nova_senha_hash, idUsuario)

        if sucesso:
            flash("Senha alterada com sucesso!")
            if "usuario" in session:
                return redirect("/perfil")
            # Limpa a sessão para forçar o re-login com a nova senha
            session.clear()
            return redirect("/login")
        else:
            flash("Erro ao atualizar a senha no banco de dados. Tente novamente.")
            return redirect("/reset_password")


@app.route("/usuario/reset/<int:idUsuario>", methods=["POST"])
def reset_senha_usuario(idUsuario):
    """Permite ao administrador resetar a senha de um usuário.
    Esta rota aceita apenas requisições POST (chamada via fetch/ajax no dashboard).
    """
    if not session.get("admin"):
        flash("Acesso não autorizado.")
        return redirect("/")
    # Executa o reset mediante POST
    from werkzeug.security import generate_password_hash

    senha_padrao = generate_password_hash("1234")

    sucesso = reset_senha(idUsuario, senha_padrao)

    if sucesso:
        flash(
            "Senha redefinida com sucesso para '1234'. O usuário deve alterar na próxima vez que fizer login."
        )
    else:
        flash("Erro ao redefinir a senha do usuário!")

    # Como esta rota é chamada via JS, retornamos um redirecionamento para a dashboard.
    return redirect("/dashboard")


@app.route("/dashboard")
def dashborard():
    """Dashboard de Administração.
    Requer autenticação de administrador. Exibe listas de usuários e posts, além de totais estatísticos.
    """
    # 1. Checagem de Admin
    if "admin" not in session:
        flash("Acesso não autorizado.")
        return redirect("/")

    # 2. Chamada Corrigida: Usar listar_usuarios() em vez de obter_usuario() sem argumentos
    try:
        # Se a intenção é listar todos, você deve chamar a função correta (ex: listar_usuarios)
        # O nome da variável 'usuarios' no plural confirma que a intenção era listar todos.
        usuarios = listar_usuarios()
    except NameError:
        # Caso a função listar_usuarios não esteja definida ou importada
        print(
            "Erro: A função listar_usuarios não foi encontrada. Certifique-se de importá-la do db.py."
        )
        usuarios = []  # Lista vazia para evitar mais erros

    # 3. Obter totais (posts e usuarios) via função interna `totais()` se disponível
    try:
        total_posts, total_usuarios = totais()
    except Exception:
        total_posts, total_usuarios = None, None

    # Garantir formatos compatíveis com o template (que usa index [0])
    if total_posts is None:
        total_posts = (0,)
    if total_usuarios is None:
        total_usuarios = (0,)

    # 4. Obter lista de posts para exibir na coluna de Posts
    try:
        posts = listar_post()
    except Exception:
        posts = []

    # 5. Renderização: passar todas as variáveis necessárias ao template
    return render_template(
        "dashboard.html",
        usuarios=usuarios,
        posts=posts,
        total_posts=total_posts,
        total_usuarios=total_usuarios,
    )


@app.route("/excluirusuario/<int:idUsuario>")
def excluirusuario(idUsuario):
    """Alterna o status de um usuário entre ativo (1) e inativo (0 - banido).
    Ação restrita ao administrador. Impede que o admin altere seu próprio status.
    """
    # Apenas admin pode alterar status de usuários
    if not session or "admin" not in session:
        return redirect("/")

    try:
        usuario = obter_usuario(idUsuario)
        if not usuario:
            flash("Usuário não encontrado.")
            return redirect("/dashboard")

        # Evitar que o admin altere o status de si mesmo.
        if usuario.get("idUsuario") == session.get("idUsuario"):
            flash("Você não pode banir/reativar seu próprio usuário.")
            return redirect("/dashboard")

        # Inverte o status: se 1, vai para 0 (banir). Se 0, vai para 1 (reativar).
        sucesso = alterar_status(idUsuario)
        if sucesso:
            usuario_atualizado = obter_usuario(idUsuario)
            novo_status = usuario_atualizado.get("ativo", 1)
            # Feedback baseado no novo status.
            if novo_status == 0:
                flash("Usuário banido com sucesso!")
            else:
                flash("Usuário reativado com sucesso!")
        else:
            flash("Falha ao atualizar status do usuário. Confira os logs.")

    except Exception as e:
        print(f"Erro ao atualizar status do usuario: {e}")
        flash("Ocorreu um erro ao tentar atualizar o usuário.")

    return redirect("/dashboard")


@app.route("/logout")
def logout():
    """Limpa todos os dados da sessão do usuário logado (incluindo admin) e redireciona para a página inicial."""
    session.clear()
    return redirect("/")


@app.route("/signin", methods=["GET", "POST"])
def signin():
    """Rota para registro de novos usuários.
    No método POST, pega os dados do formulário, gera o hash seguro da senha e tenta adicionar o usuário ao banco de dados. Trata erros de duplicidade (usuário/email existente).
    """
    if request.method == "GET":
        return render_template("signin.html")

    elif request.method == "POST":
        # Pega e sanitiza os dados do formulário.
        nome = request.form.get("nome", "").strip()
        usuario = request.form.get("username", "").strip()
        email = request.form.get("email", "").strip()
        senha = request.form.get("password", "")

        if not nome or not usuario or not email or not senha:
            flash("Preencha todos os campos!")
            return redirect("/signin")

        # Gera o hash seguro da senha.
        senha_hash = generate_password_hash(senha)

        resultado, erro = adicionar_usuario(nome, usuario, email, senha_hash)

        if resultado:
            flash("Usuário cadastrado com sucesso!")
            return redirect("/login")
        else:
            # Trata erro de duplicidade (MySQL 1062).
            if erro.errno == 1062:
                flash("Usuário ou email existente! Tente outro.")
            else:
                flash(f"Erro ao cadastrar usuário! Detalhes: {erro}")
            return redirect("/signin")


@app.route("/perfil", methods=["GET", "POST"])
def perfil():
    """Permite ao usuário logado visualizar (GET) e editar (POST) seus dados de perfil.
    Gerencia a atualização do nome, nome de usuário e o upload/troca de foto de perfil, validando o arquivo.
    """
    if "idUsuario" not in session:
        return redirect("/")

    idUsuario = session["idUsuario"]
    # Obtém o usuário mais recente do banco (assumindo que obter_usuario faz isso)
    usuario = obter_usuario(idUsuario)

    if usuario is None:
        flash("Erro: Usuário não encontrado.")
        return redirect("/logout")

    if request.method == "GET":
        usuario["foto"] = usuario.get("foto") or "default.jpg"
        return render_template("perfil.html", usuario=usuario)

    # --- Rota POST: Atualizar Perfil ---
    if request.method == "POST":
        nome = request.form["nome"]
        user = request.form["user"]
        foto_file = request.files.get("foto")
        nome_foto = usuario.get("foto") or "default.jpg"

        if not nome or not user:
            flash("Os campos Nome e User não podem estar vazios!")
            return redirect("/perfil")

        # Processamento de upload de foto
        if foto_file and foto_file.filename != "":

            # Validação da extensão
            extensao = foto_file.filename.rsplit(".", 1)[-1].lower()
            if extensao not in ("png", "jpg", "webp"):
                flash("Extensão inválida! Use png, jpg ou webp.")
                return redirect("/perfil")

            # Validação de tamanho (máx. 2MB)
            foto_file.seek(0)
            if len(foto_file.read()) > 2 * 1024 * 1024:
                flash("Arquivo acima de 2MB não é aceito!")
                return redirect("/perfil")

            # Salvar a foto
            foto_file.seek(0)
            nome_foto = f"{idUsuario}.{extensao}"
            caminho_completo = os.path.join(app.config['UPLOAD_FOLDER'], nome_foto)
            foto_file.save(caminho_completo)

        # Se não houve upload e não havia foto anterior, usa o default
        if not nome_foto:
            nome_foto = "default_user.jpg"

        # Atualiza o perfil no banco de dados
        sucesso = editar_perfil(nome, user, nome_foto, idUsuario)

        if sucesso:
            flash("Dados atualizados com sucesso!")
        else:
            flash("Erro ao atualizar dados!")

        return redirect("/perfil")


# --- Handlers de Erros Adicionais ---


@app.errorhandler(500)
def page_internal_error(error):
    """Handler para erro 500 - Erro Interno do Servidor.
    Exibe uma página de erro genérica para falhas internas.
    """
    return render_template("e500.html")


@app.route("/status")
def verificar_status():
    """Endpoint para verificar o status de banimento do usuário logado.
    Retorna JSON indicando se o usuário está 'ativo', 'banido' ou 'nao_logado'.
    """
    if "idUsuario" in session:
        usuario = obter_usuario(session["idUsuario"])
        if usuario and usuario.get("ativo", 1) == 0:
            return {
                "status": "banido",
                "mensagem": "Você está banido e não pode postar ou editar informações.",
            }
        return {"status": "ativo"}
    return {"status": "nao_logado"}


@app.route("/alterar_status/<int:idUsuario>")
def alterar_status(idUsuario):
    """Altera o status de um usuário entre ativo e banido.
    Ação restrita ao administrador.
    """
    # Apenas admin pode alterar status
    if not session or "admin" not in session:
        return redirect("/")

    try:
        with conectar() as conexao:
            cursor = conexao.cursor(dictionary=True)

            # Evitar que o admin altere seu próprio status.
            if idUsuario == session.get("idUsuario"):
                flash("Você não pode alterar seu próprio status.")
                return redirect("/dashboard")

            # Obter o status atual do usuário
            cursor.execute(
                "SELECT ativo FROM usuario WHERE idUsuario = %s", (idUsuario,)
            )
            usuario = cursor.fetchone()
            if not usuario:
                flash("Usuário não encontrado.")
                return redirect("/dashboard")

            novo_status = 0 if usuario["ativo"] else 1
            cursor.execute(
                "UPDATE usuario SET ativo = %s WHERE idUsuario = %s",
                (novo_status, idUsuario),
            )
            conexao.commit()
            flash("Status do usuário atualizado com sucesso!")
    except mysql.connector.Error as erro:
        print(f"ERRO DE DATABASE!! Erro ao alterar status do usuário: {erro}")
        conexao.rollback()
        flash("Falha ao alterar o status do usuário.")

    return redirect("/dashboard")


@app.route("/editaremail", methods=["GET", "POST"])
def editaremail():
    """Permite ao usuário logado editar seu email.
    Verifica se o usuário está logado e não banido. No método POST, valida o novo email e o atualiza no banco de dados.
    """
    # Verifica se o usuário está logado
    if "idUsuario" not in session:
        flash("Você precisa estar logado para editar seu email.")
        return redirect("/login")

    # Verifica se o usuário está banido
    usuario = obter_usuario(session["idUsuario"])
    if usuario and usuario.get("ativo", 1) == 0:
        flash("Você está banido e não pode editar suas informações.")
        return redirect("/")

    if request.method == "GET":
        return render_template("editaremail.html", usuario=usuario)

    elif request.method == "POST":
        novo_email = request.form.get("email", "").strip()

        if not novo_email:
            flash("Email não pode estar vazio!")
            return redirect("/editaremail")

        try:
            with conectar() as conexao:
                cursor = conexao.cursor()
                sql = "UPDATE usuario SET email = %s WHERE idUsuario = %s"
                cursor.execute(sql, (novo_email, session["idUsuario"]))
                conexao.commit()
                flash("Email atualizado com sucesso!")
                return redirect("/")
        except mysql.connector.Error as erro:
            print(f"ERRO DE DATABASE!! Erro ao atualizar email: {erro}")
            conexao.rollback()
            flash("Erro ao atualizar email. Tente novamente.")
            return redirect("/editaremail")


@app.route("/usuario/excluir/<int:idUsuario>")
def excluir_usuario(idUsuario):
    """Remove um usuário pelo id (DELETE físico) do banco de dados.
    Ação restrita ao administrador. Impede que o admin exclua sua própria conta.
    """
    # Apenas admin pode excluir usuários
    if not session or "admin" not in session:
        return redirect("/")

    try:
        with conectar() as conexao:
            cursor = conexao.cursor(dictionary=True)

            # Evitar que o admin exclua a si mesmo.
            if idUsuario == session.get("idUsuario"):
                flash("Você não pode excluir seu próprio usuário.")
                return redirect("/dashboard")

            cursor.execute(f"DELETE FROM usuario WHERE idUsuario = {idUsuario}")
            conexao.commit()
            flash("Usuário excluído permanentemente com sucesso!")
    except mysql.connector.Error as erro:
        print(f"ERRO DE DATABASE!! Erro ao excluir usuario: {erro}")
        conexao.rollback()
        flash("Falha ao excluir o usuário.")

    return redirect("/dashboard")


def totais():
    """Busca o total de posts e usuários do banco de dados.
    Utiliza views (`vw_total_posts` e `vw_usuarios`) para obter contagens estatísticas para o Dashboard.
    """
    try:
        with conectar() as conexao:
            cursor = conexao.cursor()
            cursor.execute("SELECT * FROM vw_total_posts")
            total_posts = cursor.fetchone()
            cursor.execute("SELECT * FROM vw_usuarios")
            total_usuarios = cursor.fetchone()
            return total_posts, total_usuarios
    except mysql.connector.Error as erro:
        print(f"ERRO DE DATABASE!! Erro: {erro}")
        return None, None


# --- Bloco Principal de Execução ---

if __name__ == "__main__":
    app.run(debug=True)
