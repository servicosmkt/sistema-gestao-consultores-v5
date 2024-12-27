# Sistema de Gestão de Consultores v6

Sistema de gerenciamento e distribuição de consultores para atendimento, com suporte a múltiplos idiomas e controle de protocolos.

## Visão Geral

O Sistema de Gestão de Consultores é uma API REST desenvolvida em Python que gerencia a distribuição automática de consultores para atendimento, considerando:
- Disponibilidade do consultor
- Idiomas suportados
- Balanceamento de carga (tempo desde último atendimento)
- Geração e controle de protocolos
- Integração com Pipedrive
- Logs estruturados para monitoramento

## Funcionalidades Principais

- 👥 **Gestão de Consultores**
  - Cadastro e atualização de consultores
  - Controle de status (ativo/inativo, online/offline)
  - Suporte a múltiplos idiomas por consultor
  - Integração com Pipedrive através de ID

- 🔄 **Distribuição Inteligente**
  - Seleção automática do próximo consultor disponível
  - Balanceamento por tempo de espera
  - Filtro por idioma do atendimento
  - Sistema de fila FIFO (First In, First Out)

- 📝 **Gestão de Protocolos**
  - Geração automática de números sequenciais
  - Associação com consultores
  - Histórico de atendimentos
  - Consulta e atualização de protocolos
  - Controle transacional para evitar duplicação

- 🔒 **Segurança**
  - Autenticação via API Key
  - Controle de acesso por endpoints
  - Registro de operações

- 📊 **Monitoramento**
  - Logs estruturados em JSON
  - Rastreamento de requisições por ID único
  - Métricas de tempo de resposta
  - Registro completo de operações

## Tecnologias Utilizadas

- **FastAPI**: Framework web moderno e rápido
- **SQLAlchemy**: ORM para banco de dados
- **Pydantic**: Validação de dados e serialização
- **PostgreSQL**: Banco de dados relacional
- **Docker**: Containerização da aplicação
- **Python 3.8+**: Linguagem de programação

## Estrutura do Projeto

```
sistema-gestao-consultores-v6/
├── main.py              # Aplicação FastAPI e rotas
├── models.py            # Modelos SQLAlchemy e lógica de negócio
├── schemas.py           # Schemas Pydantic para validação
├── database.py          # Configuração do banco de dados
├── migrations/          # Scripts de migração do banco
│   └── setup_database.py # Script de inicialização do banco
├── Dockerfile          # Configuração Docker
├── stack.yml           # Configuração Docker Compose
├── start.sh           # Script de inicialização
├── requirements.txt    # Dependências Python
└── .dockerignore      # Arquivos ignorados no Docker
```

## Configuração e Instalação

1. Clone o repositório
2. Configure as variáveis de ambiente necessárias
3. Instale as dependências:
```bash
pip install -r requirements.txt
```

4. Execute as migrações do banco de dados:
```bash
python migrations/setup_database.py
```

5. Inicie o servidor:
```bash
uvicorn main:app --host 0.0.0.0 --port 8000
```

### Usando Docker

1. Construa e execute usando Docker Compose:
```bash
docker-compose -f stack.yml up --build
```

## Variáveis de Ambiente

```env
DATABASE_URL=postgresql://user:password@localhost:5432/dbname
AUTHENTICATION_API_KEY=sua-api-key-secreta
```

## Endpoints da API

### Consultores

- `GET /consultores` - Lista todos os consultores
- `POST /consultor` - Cria novo consultor
- `GET /consultor/{id}` - Obtém dados de um consultor
- `PUT /consultor/{id}` - Atualiza dados do consultor
- `DELETE /consultor/{id}` - Remove consultor
- `PUT /consultor/{id}/connection` - Atualiza status online/offline

### Distribuição

- `GET /consultor/da-vez` - Obtém próximo consultor disponível
  - Parâmetros:
    - `idioma`: Idioma requerido para atendimento

### Protocolos

- `GET /protocolos` - Lista protocolos
  - Parâmetros opcionais:
    - `consultor_id`: Filtrar por consultor
    - `skip`: Paginação (offset)
    - `limit`: Limite de registros
- `GET /protocolo/{id}` - Obtém dados do protocolo
- `PUT /protocolo/{id}` - Atualiza protocolo
- `GET /gerar-protocolo` - Gera novo número de protocolo

## Logs e Monitoramento

O sistema utiliza logs estruturados em JSON para facilitar o monitoramento e análise. Cada requisição recebe um ID único e os logs incluem:

### Formato dos Logs

```json
// Log de Requisição
{
  "request": {
    "id": "18d2e9b4",
    "method": "GET",
    "path": "/consultor/da-vez",
    "params": {"idioma": "pt"}
  }
}

// Log de Resposta
{
  "response": {
    "id": "18d2e9b4",
    "status": 200,
    "time": "0.02s",
    "data": {
      "consultor_id": 1,
      "numero_protocolo": "#00001"
    }
  }
}

// Log de Erro
{
  "error": {
    "id": "18d2e9b4",
    "method": "GET",
    "path": "/consultor/da-vez",
    "error": "Consultor não encontrado"
  }
}
```

## Modelos de Dados

### Consultor

```python
{
    "id": int,
    "nome": str,
    "idiomas": List[str],
    "status_ativo": bool,
    "status_ativo_sequencial": bool,
    "status_online": bool,
    "ultimo_atendimento": datetime,
    "id_pipedrive": Optional[int]
}
```

### Protocolo

```python
{
    "id": int,
    "numero": str,  # Formato: #00001
    "consultor_id": int,
    "created_at": datetime
}
```

## Segurança

Todas as requisições devem incluir o header `api-key` com uma chave válida:

```http
api-key: sua-api-key-secreta
```

## Contribuição

1. Faça um Fork do projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

## Licença

Este projeto está sob a licença MIT. Veja o arquivo `LICENSE` para mais detalhes.
