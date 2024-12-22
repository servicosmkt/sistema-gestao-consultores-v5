#!/bin/bash

# Configurações
DOCKER_HUB_USER="servicosia"
IMAGE_NAME="$DOCKER_HUB_USER/gestao-consultores"
VERSION="5.0.0"

# Constrói a imagem
echo "Construindo imagem Docker..."
docker build -t $IMAGE_NAME:$VERSION .
docker tag $IMAGE_NAME:$VERSION $IMAGE_NAME:latest

# Faz push para o Docker Hub
echo "Fazendo push para o Docker Hub..."
docker push $IMAGE_NAME:$VERSION
docker push $IMAGE_NAME:latest

echo "Processo concluído!"
echo "A imagem está disponível em: $IMAGE_NAME:$VERSION"
echo "Para usar no stack.yml, atualize a imagem para: $IMAGE_NAME:$VERSION"
