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
    Adiciona as colunas necessárias na tabela consultores.
    """
    engine = create_engine(DATABASE_URL)
    
    with engine.connect() as connection:
        # Verifica se a tabela existe
        check_table = text("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_name = 'consultores'
            );
        """)
        result = connection.execute(check_table)
        table_exists = result.scalar()

        if not table_exists:
            # Cria a tabela se não existir
            create_table = text("""
                CREATE TABLE consultores (
                    id SERIAL PRIMARY KEY,
                    nome VARCHAR NOT NULL,
                    idiomas VARCHAR[] NOT NULL,
                    status_ativo BOOLEAN DEFAULT TRUE,
                    status_ativo_sequencial BOOLEAN DEFAULT TRUE,
                    status_online BOOLEAN DEFAULT FALSE,
                    ultimo_atendimento TIMESTAMP WITH TIME ZONE,
                    id_pipedrive INTEGER,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP WITH TIME ZONE
                );
                CREATE INDEX idx_consultores_id_pipedrive ON consultores(id_pipedrive);
            """)
            connection.execute(create_table)
            connection.commit()
            print("Tabela consultores criada com sucesso!")
        else:
            # Adiciona colunas se não existirem
            columns = [
                ("status_ativo", "BOOLEAN DEFAULT TRUE"),
                ("status_ativo_sequencial", "BOOLEAN DEFAULT TRUE"),
                ("status_online", "BOOLEAN DEFAULT FALSE"),
                ("ultimo_atendimento", "TIMESTAMP WITH TIME ZONE"),
                ("id_pipedrive", "INTEGER"),
                ("created_at", "TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP"),
                ("updated_at", "TIMESTAMP WITH TIME ZONE")
            ]
            
            for column_name, column_type in columns:
                check_column = text(f"""
                    SELECT column_name 
                    FROM information_schema.columns 
                    WHERE table_name = 'consultores' 
                    AND column_name = '{column_name}';
                """)
                result = connection.execute(check_column)
                column_exists = result.fetchone() is not None

                if not column_exists:
                    add_column = text(f"""
                        ALTER TABLE consultores
                        ADD COLUMN {column_name} {column_type};
                    """)
                    connection.execute(add_column)
                    connection.commit()
                    print(f"Coluna {column_name} adicionada com sucesso!")

            # Cria índice para id_pipedrive se não existir
            check_index = text("""
                SELECT indexname 
                FROM pg_indexes 
                WHERE tablename = 'consultores' 
                AND indexname = 'idx_consultores_id_pipedrive';
            """)
            result = connection.execute(check_index)
            index_exists = result.fetchone() is not None

            if not index_exists:
                create_index = text("""
                    CREATE INDEX idx_consultores_id_pipedrive 
                    ON consultores(id_pipedrive);
                """)
                connection.execute(create_index)
                connection.commit()
                print("Índice idx_consultores_id_pipedrive criado com sucesso!")

if __name__ == "__main__":
    run_migration()
