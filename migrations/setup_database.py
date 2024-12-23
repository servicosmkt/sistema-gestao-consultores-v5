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

def upgrade():
    """
    Configura o banco de dados com todas as tabelas e configurações necessárias.
    """
    engine = create_engine(DATABASE_URL)
    
    with engine.connect() as connection:
        print("Iniciando setup do banco de dados...")
        
        # 1. Cria tabela de consultores
        print("Criando tabela de consultores...")
        connection.execute(text("""
            CREATE TABLE IF NOT EXISTS consultores (
                id SERIAL PRIMARY KEY,
                nome VARCHAR(255) NOT NULL,
                email VARCHAR(255) UNIQUE,
                idiomas VARCHAR[] NOT NULL,
                status_ativo BOOLEAN DEFAULT true,
                status_ativo_sequencial BOOLEAN DEFAULT true,
                status_online BOOLEAN DEFAULT false,
                ultimo_atendimento TIMESTAMP WITH TIME ZONE,
                id_pipedrive INTEGER
            );
            
            CREATE INDEX IF NOT EXISTS idx_consultores_nome ON consultores(nome);
            CREATE INDEX IF NOT EXISTS idx_consultores_email ON consultores(email);
            CREATE INDEX IF NOT EXISTS idx_consultores_id_pipedrive ON consultores(id_pipedrive);
        """))
        
        # 2. Cria tabela de protocolos e controle
        print("Criando tabelas de protocolos...")
        connection.execute(text("""
            CREATE TABLE IF NOT EXISTS controle_protocolo (
                id SERIAL PRIMARY KEY,
                ultimo_numero INTEGER DEFAULT 0,
                updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
            );
            
            CREATE TABLE IF NOT EXISTS protocolos (
                id SERIAL PRIMARY KEY,
                numero VARCHAR(255) UNIQUE NOT NULL,
                consultor_id INTEGER NOT NULL,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
            );
            
            CREATE INDEX IF NOT EXISTS idx_protocolos_numero ON protocolos(numero);
            CREATE INDEX IF NOT EXISTS idx_protocolos_consultor_id ON protocolos(consultor_id);
        """))
        
        # 3. Cria tabela de API keys e insere a chave padrão
        print("Configurando API keys...")
        connection.execute(text("""
            CREATE TABLE IF NOT EXISTS api_keys (
                id SERIAL PRIMARY KEY,
                key VARCHAR(255) UNIQUE NOT NULL,
                description VARCHAR(255),
                is_active BOOLEAN DEFAULT true,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
            );
        """))
        
        # Adiciona a API key do .env
        api_key = os.getenv("AUTHENTICATION_API_KEY")
        if api_key:
            connection.execute(text("""
                INSERT INTO api_keys (key, description)
                VALUES (:key, 'API Key padrão do sistema')
                ON CONFLICT (key) DO NOTHING;
            """), {"key": api_key})
        
        # 4. Inicializa o controle de protocolo se necessário
        print("Inicializando controle de protocolo...")
        connection.execute(text("""
            INSERT INTO controle_protocolo (ultimo_numero, updated_at)
            SELECT 0, CURRENT_TIMESTAMP
            WHERE NOT EXISTS (SELECT 1 FROM controle_protocolo);
        """))
        
        connection.commit()
        print("Setup do banco de dados concluído com sucesso!")

def downgrade():
    """
    Remove todas as tabelas e configurações.
    """
    engine = create_engine(DATABASE_URL)
    
    with engine.connect() as connection:
        print("Removendo todas as tabelas...")
        connection.execute(text("""
            DROP TABLE IF EXISTS protocolos;
            DROP TABLE IF EXISTS controle_protocolo;
            DROP TABLE IF EXISTS api_keys;
            DROP TABLE IF EXISTS consultores;
        """))
        connection.commit()
        print("Todas as tabelas foram removidas com sucesso!")

if __name__ == "__main__":
    upgrade()
