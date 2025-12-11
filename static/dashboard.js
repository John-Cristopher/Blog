// ===== SISTEMA DE DROPDOWN =====
document.addEventListener('DOMContentLoaded', function () {
    const btnDropdowns = document.querySelectorAll('.btn-dropdown');

    btnDropdowns.forEach(btn => {
        btn.addEventListener('click', function (e) {
            e.stopPropagation();
            const dropdown = this.nextElementSibling;

            // Fechar todos os dropdowns abertos
            document.querySelectorAll('.dropdown-content').forEach(d => {
                if (d !== dropdown) d.classList.remove('show');
            });

            // Toggle do dropdown atual
            dropdown.classList.toggle('show');
        });
    });

    // Fechar dropdown ao clicar em um item
    document.querySelectorAll('.dropdown-item').forEach(item => {
        item.addEventListener('click', function () {
            this.closest('.dropdown-content').classList.remove('show');
        });
    });

    // Fechar dropdown ao clicar fora
    document.addEventListener('click', function () {
        document.querySelectorAll('.dropdown-content').forEach(d => {
            d.classList.remove('show');
        });
    });
});

// ===== MODAL DE CONFIRMAÇÃO =====
const modal = document.getElementById('modalConfirmacao');
const closeBtn = document.querySelector('.close');
const btnCancelar = document.getElementById('btnCancelar');
const btnConfirmar = document.getElementById('btnConfirmar');
const modalTitulo = document.getElementById('modalTitulo');
const modalMensagem = document.getElementById('modalMensagem');

let acaoAtual = null;

function abrirModal(titulo, mensagem, callback) {
    modalTitulo.textContent = titulo;
    modalMensagem.textContent = mensagem;
    acaoAtual = callback;
    modal.style.display = 'block';
}

function fecharModal() {
    modal.style.display = 'none';
    acaoAtual = null;
}

closeBtn.addEventListener('click', fecharModal);
btnCancelar.addEventListener('click', fecharModal);
btnConfirmar.addEventListener('click', function () {
    if (acaoAtual) {
        acaoAtual();
    }
    fecharModal();
});

window.addEventListener('click', function (event) {
    if (event.target === modal) {
        fecharModal();
    }
});

// ===== FUNÇÕES DE CONFIRMAÇÃO PARA USUÁRIOS =====
function confirmarBanimento(idUsuario, nomeUsuario) {
    abrirModal(
        '⚠️ Confirmar Banimento',
        `Tem certeza de que deseja banir o usuário "${nomeUsuario}"?\n\nEle não poderá acessar a plataforma até ser reativado.`,
        function () {
            window.location.href = `/excluirusuario/${idUsuario}`;
        }
    );
}

function confirmarReativacao(idUsuario, nomeUsuario) {
    abrirModal(
        '✓ Confirmar Reativação',
        `Tem certeza de que deseja reativar o usuário "${nomeUsuario}"?\n\nEle poderá acessar a plataforma novamente.`,
        function () {
            window.location.href = `/excluirusuario/${idUsuario}`;
        }
    );
}

function confirmarExclusao(idUsuario, nomeUsuario) {
    abrirModal(
        '🗑️ Confirmar Exclusão',
        `Tem certeza de que deseja EXCLUIR permanentemente o usuário "${nomeUsuario}"?\n\nEsta ação é IRREVERSÍVEL e não poderá ser desfeita.`,
        function () {
            window.location.href = `/usuario/excluir/${idUsuario}`;
        }
    );
}

