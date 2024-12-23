# Imagem base Python
FROM python:3.11-slim

# Define o diretório de trabalho
WORKDIR /app

# Instala dependências do sistema
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copia os arquivos de requisitos primeiro para aproveitar o cache do Docker
COPY requirements.txt .

# Instala as dependências
RUN pip install --no-cache-dir -r requirements.txt

# Copia o código da aplicação
COPY . .

# Script para ler secrets e iniciar a aplicação
RUN echo '#!/bin/sh\n\
if [ -f "/run/secrets/db_password" ]; then\n\
    export POSTGRES_PASSWORD=$(cat /run/secrets/db_password)\n\
fi\n\
if [ -f "/run/secrets/api_key" ]; then\n\
    export AUTHENTICATION_API_KEY=$(cat /run/secrets/api_key)\n\
fi\n\
# Executa a migração antes de iniciar a aplicação\n\
python migrations/add_id_pipedrive.py\n\
exec uvicorn main:app --host 0.0.0.0 --port 8000\n\
' > /app/entrypoint.sh \
    && chmod +x /app/entrypoint.sh

# Expõe a porta que a aplicação usa
EXPOSE 8000

# Define as variáveis de ambiente padrão
ENV POSTGRES_HOST=postgres \
    POSTGRES_PORT=5432 \
    POSTGRES_USERNAME=postgres \
    POSTGRES_DATABASE=gestao_consultores \
    ENVIRONMENT=production

# Comando para iniciar a aplicação
ENTRYPOINT ["/app/entrypoint.sh"]
