# Use a imagem oficial do Python
FROM python:3.11-slim

# Define o diretório de trabalho
WORKDIR /app

# Copia os arquivos de requisitos
COPY requirements.txt .

# Instala as dependências
RUN pip install --no-cache-dir -r requirements.txt

# Copia o código da aplicação
COPY . .

# Expõe a porta que a aplicação usa
EXPOSE 8000

# Dá permissão de execução ao script de inicialização
RUN chmod +x start.sh

# Comando para executar a aplicação
CMD ["./start.sh"]

# Metadados da imagem
LABEL version="6.0.0" \
      description="Sistema de Gestão de Consultores com Protocolos" \
      maintainer="Serviços IA <adm@servicosmkt.com.br>"
