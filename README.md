
# API de Gerenciamento de Tarefas

API REST desenvolvida com **Python, FastAPI, SQLAlchemy e SQLite**, utilizando Poetry para gerenciamento de dependências e Docker/Podman para containerização.

A aplicação permite cadastrar, listar, atualizar e excluir tarefas, com autenticação HTTP Basic, paginação e ordenação.

## Tecnologias utilizadas

- Python 3.14
- FastAPI
- Uvicorn
- SQLAlchemy
- SQLite
- Poetry
- Docker / Podman
- Docker Compose / Podman Compose

## Pré-requisitos

Para executar o projeto, é necessário ter:

- Git instalado.
- Docker e Docker Compose ou Podman com um provedor compatível com Compose.
- Conexão com a internet para baixar a imagem Python e instalar as dependências durante a construção.

Não é necessário instalar Python ou Poetry diretamente na máquina, pois o ambiente da aplicação é preparado dentro do contêiner.

## Estrutura do projeto

```text
tarefas-api/
├── Dockerfile
├── docker-compose.yml
├── .dockerignore
├── .env
├── .env.example
├── main.py
├── pyproject.toml
├── poetry.lock
└── README.md
```

O arquivo `tarefas.db` é criado automaticamente pela aplicação na inicialização do banco de dados.

## Configuração das variáveis de ambiente

O arquivo `.env.example` contém um modelo das variáveis necessárias para executar a aplicação:

```dotenv
MEU_USUARIO=admin
MINHA_SENHA=admin
DATABASE_URL=sqlite:///./tarefas.db
```

### Criando o arquivo `.env`

Após clonar o repositório, copie o arquivo de exemplo.

No Windows PowerShell:

```powershell
Copy-Item .env.example .env
```

No Linux ou macOS:

```bash
cp .env.example .env
```

O arquivo `.env` será utilizado pelo Docker Compose para disponibilizar as variáveis de ambiente à aplicação.

**Importante:** as credenciais apresentadas são destinadas apenas ao desenvolvimento. Altere-as conforme necessário e não versione credenciais reais no repositório.

A aplicação deve ler as variáveis `MEU_USUARIO`, `MINHA_SENHA` e `DATABASE_URL` por meio do ambiente.

## Executando com Docker Compose

### 1. Clone o repositório

```bash
git clone URL_DO_REPOSITORIO
cd NOME_DO_REPOSITORIO
```

Substitua `URL_DO_REPOSITORIO` e `NOME_DO_REPOSITORIO` pela URL e pelo nome reais do repositório.

### 2. Configure o ambiente

Crie o arquivo `.env` a partir do modelo:

```powershell
Copy-Item .env.example .env
```

Se necessário, edite o arquivo `.env` para configurar as credenciais e a URL do banco de dados.

### 3. Construa a imagem e inicie a aplicação

```bash
docker compose up --build -d
```

O Docker Compose utiliza o Dockerfile para construir a imagem, instalar as dependências com Poetry e iniciar o servidor Uvicorn.

### 4. Verifique o estado da aplicação

```bash
docker compose ps
```

Para acompanhar os logs:

```bash
docker compose logs -f app
```

### 5. Acesse a documentação

Abra no navegador:

http://localhost:8000/docs

A documentação interativa do FastAPI permite consultar e testar os endpoints da aplicação.

Para acessar as rotas protegidas, informe o usuário e a senha definidos no arquivo `.env`.

Se a porta 8000 já estiver ocupada, altere o mapeamento no `docker-compose.yml`:

```yaml
ports:
  - "8001:8000"
```

Nesse caso, acesse http://localhost:8001/docs.

### 6. Encerre a aplicação

```bash
docker compose down
```

Esse comando interrompe e remove os contêineres gerenciados pelo Compose.

Como o projeto utiliza o volume de montagem `.:/app`, o arquivo SQLite criado nesse diretório permanece na pasta local quando a aplicação é encerrada normalmente.

## Executando com Podman Compose

O projeto também pode ser executado com Podman, sem precisar substituir o Dockerfile ou o arquivo Compose.

### 1. Inicie a máquina Podman

No Windows PowerShell, caso a máquina ainda não esteja iniciada:

```powershell
podman machine start
```

Se ela já estiver em execução, não é necessário executar esse comando novamente.

