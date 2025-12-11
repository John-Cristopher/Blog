DROP DATABASE IF EXISTS blog_john;

USE blog_john;

CREATE DATABASE blog_john;

CREATE TABLE
    usuario (
        idUsuario INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
        nome VARCHAR(50) NOT NULL,
        user VARCHAR(15) NOT NULL UNIQUE,
        email VARCHAR(100) NOT NULL UNIQUE,
        senha VARCHAR(60) NOT NULL,
        foto VARCHAR(100),
        dataCadastro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        ativo BOOLEAN NOT NULL DEFAULT 1
    );

CREATE TABLE
    post (
        idPost INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
        titulo VARCHAR(60) NOT NULL,
        conteudo TEXT NOT NULL,
        dataPost TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        idUsuario INT,
        FOREIGN KEY (idUsuario) REFERENCES usuario (idUsuario) ON DELETE CASCADE
    );

ALTER TABLE usuario ADD ativo BOOLEAN NOT NULL DEFAULT 1;

ALTER TABLE post ADD FOREIGN KEY (idUsuario) REFERENCES usuario (idUsuario) ON DELETE CASCADE;

DELETE FROM usuario
WHERE
    idUsuario = 0;

SELECT
    *
FROM
    post;

CREATE VIEW
    vw_total_posts AS
SELECT
    COUNT(*) AS total_posts
FROM
    post p
    JOIN usuario u ON p.idUsuario = u.idUsuario
WHERE
    u.ativo = 1;

CREATE VIEW
    vw_usuarios AS
SELECT
    COUNT(*) AS total_usuarios
FROM
    usuario
WHERE
    ativo = 1;

ALTER TABLE usuario
ADD COLUMN reset_obrigatorio TINYINT (1) DEFAULT 0;

-- INSERT INTO usuario (nome, user, senha, email) VALUES ("Teste", "testador", "Testinho", "TesteSilva@gmail"); USER TESTE
-- TRUNCATE post * Apagar postagens *