# Sistema de Gestão de Consultores V6

API para gerenciamento de consultores com distribuição sequencial de atendimentos.

## Novas Funcionalidades na V6

- Sistema de protocolos de atendimento (#12345)
- Geração automática de números de protocolo
- Endpoint para criação manual de protocolos
- Retorno do protocolo junto com o consultor da vez

## Endpoints

### Distribuição

- `GET /consultor/da-vez?idioma=pt` - Retorna o próximo consultor disponível e gera protocolo
  - Parâmetros:
    - `idioma`: Código do idioma (ex: pt, en, es)
  - Retorno:
    - Dados do consultor
    - ID do Pipedrive
    - Número do protocolo (#12345)

### Protocolos

- `POST /protocolo` - Cria um novo protocolo manualmente
  - Corpo:
    ```json
    {
      "consultor_id": 123
    }
    ```
  - Retorno:
    - Número do protocolo
    - Data de criação
    - ID do consultor

### Consultores

- `GET /consultores` - Lista todos os consultores
- `POST /consultor` - Cria novo consultor
- `GET /consultor/{id}` - Obtém consultor por ID
- `PUT /consultor/{id}` - Atualiza consultor
- `DELETE /consultor/{id}` - Remove consultor
- `PUT /consultor/{id}/connection` - Atualiza status de conexão

## Configuração

1. Copie o arquivo `.env.example` para `.env`:
```bash
cp .env.example .env
```

2. Configure as variáveis de ambiente no arquivo `.env`:
```env
POSTGRES_PASSWORD=[SUA SENHA POSTGRES]
AUTHENTICATION_API_KEY=[SUA CHAVE API]
API_URL=[SUA URL API]
```

## Instalação

### Docker

1. Construa a imagem:
```bash
./build_and_push.sh
```

2. Configure o stack.yml com suas credenciais

3. Deploy no Swarm:
```bash
docker stack deploy -c stack.yml gestao-consultores
```

### Desenvolvimento Local

1. Instale as dependências:
```bash
pip install -r requirements.txt
```

2. Execute as migrações:
```bash
python migrations/add_protocolos.py
```

3. Inicie o servidor:
```bash
uvicorn main:app --reload
```

## Documentação da API

Acesse a documentação interativa em:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Exemplos de Uso

### Obter Consultor da Vez

```bash
curl -X GET "http://localhost:8000/consultor/da-vez?idioma=pt" \
  -H "api-key: sua-api-key"
```

Resposta:
```json
{
  "consultor_id": 123,
  "consultor_nome": "João Silva",
  "consultor_idiomas": ["pt", "en"],
  "consultor_status_online": true,
  "consultor_atendimento_iso": "2024-01-23T14:30:00Z",
  "consultor_id_pipedrive": 456,
  "protocolo": "#00001"
}
```

### Criar Protocolo Manualmente

```bash
curl -X POST "http://localhost:8000/protocolo" \
  -H "api-key: sua-api-key" \
  -H "Content-Type: application/json" \
  -d '{"consultor_id": 123}'
```

Resposta:
```json
{
  "id": 1,
  "numero": "#00002",
  "consultor_id": 123,
  "created_at": "2024-01-23T14:35:00Z"
}