function confirmarResetSenha(idUsuario, nomeUsuario) {
    abrirModal(
        '🔑 Confirmar Reset de Senha',
        `Tem certeza de que deseja redefinir a senha do usuário "${nomeUsuario}"?\n\nA nova senha será "1234" e ele será obrigado a alterá-la no próximo acesso.`,
        function () {
            // Faz uma requisição POST para resetar a senha (mantém segurança via sessão)
            fetch(`/usuario/reset/${idUsuario}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                credentials: 'same-origin'
            })
                .then(response => {
                    // Após a ação, recarrega a dashboard para ver a mudança e flashes
                    window.location.href = '/dashboard';
                })
                .catch(err => {
                    console.error('Erro ao resetar senha:', err);
                    window.location.href = '/dashboard';
                });
        }
    );
}

// ===== FUNÇÕES DE CONFIRMAÇÃO PARA POSTS =====
function confirmarEditPost(idPost, titulo) {
    abrirModal(
        '✏️ Editar Post',
        `Você está prestes a editar o post "${titulo}".\n\nClique em confirmar para continuar.`,
        function () {
            window.location.href = `/editarpost/${idPost}`;
        }
    );
}

function confirmarExcluirPost(idPost, titulo) {
    abrirModal(
        '🗑️ Confirmar Exclusão de Post',
        `Tem certeza de que deseja EXCLUIR o post "${titulo}"?\n\nEsta ação é IRREVERSÍVEL.`,
        function () {
            window.location.href = `/excluirpost/${idPost}`;
        }
    );
}

// ===== BUSCA, FILTRO E PAGINAÇÃO =====
const PAGE_SIZE = 20;

document.addEventListener('DOMContentLoaded', function () {
    // Usuários
    const buscaUsuariosInput = document.getElementById('buscaUsuarios');
    const filtroStatusSelect = document.getElementById('filtroStatus');

    // Posts
    const buscaPostsInput = document.getElementById('buscaPosts');

    // Estado de paginação
    let currentPageUsuarios = 1;
    let currentPagePosts = 1;

    function getUsuarioRows() {
        return Array.from(document.querySelectorAll('.usuario-row'));
    }

    function getPostRows() {
        return Array.from(document.querySelectorAll('.post-row'));
    }

    function filterUsuarios() {
        const q = (buscaUsuariosInput && buscaUsuariosInput.value || '').trim().toLowerCase();
        const statusFilter = (filtroStatusSelect && filtroStatusSelect.value);

        const rows = getUsuarioRows();
        const filtered = rows.filter(r => {
            const nome = r.dataset.nome || '';
            const user = r.dataset.user || '';
            const email = r.dataset.email || '';
            const ativo = r.dataset.ativo;

            if (statusFilter !== '' && String(ativo) !== String(statusFilter)) return false;

            if (!q) return true;
            return nome.includes(q) || user.includes(q) || email.includes(q) || String(r.dataset.id).includes(q);
        });

        // esconder todos e só mostrar os filtrados de acordo com paginação
        rows.forEach(r => r.style.display = 'none');

        const totalPages = Math.max(1, Math.ceil(filtered.length / PAGE_SIZE));
        if (currentPageUsuarios > totalPages) currentPageUsuarios = totalPages;

        const start = (currentPageUsuarios - 1) * PAGE_SIZE;
        const end = start + PAGE_SIZE;
        filtered.slice(start, end).forEach(r => r.style.display = 'table-row');

        // atualizar UI de paginação
        const paginaAtualEl = document.getElementById('paginaAtualUsuarios');
        const totalPaginasEl = document.getElementById('totalPaginasUsuarios');
        if (paginaAtualEl) paginaAtualEl.textContent = currentPageUsuarios;
        if (totalPaginasEl) totalPaginasEl.textContent = totalPages;

        const btnPrev = document.getElementById('btnAnteriorUsuarios');
        const btnNext = document.getElementById('btnProximoUsuarios');
        if (btnPrev) btnPrev.disabled = currentPageUsuarios <= 1;
        if (btnNext) btnNext.disabled = currentPageUsuarios >= totalPages;
    }

    function filterPosts() {
        const q = (buscaPostsInput && buscaPostsInput.value || '').trim().toLowerCase();
        const rows = getPostRows();
        const filtered = rows.filter(r => {
            const titulo = r.dataset.titulo || '';
            const id = String(r.dataset.id || '');
            if (!q) return true;
            return titulo.includes(q) || id.includes(q);
        });

        rows.forEach(r => r.style.display = 'none');

        const totalPages = Math.max(1, Math.ceil(filtered.length / PAGE_SIZE));
        if (currentPagePosts > totalPages) currentPagePosts = totalPages;

        const start = (currentPagePosts - 1) * PAGE_SIZE;
        const end = start + PAGE_SIZE;
        filtered.slice(start, end).forEach(r => r.style.display = 'table-row');

        const paginaAtualEl = document.getElementById('paginaAtualPosts');
        const totalPaginasEl = document.getElementById('totalPaginasPosts');
        if (paginaAtualEl) paginaAtualEl.textContent = currentPagePosts;
        if (totalPaginasEl) totalPaginasEl.textContent = totalPages;

        const btnPrev = document.getElementById('btnAnteriorPosts');
        const btnNext = document.getElementById('btnProximoPosts');
        if (btnPrev) btnPrev.disabled = currentPagePosts <= 1;
        if (btnNext) btnNext.disabled = currentPagePosts >= totalPages;
    }

    // Paginação compartilhada (aceita 'usuarios' ou 'posts')
    window.paginaAnterior = function (tipo) {
        if (tipo === 'posts') {
            currentPagePosts = Math.max(1, currentPagePosts - 1);
            filterPosts();
        } else {
            currentPageUsuarios = Math.max(1, currentPageUsuarios - 1);
            filterUsuarios();
        }
    };

    window.paginaProxima = function (tipo) {
        if (tipo === 'posts') {
            currentPagePosts = currentPagePosts + 1;
            filterPosts();
        } else {
            currentPageUsuarios = currentPageUsuarios + 1;
            filterUsuarios();
        }
    };

    // Listeners
    if (buscaUsuariosInput) {
        buscaUsuariosInput.addEventListener('input', function () {
            currentPageUsuarios = 1;
            filterUsuarios();
        });
    }
    if (filtroStatusSelect) {
        filtroStatusSelect.addEventListener('change', function () {
            currentPageUsuarios = 1;
            filterUsuarios();
        });
    }
    if (buscaPostsInput) {
        buscaPostsInput.addEventListener('input', function () {
            currentPagePosts = 1;
            filterPosts();
        });
    }

    // Inicializar exibição
    filterUsuarios();
    filterPosts();
});
