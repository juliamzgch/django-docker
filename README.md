# Django Docker Upload

Aplicação Django conteinerizada com Gunicorn, Nginx e PostgreSQL. O projeto atende à atividade de infraestrutura com Docker e possui upload de arquivos armazenado em volume persistente.

## Objetivo da atividade

A aplicação possui:

- um container para o Django executado com Gunicorn;
- um container Nginx funcionando como proxy reverso;
- um container PostgreSQL para o banco de dados;
- uma tela para upload de arquivos;
- um volume Docker para preservar os arquivos enviados mesmo quando o container é reiniciado ou recriado.

## Arquitetura

```text
Navegador
    |
    | http://localhost:8080
    v
Nginx (porta 8080)
    |
    | proxy reverso pela rede Docker
    v
Django + Gunicorn (porta interna 8000)
    |
    +--> PostgreSQL (porta interna 5432)
    |
    +--> volume media_data: /app/media
```

### Serviços

| Serviço | Imagem ou build | Função |
| --- | --- | --- |
| `web` | Imagem criada pelo `Dockerfile` | Executa Django com Gunicorn |
| `nginx` | `nginx:alpine` | Proxy reverso e servidor de arquivos estáticos e uploads |
| `db` | `postgres:16-alpine` | Armazena os dados da aplicação |

## Volumes persistentes

O `docker-compose.yml` cria três volumes:

| Volume | Local no container | Finalidade |
| --- | --- | --- |
| `media_data` | `/app/media` no Django e `/media` no Nginx | Arquivos enviados pelos usuários |
| `static_data` | `/app/staticfiles` no Django e `/staticfiles` no Nginx | Arquivos estáticos |
| `postgres_data` | `/var/lib/postgresql/data` no PostgreSQL | Dados do banco |

Os uploads são gravados em:

```text
/app/media/uploads/
```

Como `/app/media` é um volume Docker, os arquivos não dependem da existência temporária do container Django.

## Requisitos

- Docker Desktop instalado e em execução;
- Docker Compose v2, incluído nas versões atuais do Docker Desktop.

Não é necessário instalar Python, Django ou PostgreSQL na máquina host.

## Configuração

O arquivo `.env` contém as credenciais locais do PostgreSQL e não é versionado por segurança. Para criar uma configuração local:

```bash
cp .env.example .env
```

Os valores padrão são:

```env
POSTGRES_DB=appdb
POSTGRES_USER=appuser
POSTGRES_PASSWORD=apppassword
POSTGRES_HOST=db
POSTGRES_PORT=5432
```

Em um ambiente real, altere principalmente `POSTGRES_PASSWORD` e `SECRET_KEY` antes de publicar a aplicação.

## Executando o projeto

Na pasta raiz do projeto, execute:

```bash
docker compose up -d --build
```

O Compose inicia os containers, aplica as migrações do Django, coleta os arquivos estáticos e inicia o Gunicorn.

Acesse a aplicação em:

```text
http://localhost:8080
```

Na página inicial, selecione um arquivo e clique em **Enviar arquivo**. O arquivo aparecerá na lista de uploads.

## Comandos úteis

Ver o estado dos containers:

```bash
docker compose ps
```

Ver os logs:

```bash
docker compose logs -f
```

Parar os containers sem apagar os volumes:

```bash
docker compose down
```

Subir novamente:

```bash
docker compose up -d
```

Executar os testes Django:

```bash
docker compose exec web python manage.py test
```

Verificar os arquivos persistidos no volume de uploads:

```bash
docker compose exec web find /app/media/uploads -type f
```

## Estrutura principal

```text
.
├── Dockerfile                  # Imagem do container Django
├── docker-compose.yml          # Django, Nginx, PostgreSQL e volumes
├── requirements.txt            # Dependências Python
├── manage.py                   # Comandos administrativos do Django
├── config/
│   ├── settings.py             # Configurações do projeto
│   ├── urls.py                 # URLs principais
│   ├── wsgi.py                 # Entrada usada pelo Gunicorn
│   └── asgi.py                 # Entrada ASGI do Django
├── nginx/
│   └── default.conf            # Configuração do proxy reverso
└── uploads/
    ├── models.py               # Modelo do arquivo enviado
    ├── forms.py                # Formulário de upload
    ├── views.py                # Lógica da página
    ├── urls.py                 # URL da página de upload
    ├── migrations/             # Migrações do banco
    └── templates/              # Página HTML do upload
```

## Funcionamento do upload

1. O usuário acessa a aplicação pelo Nginx em `localhost:8080`.
2. O Nginx encaminha a requisição para o Django/Gunicorn.
3. O formulário envia o arquivo usando `multipart/form-data`.
4. O Django valida o formulário e salva o registro no PostgreSQL.
5. O arquivo físico é salvo em `media/uploads/`.
6. O volume `media_data` preserva o arquivo.
7. O Nginx disponibiliza o arquivo pela URL `/media/`.

O PostgreSQL guarda os dados do registro, como o caminho e a data do upload. O arquivo físico fica no volume `media_data`.

## Verificação realizada

A aplicação foi validada com:

```bash
docker compose config
docker compose up -d --build
docker compose ps
docker compose exec web python manage.py check
```

Também foi realizado um upload real pela página. O arquivo ficou disponível em `/app/media/uploads/` dentro do volume `media_data`.

## Roteiro para apresentação

> O projeto possui três containers. O primeiro executa o Django com Gunicorn, o segundo executa o Nginx como proxy reverso e o terceiro executa o PostgreSQL. O usuário acessa o Nginx pela porta 8080, e o Nginx encaminha as requisições para o Django pela rede interna do Docker. Os dados do banco ficam no volume `postgres_data` e os arquivos enviados ficam no volume `media_data`. Assim, os uploads não são perdidos quando o container é reiniciado.

## Observação sobre volumes

O comando abaixo remove os containers e também os volumes, apagando os dados persistidos:

```bash
docker compose down -v
```

Use-o somente quando quiser apagar completamente o banco e os uploads.
