import os
import requests
import pandas as pd
import random

# NOVO: bibliotecas para PostgreSQL
from sqlalchemy import create_engine


# Coloque sua chave API no final para teste
# http://www.omdbapi.com/?t=Inception&apikey=

# Configurações
API_KEY = os.getenv("OMDB_API_KEY")
BASE_URL = "http://www.omdbapi.com/"

# Defina os gêneros que você deseja filtrar
GENEROS_ALVO = ["Action", "Sci-Fi", "Comedy"] 
TERMOS_BUSCA = ["Life", "World", "Star", "Man"] # Termos genéricos para achar muitos filmes

def fetch_movies_by_genre(keywords, target_genres, limit_per_genre=10):
    all_movies = []
    seen_ids = set()
    genre_counts = {g: 0 for g in target_genres}

    for kw in keywords:
        print(f"🔎 Vasculhando filmes com o termo: {kw}...")
        for page in range(1, 5): # Busca em até 5 páginas por termo
            params = {'s': kw, 'type': 'movie', 'apikey': API_KEY, 'page': page}
            try:
                res = requests.get(BASE_URL, params=params).json()
                if res.get('Response') == 'False': break

                for item in res.get('Search', []):
                    m_id = item['imdbID']
                    if m_id in seen_ids: continue

                    # Chamada extra para pegar o Gênero detalhado
                    detail_params = {'i': m_id, 'apikey': API_KEY}
                    detail_res = requests.get(BASE_URL, params=detail_params).json()

                    movie_genres = detail_res.get('Genre', '')

                    # Verifica se o filme se encaixa nos gêneros que queremos
                    for target in target_genres:
                        if target in movie_genres and genre_counts[target] < limit_per_genre:
                            all_movies.append({
                                'movie_id': m_id,
                                'title': detail_res.get('Title'),
                                'year': detail_res.get('Year'),
                                'genre': movie_genres,
                                'director': detail_res.get('Director')
                            })
                            seen_ids.add(m_id)
                            genre_counts[target] += 1
                            print(f"✅ Adicionado: {detail_res.get('Title')} [{target}]")
                            break

            except Exception as e:
                print(f"Erro: {e}")

            # Para se já atingimos a meta de todos os gêneros
            if all(count >= limit_per_genre for count in genre_counts.values()):
                break

    return pd.DataFrame(all_movies)

# Funções de Users e Ratings permanecem as mesmas da resposta anterior
def generate_mock_data(movie_df):
    if movie_df.empty: return pd.DataFrame(), pd.DataFrame()
    users = pd.DataFrame({
        'user_id': range(1, 21),
        'name': [f'Usuario_{i}' for i in range(1, 21)],
        'email': [f'user{i}@movieflix.com' for i in range(1, 21)]
    })
    ratings_list = []
    for u_id in users['user_id']:
        for m_id in random.sample(movie_df['movie_id'].tolist(), k=min(len(movie_df), 5)):
            ratings_list.append({
                'user_id': u_id, 'movie_id': m_id, 
                'rating': random.randint(1, 5), 'timestamp': '2024-02-15'
            })
    return users, pd.DataFrame(ratings_list)

# --- EXECUÇÃO ---
df_movies = fetch_movies_by_genre(TERMOS_BUSCA, GENEROS_ALVO, limit_per_genre=15)

if not df_movies.empty:
    df_users, df_ratings = generate_mock_data(df_movies)
    df_movies.to_csv('movies.csv', index=False)
    df_users.to_csv('users.csv', index=False)
    df_ratings.to_csv('ratings.csv', index=False)
    # alterei a msgs
    print(f"\n🚀 CSVS gerados com sucesso! {len(df_movies)} filmes filtrados por gênero salvos.")


    # NOVA ETAPA: CONEXÃO COM O POSTGRES
    PG_HOST = os.getenv("PG_HOST")
    PG_PORT = os.getenv("PG_PORT")
    PG_USER = os.getenv("PG_USER")
    PG_PASSWORD = os.getenv("PG_PASSWORD")
    PG_DATABASE = os.getenv("PG_DATABASE")

    engine = create_engine(
        f"postgresql://{PG_USER}:{PG_PASSWORD}@{PG_HOST}:{PG_PORT}/{PG_DATABASE}"
    )

    # CARGA DOS DADOS NO BANCO
    df_movies.to_sql("movies", engine, if_exists="replace", index=False)
    df_users.to_sql("users", engine, if_exists="replace", index=False)
    df_ratings.to_sql("ratings", engine, if_exists="replace", index=False)

    print("✅ Dados carregados com sucesso no PostgreSQL!")

    # CONSULTA VIEW 
    from sqlalchemy import text
    
    with engine.connect() as conn:
        conn.execute(text("""
            CREATE OR REPLACE VIEW filmes_mais_bem_rankeados AS
            SELECT
                m.movie_id,
                m.title,
                m.year,
                m.genre
            FROM movies m
            JOIN ratings r
                ON m.movie_id = r.movie_id
            WHERE r.rating = 5;
        """))
 
    print("✅ View 'filmes_mais_bem_rankeados' criada com sucesso!")
    df_page = pd.read_sql(
        "SELECT * FROM filmes_mais_bem_rankeados ORDER BY title",
        engine
    )
    print("\n Filmes mais bem rankiados (5 estrelas):")
    print(df_page)
    
    df_page.to_csv("filmes_mais_bem_rankeados.csv", index=False)
