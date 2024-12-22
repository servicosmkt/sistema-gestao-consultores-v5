# Sistema de Gestão de Consultores V5

API para gerenciamento de consultores com distribuição sequencial de atendimentos.

## Funcionalidades

### Distribuição de Atendimentos
- Sistema inteligente de distribuição sequencial
- Priorização baseada em último atendimento
- Suporte a múltiplos idiomas
- Controle de status online/offline
- Integração com Pipedrive

### Gestão de Consultores
- Cadastro e atualização de consultores
- Controle de status ativo/inativo
- Gerenciamento de idiomas atendidos
- Monitoramento de disponibilidade
- ID do Pipedrive vinculado

### Segurança
- Autenticação via API Key
- Todas as rotas protegidas
- Gerenciamento de chaves de API

## Requisitos

- Python 3.11+
- PostgreSQL
- Docker e Docker Compose

## Configuração

1. Clone o repositório
```bash
git clone [URL_DO_REPOSITORIO]
cd sistema-gestao-consultores-v5
```

2. Configure as variáveis de ambiente
```bash
cp .env.example .env
# Edite o arquivo .env com suas configurações
```

3. Execute com Docker
```bash
docker build -t servicosia/gestao-consultores:5.0.0 .
docker stack deploy -c stack.yml gestao-consultores
```

## Documentação da API

A documentação completa da API está disponível em `/docs` quando o servidor está em execução.

## Endpoints Principais

- `GET /consultor/da-vez`: Obtém o próximo consultor disponível para atendimento
- `GET /consultores`: Lista todos os consultores
- `POST /consultor`: Cria um novo consultor
- `PUT /consultor/{id}`: Atualiza um consultor existente
- `PUT /consultor/{id}/connection`: Atualiza o status de conexão de um consultor

## Estrutura do Projeto

```
.
├── migrations/           # Scripts de migração do banco de dados
├── models.py            # Modelos SQLAlchemy
├── schemas.py           # Schemas Pydantic
├── main.py             # Aplicação FastAPI
├── database.py         # Configuração do banco de dados
├── requirements.txt    # Dependências Python
├── Dockerfile         # Configuração Docker
└── stack.yml         # Configuração Docker Stack
```

## Desenvolvimento

Para executar em ambiente de desenvolvimento:

1. Crie um ambiente virtual
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

2. Instale as dependências
```bash
pip install -r requirements.txt
```

3. Execute o servidor
```bash
uvicorn main:app --reload
```

## Licença

Este projeto está licenciado sob a licença MIT - veja o arquivo LICENSE para detalhes.
