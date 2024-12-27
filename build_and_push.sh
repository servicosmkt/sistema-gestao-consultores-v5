#!/bin/bash

# Versão do projeto
VERSION="5.1.0"

# Nome da imagem
IMAGE_NAME="gestao-consultores"

# Tag completa
FULL_TAG="$IMAGE_NAME:$VERSION"

# Constrói a imagem
echo "Construindo imagem $FULL_TAG..."
docker build -t $FULL_TAG .

# Verifica se a construção foi bem sucedida
if [ $? -eq 0 ]; then
    echo "Imagem construída com sucesso!"
    
    # Aqui você pode adicionar comandos para fazer push para um registry
    # Por exemplo:
    # docker tag $FULL_TAG seu-registry.com/$FULL_TAG
    # docker push seu-registry.com/$FULL_TAG
else
    echo "Erro ao construir a imagem"
    exit 1
fi
