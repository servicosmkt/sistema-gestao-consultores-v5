from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

# Carrega variáveis de ambiente
load_dotenv()

# Configuração do banco de dados
DB_USER = os.getenv("POSTGRES_USERNAME")
DB_PASS = os.getenv("POSTGRES_PASSWORD")
DB_HOST = os.getenv("POSTGRES_HOST", "localhost")
DB_PORT = os.getenv("POSTGRES_PORT", "5432")
DB_NAME = os.getenv("POSTGRES_DATABASE")

def ensure_database():
    """
    Garante que o banco de dados existe.
    """
    # Conecta ao postgres para verificar/criar o banco
    postgres_url = f"postgresql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/postgres"
    
    try:
        # Conecta ao postgres
        conn = psycopg2.connect(postgres_url)
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()
        
        # Verifica se o banco existe
        cursor.execute(f"SELECT 1 FROM pg_database WHERE datname = '{DB_NAME}'")
        exists = cursor.fetchone()
        
        if not exists:
            print(f"Criando banco de dados {DB_NAME}...")
            cursor.execute(f'CREATE DATABASE "{DB_NAME}"')
            print(f"Banco de dados {DB_NAME} criado com sucesso!")
        
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"[AVISO] Erro ao verificar/criar banco de dados: {str(e)}")

# Tenta criar o banco se não existir
ensure_database()

# String de conexão
DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# Cria engine do SQLAlchemy
engine = create_engine(DATABASE_URL)

# Cria sessão
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base para modelos
Base = declarative_base()

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
