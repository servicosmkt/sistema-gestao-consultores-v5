FROM python:3.11-slim

# Instala dependências do sistema
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Define o diretório de trabalho
WORKDIR /app

# Copia os requisitos primeiro para aproveitar o cache do Docker
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia o restante dos arquivos
COPY . .

# Script para carregar secrets em variáveis de ambiente
RUN echo '#!/bin/sh\n\
if [ -f "/run/secrets/db_password" ]; then\n\
    export POSTGRES_PASSWORD=$(cat /run/secrets/db_password)\n\
fi\n\
if [ -f "/run/secrets/api_key" ]; then\n\
    export AUTHENTICATION_API_KEY=$(cat /run/secrets/api_key)\n\
fi\n\
\n\
# Executa as migrações\n\
python migrations/tabela_bd.py\n\
\n\
# Inicia a aplicação\n\
exec uvicorn main:app --host 0.0.0.0 --port 8000\n\
' > /app/entrypoint.sh && chmod +x /app/entrypoint.sh

# Define o entrypoint
ENTRYPOINT ["/app/entrypoint.sh"]
