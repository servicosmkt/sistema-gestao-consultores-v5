from sqlalchemy import create_engine, text
from dotenv import load_dotenv
import os
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

def create_database():
    """
    Cria o banco de dados se não existir.
    """
    # Conecta ao postgres para criar o banco
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
        else:
            print(f"Banco de dados {DB_NAME} já existe.")
        
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"Erro ao criar banco de dados: {str(e)}")
        raise

def run_migration():
    """
    Executa a migração para adicionar as tabelas de protocolo.
    """
    try:
        # Tenta criar o banco, mas ignora se já existir
        create_database()
    except Exception as e:
        print(f"Nota: {str(e)}")
        print("Continuando com a migração das tabelas...")

    # String de conexão para o banco específico
    DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    
    # Cria engine do SQLAlchemy
    engine = create_engine(DATABASE_URL)

    with engine.connect() as conn:
        print("Criando tabela de consultores...")
        # Cria tabela de consultores primeiro
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS consultores (
                id SERIAL PRIMARY KEY,
                nome VARCHAR(255) NOT NULL,
                email VARCHAR(255),
                telefone VARCHAR(50),
                idiomas VARCHAR[] NOT NULL,
                status_ativo BOOLEAN DEFAULT true,
                status_ativo_sequencial BOOLEAN DEFAULT true,
                status_online BOOLEAN DEFAULT false,
                ultimo_atendimento TIMESTAMP WITH TIME ZONE,
                id_pipedrive INTEGER
            );
        """))

        print("Criando sequence para protocolos...")
        # Cria sequence para números de protocolo
        conn.execute(text("""
            CREATE SEQUENCE IF NOT EXISTS seq_numero_protocolo
            START WITH 1
            INCREMENT BY 1
            NO MINVALUE
            NO MAXVALUE
            CACHE 1;
        """))

        print("Criando tabela de controle de protocolo...")
        # Cria tabela de controle de protocolo
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS controle_protocolo (
                id SERIAL PRIMARY KEY,
                ultimo_numero INTEGER DEFAULT 0,
                updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
            );
        """))

        print("Criando tabela de protocolos...")
        # Cria tabela de protocolos
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS protocolos (
                id SERIAL PRIMARY KEY,
                numero VARCHAR(10) UNIQUE NOT NULL,
                consultor_id INTEGER NOT NULL,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                CONSTRAINT fk_consultor
                    FOREIGN KEY (consultor_id)
                    REFERENCES consultores (id)
                    ON DELETE CASCADE
            );
        """))

        print("Criando índices...")
        # Cria índices
        conn.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_protocolos_numero ON protocolos (numero);
            CREATE INDEX IF NOT EXISTS idx_protocolos_consultor_id ON protocolos (consultor_id);
        """))

        print("Criando função para gerar próximo número de protocolo...")
        # Adiciona função para gerar próximo número de protocolo
        conn.execute(text("""
            CREATE OR REPLACE FUNCTION get_next_protocol_number()
            RETURNS VARCHAR(10)
            LANGUAGE plpgsql
            AS $$
            DECLARE
                next_number INTEGER;
            BEGIN
                -- Atualiza e retorna o próximo número
                UPDATE controle_protocolo
                SET ultimo_numero = ultimo_numero + 1,
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = 1
                RETURNING ultimo_numero INTO next_number;
                
                -- Se não existir registro, cria um
                IF NOT FOUND THEN
                    INSERT INTO controle_protocolo (ultimo_numero, updated_at)
                    VALUES (1, CURRENT_TIMESTAMP)
                    RETURNING ultimo_numero INTO next_number;
                END IF;
                
                -- Retorna o número formatado
                RETURN '#' || LPAD(next_number::TEXT, 5, '0');
            END;
            $$;
        """))

        print("Criando função para criar protocolo automaticamente...")
        # Adiciona função para criar protocolo automaticamente
        conn.execute(text("""
            CREATE OR REPLACE FUNCTION create_protocol_for_consultant(p_consultor_id INTEGER)
            RETURNS VARCHAR(10)
            LANGUAGE plpgsql
            AS $$
            DECLARE
                v_numero VARCHAR(10);
            BEGIN
                -- Gera o próximo número de protocolo
                v_numero := get_next_protocol_number();
                
                -- Insere o protocolo
                INSERT INTO protocolos (numero, consultor_id)
                VALUES (v_numero, p_consultor_id);
                
                RETURN v_numero;
            END;
            $$;
        """))

        print("Criando trigger para protocolo automático...")
        # Adiciona trigger para criar protocolo quando consultor é selecionado
        conn.execute(text("""
            CREATE OR REPLACE FUNCTION create_protocol_on_consultant_selection()
            RETURNS TRIGGER
            LANGUAGE plpgsql
            AS $$
            BEGIN
                -- Cria protocolo para o consultor selecionado
                PERFORM create_protocol_for_consultant(NEW.id);
                RETURN NEW;
            END;
            $$;
        """))

        conn.execute(text("""
            DROP TRIGGER IF EXISTS trg_create_protocol_on_consultant_selection ON consultores;
            CREATE TRIGGER trg_create_protocol_on_consultant_selection
            AFTER UPDATE OF ultimo_atendimento ON consultores
            FOR EACH ROW
            WHEN (OLD.ultimo_atendimento IS DISTINCT FROM NEW.ultimo_atendimento)
            EXECUTE FUNCTION create_protocol_on_consultant_selection();
        """))

        print("Criando tabela de api_keys...")
        # Cria tabela de api_keys
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS api_keys (
                id SERIAL PRIMARY KEY,
                key VARCHAR(255) UNIQUE NOT NULL,
                description VARCHAR(255),
                is_active BOOLEAN DEFAULT true,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
            );
        """))

        # Insere a API key do .env se não existir
        api_key = os.getenv("AUTHENTICATION_API_KEY")
        if api_key:
            print("Inserindo API key padrão...")
            conn.execute(text("""
                INSERT INTO api_keys (key, description)
                VALUES (:key, 'API Key padrão do sistema')
                ON CONFLICT (key) DO NOTHING;
            """), {"key": api_key})

        # Commit das alterações
        conn.commit()
        print("Migração concluída com sucesso!")

if __name__ == "__main__":
    try:
        run_migration()
        print("\nBanco de dados configurado e pronto para uso!")
    except Exception as e:
        print(f"\nErro durante a migração: {str(e)}")
        raise
