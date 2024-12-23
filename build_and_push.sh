#!/bin/bash

# Versão da imagem
VERSION="6.0.0"
IMAGE_NAME="servicosia/gestao-consultores"

# Constrói a imagem
echo "Construindo imagem $IMAGE_NAME:$VERSION..."
docker build -t $IMAGE_NAME:$VERSION .

# Adiciona tag latest
echo "Adicionando tag latest..."
docker tag $IMAGE_NAME:$VERSION $IMAGE_NAME:latest

# Push das imagens
echo "Enviando imagens para o Docker Hub..."
docker push $IMAGE_NAME:$VERSION
docker push $IMAGE_NAME:latest

echo "Processo concluído!"
