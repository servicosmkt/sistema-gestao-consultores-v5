from sqlalchemy import create_engine, text
import os
from dotenv import load_dotenv

# Carrega variáveis de ambiente
load_dotenv()

# Configurações do banco de dados
POSTGRES_HOST = os.getenv("POSTGRES_HOST", "localhost")
POSTGRES_PORT = os.getenv("POSTGRES_PORT", "5432")
POSTGRES_USERNAME = os.getenv("POSTGRES_USERNAME", "postgres")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")
POSTGRES_DATABASE = os.getenv("POSTGRES_DATABASE", "gestao_consultores")

# String de conexão
DATABASE_URL = f"postgresql://{POSTGRES_USERNAME}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DATABASE}"

def run_migration():
    """
    Cria as tabelas de protocolos e controle.
    """
    engine = create_engine(DATABASE_URL)
    
    with engine.connect() as connection:
        # Verifica e cria a tabela de controle de protocolo
        check_controle = text("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_name = 'controle_protocolo'
            );
        """)
        result = connection.execute(check_controle)
        controle_exists = result.scalar()

        if not controle_exists:
            create_controle = text("""
                CREATE TABLE controle_protocolo (
                    id SERIAL PRIMARY KEY,
                    ultimo_numero INTEGER DEFAULT 0,
                    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                );
                INSERT INTO controle_protocolo (ultimo_numero) VALUES (0);
            """)
            connection.execute(create_controle)
            connection.commit()
            print("Tabela controle_protocolo criada com sucesso!")

        # Verifica e cria a tabela de protocolos
        check_protocolos = text("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_name = 'protocolos'
            );
        """)
        result = connection.execute(check_protocolos)
        protocolos_exists = result.scalar()

        if not protocolos_exists:
            create_protocolos = text("""
                CREATE TABLE protocolos (
                    id SERIAL PRIMARY KEY,
                    numero VARCHAR NOT NULL UNIQUE,
                    consultor_id INTEGER NOT NULL,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                );
                CREATE INDEX idx_protocolos_numero ON protocolos(numero);
                CREATE INDEX idx_protocolos_consultor_id ON protocolos(consultor_id);
            """)
            connection.execute(create_protocolos)
            connection.commit()
            print("Tabela protocolos criada com sucesso!")

if __name__ == "__main__":
    run_migration()
