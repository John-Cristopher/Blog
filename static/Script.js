// ===========================
// Consolidação de todos os scripts JavaScript
// ===========================

// ===========================
// 1. CARROSSEL DE IMAGENS
// ===========================

document.addEventListener('DOMContentLoaded', function () {
    initializeCarousels();
});

function initializeCarousels() {
    const carousels = document.querySelectorAll('.carousel-container');

    carousels.forEach((carousel, index) => {
        // Cada carrossel ganha seus próprios estados
        let slideIndex = 1;
        let slideTimer;

        const slides = carousel.querySelectorAll('.carousel-slide');
        const dots = carousel.querySelectorAll('.dot');

        function showSlide(n) {
            if (n > slides.length) slideIndex = 1;
            if (n < 1) slideIndex = slides.length;

            slides.forEach(s => s.style.display = "none");
            dots.forEach(d => d.classList.remove("active"));

            slides[slideIndex - 1].style.display = "block";
            dots[slideIndex - 1].classList.add("active");
        }

        function autoSlide() {
            slideTimer = setTimeout(() => {
                slideIndex++;
                showSlide(slideIndex);
                autoSlide();
            }, 10000);
        }

        // Torna os dots funcionais
        dots.forEach((dot, dotIndex) => {
            dot.addEventListener("click", () => {
                clearTimeout(slideTimer);
                slideIndex = dotIndex + 1;
                showSlide(slideIndex);
                autoSlide();
            });
        });

        // Inicia tudo para este carrossel
        showSlide(slideIndex);
        autoSlide();
    });
}

// ===========================
// 2. EFEITO MATRIX 
// ===========================

// 1. Seleciona todos os spans (letras) dentro do container .jp-matrix
const matrixLetters = document.querySelectorAll('.jp-matrix span');

// 2. Define a função principal de animação aleatória
function animateRandomLetters() {
    // Se não houver letras do matrix na página, não faz nada
    if (matrixLetters.length === 0) {
        return;
    }

    // Define quantas letras piscarão em cada ciclo (por exemplo, 3 a 7)
    const numToAnimate = Math.floor(Math.random() * 5) + 3;

    for (let i = 0; i < numToAnimate; i++) {
        // Escolhe um índice aleatório
        const randomIndex = Math.floor(Math.random() * matrixLetters.length);
        const letter = matrixLetters[randomIndex];

        // Verifica se a letra já está brilhando (evita piscar a mesma letra duas vezes rápido)
        if (letter.classList.contains('is-glowing')) {
            continue;
        }

        // 3. Aplica a classe de brilho (is-glowing)
        letter.classList.add('is-glowing');

        // 4. Agenda a remoção da classe após um tempo muito curto (simulando um "flash")
        // O tempo aqui define o quão rápido a letra "pisca" (em milissegundos)
        const flashDuration = Math.random() * 500 + 300; // Pisca entre 100ms e 300ms

        setTimeout(() => {
            // Remove a classe para que a letra volte ao estado normal (subtle)
            letter.classList.remove('is-glowing');
        }, flashDuration);
    }
}

// 5. Configura a repetição
// Executa a função a cada 100 milissegundos. Ajuste este valor para controlar
// a FREQUÊNCIA de flashes em toda a tela (quanto menor, mais intenso).
const flashFrequency = 600; // 100ms = 10 flashes por segundo
setInterval(animateRandomLetters, flashFrequency);

// ===========================
// FIM DO SCRIPT
// ===========================
