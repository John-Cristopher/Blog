
---
# 📝 Projeto — Blog em Flask (Resumo e Documentação)

## 📌 Resumo Rápido

Este projeto é uma aplicação Flask simples que funciona como um blog:

-   Exibe postagens (`/`).
-   Permite criar, editar e excluir posts.
-   Possui autenticação básica para área administrativa (`/login`, `/dashboard`).
-   Faz registro de usuários com hashing de senha.
-   Utiliza **MySQL** (arquivo `db.py`).
-   Usa templates Jinja2 (pasta `templates/`).
-   Backend principal em **app.py**.

---

# 📂 app.py — Explicação Geral (Linha a Linha)

## ✅ Imports

-   `Flask`, `render_template`, `request`, `redirect`, `flash`, `session`: funcionalidades centrais do Flask.
-   `from db import *`: importa todas as funções de acesso ao banco (listar posts, criar usuário, etc.).
-   `werkzeug.security`: `generate_password_hash`, `check_password_hash` — hashing de senha.
-   `mysql.connector`: tratamento de erros do MySQL.
-   `dotenv`: `load_dotenv()` para carregar variáveis de ambiente.
-   `os`: acesso às variáveis do sistema.

---

## ✅ Configurações Iniciais

-   `load_dotenv()` → carrega variáveis do `.env`.
-   `app = Flask(__name__)`
-   `app.secret_key = SECRET_KEY`
-   `MAX_TITULO_LEN = 60` → validação do tamanho do título.
-   `mensagem = ""` → **não utilizada**, pode ser removida.

---

## ✅ Rota `/` — Página Inicial

-   Carrega postagens via `listar_post()`.
-   Renderiza `index.html` enviando `postagens`.

---

## ✅ Rota `/novopost` — Criar Post

-   GET → redireciona para `/`.
-   POST:

    -   Valida título e conteúdo.
    -   Trunca título > 60 caracteres.
    -   `idUsuario = 3` **hardcoded** (melhor substituir por `session` no futuro).
    -   Executa `adicionar_post`.
    -   Redireciona com `flash`.

---

## ✅ Rota `/editarpost/<idPost>`

-   GET → carrega post específico e renderiza `index.html` com formulário de edição.
-   POST → faz `UPDATE` no banco e redireciona.

---

## ✅ Rota `/excluirpost/<idPost>`

-   Executa `DELETE`.
-   Redireciona com `flash`.

---

## ✅ Rota `/login`

-   GET: exibe `login.html`.
-   POST:

    -   Compara username/senha com variáveis do `.env`.
    -   Se bater, salva `session['admin'] = True`.
    -   Redireciona para `/dashboard`.

---

## ✅ Rota `/dashboard`

-   Requer admin logado.
-   Carrega:

    -   `usuarios = listar_usuarios()`
    -   `posts = listar_post()`

-   Renderiza `dashboard.html`.

---

## ✅ Rota `/logout`

-   `session.clear()`
-   Redireciona para `/`.

---

## ✅ Rota `/signin`

-   GET: exibe `signin.html`.
-   POST:

    -   Recebe nome, username, email, senha.
    -   Valida campos.
    -   Cria hash: `generate_password_hash`.
    -   Chama `criar_usuario`.
    -   Redireciona para `/login` com flash.

---

## ✅ Execução

```python
if __name__ == "__main__":
    app.run(debug=True)
```

---

# ✅ Melhorias Recomendadas para `app.py`

-   Remover variável global `mensagem`.
-   Substituir `idUsuario = 3` por ID real do usuário logado.
-   Login real de usuários (via banco) e não apenas admin estático.
-   Usar `check_password_hash` no login real.
-   Logs estruturados (não usar apenas `print`).
-   Evitar `from db import *` → prefira imports específicos.
-   Proteger rotas de edição/exclusão.
-   Implementar CSRF.
-   Trocar `../static/...` por `url_for('static', ...)`.

---

# 📂 db.py — Explicação das Funções

Arquivo responsável pelo acesso ao MySQL e operações CRUD.

## ✅ `conectar()`

-   Conecta ao banco:

    -   host: `"localhost"`
    -   user: `"root"`
    -   password: `"senai"`
    -   database: `"blog_john"`

-   Retorna objeto de conexão.

**Melhorias:**

-   Mover credenciais para `.env`.
-   Usar connection pooling.

---

## ✅ `listar_post()`

Executa:

```sql
SELECT p.*, u.user, u.foto
FROM post p
INNER JOIN usuario u ON u.idUsuario = p.idUsuario
ORDER BY idPost DESC
```

Retorna lista de dicionários contendo:

-   idPost
-   titulo
-   conteudo
-   idUsuario
-   dataPost (datetime)
-   user
-   foto

⚠️ **Importante:** `dataPost` deve vir como datetime para o template usar `.strftime()`.

---

## ✅ `listar_usuarios()`

`SELECT * FROM usuario`.

Retorna lista de dicionários:

-   idUsuario
-   nome
-   user
-   email
-   senha (hash)

---

## ✅ `adicionar_post(titulo, conteudo, idUsuario)`

`INSERT INTO post (...)`
Retorna `True` ou `False`.

---

## ✅ `criar_usuario(nome, user, email, senha_hash)`

`INSERT INTO usuario (...)`

⚠️ O código não verifica duplicidade (username/email).

---

## ✅ `buscar_usuario_por_user(user)`

Retorna:

-   dicionário com dados do usuário
    ou
-   `None`

---

# ✅ Melhorias Recomendadas para `db.py`

-   Usar variáveis de ambiente.
-   Verificar duplicidade antes de `INSERT`.
-   Usar logs estruturados.
-   Colocar docstrings e tipos.
-   Validar uploads de imagens (caso existam).

---

# 🎨 Templates Jinja — Função e Variáveis

## ✅ base.html

-   Header + navbar.
-   Verifica `session` e `session['admin']`.
-   Carrega CSS.
-   Define bloco `{% block conteudo %}`.

---

## ✅ index.html

Recebe:

-   `postagens`
-   opcionalmente `post` (quando editando)

Possui:

-   Formulário de novo post **ou** edição.
-   Feed de postagens com:

    -   imagem do autor
    -   nome do user
    -   data (`strftime`)
    -   título
    -   conteúdo
    -   links de editar/excluir

---

## ✅ dashboard.html

Recebe:

-   `usuarios`
-   `posts`

Exibe lista com truncamento do conteúdo (`truncate(35)`).

---

## ✅ login.html

Formulário de login + flashes.

---

## ✅ signin.html

Formulário de cadastro + flashes.

---

# ⚠️ Pontos de Segurança Importantes

-   Credenciais do DB **hardcoded** (mover para `.env`).
-   Administração baseada apenas em variáveis fixas.
-   Sem login real de usuários do banco.
-   **Rotas sensíveis sem validação de autor** → qualquer usuário pode tentar editar/excluir posts.
-   Nenhuma proteção CSRF.
-   Falta de sanitização mais rigorosa nas entradas.
-   Falta de logging adequado.

---

# 📘 Contratos de Funções (Formato de Dados)

### **listar_post() → List[Dict]**

```json
{
  "idPost": int,
  "titulo": "str",
  "conteudo": "str",
  "idUsuario": int,
  "dataPost": "datetime",
  "user": "str",
  "foto": "str"
}
```

### **adicionar_post(titulo, conteudo, idUsuario) → bool**

### **criar_usuario(nome, user, email, senha_hash) → bool**

### **buscar_usuario_por_user(user) → dict | None**

---
