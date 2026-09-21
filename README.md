# Django Docker Upload

Aplicacao Django conteinerizada com Gunicorn, Nginx e PostgreSQL. O projeto atende a atividade de infraestrutura com Docker e possui upload de arquivos armazenado em volume persistente.

## Objetivo da atividade

A aplicacao possui:

- um container para o Django executado com Gunicorn;
- um container Nginx funcionando como proxy reverso;
- um container PostgreSQL para o banco de dados;
- uma tela para upload de arquivos;
- um volume Docker para preservar os arquivos enviados mesmo quando o container e reiniciado ou recriado.

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

### Servicos

| Servico | Imagem ou build | Funcao |
| --- | --- | --- |
| `web` | Imagem criada pelo `Dockerfile` | Executa Django com Gunicorn |
| `nginx` | `nginx:alpine` | Proxy reverso e servidor de arquivos estaticos e uploads |
| `db` | `postgres:16-alpine` | Armazena os dados da aplicacao |

## Volumes persistentes

O `docker-compose.yml` cria tres volumes:

| Volume | Local no container | Finalidade |
| --- | --- | --- |
| `media_data` | `/app/media` no Django e `/media` no Nginx | Arquivos enviados pelos usuarios |
| `static_data` | `/app/staticfiles` no Django e `/staticfiles` no Nginx | Arquivos estaticos |
| `postgres_data` | `/var/lib/postgresql/data` no PostgreSQL | Dados do banco |

Os uploads sao gravados em:

```text
/app/media/uploads/
```

Como `/app/media` e um volume Docker, os arquivos nao dependem da existencia temporaria do container Django.

## Requisitos

- Docker Desktop instalado e em execucao;
- Docker Compose v2, incluido nas versoes atuais do Docker Desktop.

Nao e necessario instalar Python, Django ou PostgreSQL na maquina host.

## Configuracao

O arquivo `.env` contem as credenciais locais do PostgreSQL e nao e versionado por seguranca. Para criar uma configuracao local:

```bash
cp .env.example .env
```

Os valores padrao sao:

```env
POSTGRES_DB=appdb
POSTGRES_USER=appuser
POSTGRES_PASSWORD=apppassword
POSTGRES_HOST=db
POSTGRES_PORT=5432
```

Em um ambiente real, altere principalmente `POSTGRES_PASSWORD` e `SECRET_KEY` antes de publicar a aplicacao.

## Executando o projeto

Na pasta raiz do projeto, execute:

```bash
docker compose up -d --build
```

O Compose inicia os containers, aplica as migracoes do Django, coleta os arquivos estaticos e inicia o Gunicorn.

Acesse a aplicacao em:

```text
http://localhost:8080
```

Na pagina inicial, selecione um arquivo e clique em **Enviar arquivo**. O arquivo aparecera na lista de uploads.

## Comandos uteis

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
├── requirements.txt            # Dependencias Python
├── manage.py                   # Comandos administrativos do Django
├── config/
│   ├── settings.py             # Configuracoes do projeto
│   ├── urls.py                 # URLs principais
│   ├── wsgi.py                 # Entrada usada pelo Gunicorn
│   └── asgi.py                 # Entrada ASGI do Django
├── nginx/
│   └── default.conf            # Configuracao do proxy reverso
└── uploads/
    ├── models.py               # Modelo do arquivo enviado
    ├── forms.py                # Formulario de upload
    ├── views.py                # Logica da pagina
    ├── urls.py                 # URL da pagina de upload
    ├── migrations/             # Migracoes do banco
    └── templates/              # Pagina HTML do upload
```

## Funcionamento do upload

1. O usuario acessa a aplicacao pelo Nginx em `localhost:8080`.
2. O Nginx encaminha a requisicao para o Django/Gunicorn.
3. O formulario envia o arquivo usando `multipart/form-data`.
4. O Django valida o formulario e salva o registro no PostgreSQL.
5. O arquivo fisico e salvo em `media/uploads/`.
6. O volume `media_data` preserva o arquivo.
7. O Nginx disponibiliza o arquivo pela URL `/media/`.

O PostgreSQL guarda os dados do registro, como o caminho e a data do upload. O arquivo fisico fica no volume `media_data`.

## Verificacao realizada

A aplicacao foi validada com:

```bash
docker compose config
docker compose up -d --build
docker compose ps
docker compose exec web python manage.py check
```

Tambem foi realizado um upload real pela pagina. O arquivo ficou disponivel em `/app/media/uploads/` dentro do volume `media_data`.

## Roteiro para apresentacao

> O projeto possui tres containers. O primeiro executa o Django com Gunicorn, o segundo executa o Nginx como proxy reverso e o terceiro executa o PostgreSQL. O usuario acessa o Nginx pela porta 8080, e o Nginx encaminha as requisicoes para o Django pela rede interna do Docker. Os dados do banco ficam no volume `postgres_data` e os arquivos enviados ficam no volume `media_data`. Assim, os uploads nao sao perdidos quando o container e reiniciado.

## Observacao sobre volumes

O comando abaixo remove os containers e tambem os volumes, apagando os dados persistidos:

```bash
docker compose down -v
```

Use-o somente quando quiser apagar completamente o banco e os uploads.
