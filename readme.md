README – Projeto MovieFlix
Este projeto implementa um pipeline automatizado de extração, carga e consulta de dados de filmes utilizando Python, PostgreSQL, Docker e GitHub Actions.
O objetivo é extrair dados de filmes da API OMDb, gerar dados fictícios de usuários e avaliações, armazenar tudo em um banco PostgreSQL executado via Docker no GitHub Actions e gerar um CSV final com os filmes que receberam avaliação máxima (5 estrelas).
PASSO A PASSO DO FUNCIONAMENTO
Passo 1 – Disparo do workflow
O pipeline é executado manualmente através do GitHub Actions, utilizando o gatilho workflow_dispatch.
Passo 2 – Provisionamento do ambiente
O GitHub Actions:

Inicializa um runner Ubuntu
Sobe um container Docker com PostgreSQL
Configura o banco com usuário, senha e base definidos no workflow
Instala Python 3.10
Instala as dependências listadas em extract/requirements.txt, além das bibliotecas de conexão com o PostgreSQL

Passo 3 – Extração dos dados
O script extract_pipeline.py é executado.
Ele:

Consulta a API OMDb usando uma chave armazenada em GitHub Secrets
Busca filmes a partir de termos genéricos
Consulta o detalhe de cada filme
Filtra filmes pelos gêneros desejados (Action, Sci‑Fi, Comedy)
Evita duplicidade de filmes

Passo 4 – Geração de dados complementares
O script gera:

Uma tabela fictícia de usuários
Avaliações aleatórias (ratings de 1 a 5 estrelas) para esses usuários

Passo 5 – Geração de CSVs iniciais
Após a extração e geração de dados, o script cria:

movies.csv
users.csv
ratings.csv

Esses arquivos servem tanto para auditoria quanto para persistência posterior.
Passo 6 – Conexão com o PostgreSQL
O script lê as variáveis de ambiente do banco (host, porta, usuário, senha e database) e cria uma conexão com o PostgreSQL usando SQLAlchemy.
Passo 7 – Carga dos dados no banco
Os DataFrames são carregados no PostgreSQL, criando as tabelas:

movies
users
ratings

As tabelas são recriadas a cada execução para garantir consistência.
Passo 8 – Criação da view analítica
Após a carga, o script cria uma view no PostgreSQL chamada filmes_mais_bem_rankeados.
Essa view:

Faz join entre movies e ratings
Filtra apenas registros com rating igual a 5
Retorna os dados dos filmes mais bem avaliados

A criação da view é feita dentro de uma transação com commit garantido.
Passo 9 – Consulta da view
O script executa um SELECT na view filmes_mais_bem_rankeados.
O resultado é:

Exibido no log do GitHub Actions
Convertido em DataFrame no Python

Passo 10 – Geração do CSV final
O resultado da view é salvo no arquivo:

filmes_mais_bem_rankeados.csv

Esse arquivo representa a “página” de filmes mais bem avaliados.
Passo 11 – Upload dos artifacts
Ao final da execução, o workflow faz upload dos arquivos CSV como artifacts do GitHub Actions:

movies.csv
users.csv
ratings.csv
filmes_mais_bem_rankeados.csv

Passo 12 – Download do resultado
O artifact pode ser baixado pela interface do GitHub Actions.
Dentro do arquivo ZIP estarão todos os CSVs gerados, incluindo o CSV final da view.
RESULTADO FINAL
Ao final do pipeline, o projeto entrega:

Dados de filmes extraídos da API
Dados persistidos em PostgreSQL via Docker
Uma view analítica com filmes avaliados com 5 estrelas
Um CSV final pronto para consumo com os filmes mais bem rankeados

TECNOLOGIAS UTILIZADAS

Python 3.10
GitHub Actions
Docker
PostgreSQL
SQLAlchemy
Pandas
OMDb API
