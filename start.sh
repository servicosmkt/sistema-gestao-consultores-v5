#!/bin/bash

# Aguarda o PostgreSQL estar pronto
echo "Aguardando PostgreSQL..."
sleep 5

# Executa o setup do banco de dados
echo "Configurando banco de dados..."
python migrations/setup_database.py

# Em caso de erro, tenta novamente após um tempo
if [ $? -ne 0 ]; then
    echo "Erro na primeira tentativa, aguardando mais 5 segundos..."
    sleep 5
    python migrations/setup_database.py
fi

# Inicia a aplicação
echo "Iniciando aplicação..."
uvicorn main:app --host 0.0.0.0 --port 8000