### 2. Construa a imagem e inicie a aplicação

Na raiz do projeto, execute:

```powershell
podman compose up --build -d
```

### 3. Verifique os contêineres

```powershell
podman compose ps
```

### 4. Consulte os logs

```powershell
podman compose logs -f app
```

### 5. Acesse a documentação

http://localhost:8000/docs

Se a porta 8000 estiver ocupada, altere o mapeamento no `docker-compose.yml`:

```yaml
ports:
  - "8001:8000"
```

Nesse caso, acesse http://localhost:8001/docs.

### 6. Encerre a aplicação

```powershell
podman compose down
```

**Observação:** o comando `podman compose` utiliza um provedor externo de Compose, como `podman-compose` ou Docker Compose. Se nenhum provedor estiver disponível, instale ou configure um compatível com sua instalação.

## Endpoints disponíveis

Todas as rotas abaixo exigem autenticação HTTP Basic.

| Método | Endpoint | Descrição |
|---|---|---|
| POST | `/adicionar` | Cadastra uma nova tarefa |
| GET | `/tarefas` | Lista tarefas com paginação e ordenação |
| PUT | `/atualizar/{nome}` | Atualiza o estado de conclusão de uma tarefa |
| DELETE | `/deletar/{nome}` | Exclui uma tarefa pelo nome |

### Cadastro de tarefa

Endpoint: `POST /adicionar`

Exemplo de corpo da requisição:

```json
{
  "nome": "Estudar Docker",
  "descricao": "Concluir o exercício de containerização",
  "concluida": false
}
```

O campo `concluida` é opcional e assume `false` quando não informado.

Não é permitido cadastrar duas tarefas com o mesmo nome.

### Listagem, paginação e ordenação

Endpoint: `GET /tarefas`

Parâmetros disponíveis:

- `page`: número da página, padrão `1`.
- `size`: quantidade de tarefas por página, padrão `10`.
- `ordena`: campo opcional para ordenação. Valores permitidos: `nome`, `descricao` ou `concluida`.

Exemplo de requisição:

```text
/tarefas?page=1&size=10&ordena=nome
```

A resposta contém a página atual, o tamanho solicitado, a quantidade total de tarefas e a lista de resultados.

### Atualização de tarefa

Endpoint: `PUT /atualizar/{nome}`

Exemplo de corpo da requisição:

```json
{
  "concluida": true
}
```

O endpoint atualiza o estado de conclusão da tarefa identificada pelo nome.

### Exclusão de tarefa

Endpoint: `DELETE /deletar/{nome}`

Remove a tarefa identificada pelo nome informado no caminho da requisição.

## Gerenciamento de dependências com Poetry

O projeto utiliza Poetry para gerenciar as dependências.

- `pyproject.toml`: declara as dependências e a configuração do projeto.
- `poetry.lock`: registra as versões resolvidas das dependências.

O Dockerfile instala o Poetry e utiliza esses arquivos para instalar as dependências durante a construção da imagem.

Quando as dependências forem modificadas, mantenha o `poetry.lock` sincronizado com o `pyproject.toml`.

## Solução de problemas

### A porta 8000 já está em uso

Altere o mapeamento de portas no `docker-compose.yml`:

```yaml
ports:
  - "8001:8000"
```

Reconstrua e inicie a aplicação.

Com Docker:

```bash
docker compose up --build -d
```

Com Podman:

```powershell
podman compose up --build -d
```

Acesse http://localhost:8001/docs.

### O contêiner não inicia

Consulte os logs.

Com Docker:

```bash
docker compose logs app
```

Com Podman:

```powershell
podman compose logs app
```

Verifique se as dependências foram instaladas corretamente, se o arquivo `main.py` está presente e se o comando de inicialização aponta para `main:app`.

### O arquivo `.env` não foi encontrado

Confirme se o arquivo `.env` foi criado na raiz do projeto, no mesmo diretório do `docker-compose.yml`.

### A API não responde

Confira o estado dos contêineres com `docker compose ps` ou `podman compose ps`. Verifique também o mapeamento de portas e os logs da aplicação.

## Licença

Projeto desenvolvido para fins educacionais como parte de um exercício de containerização de aplicações Python com FastAPI, Poetry e Docker Compose.