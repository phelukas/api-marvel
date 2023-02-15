
[![NPM](https://img.shields.io/npm/l/react)](https://github.com/devsuperior/sds1-wmazoni/blob/master/LICENSE) 

# Sobre o projeto

Essa é uma simples api de um de que consome dados da api da marvel.

# REST API
A api utiliza arquitetura rest.

# Clone

Uma vez que o projeto estiver clonado na sua maquina você pode fazer as configuração das variaveis de ambiente no arquivo `.env.sample` dentro da pasta `./api`.

```
cd api/
cp .env.sample .env
```
Com isso o arquivo `.env` foi criado onde la você vai preencher as variaveis de ambiente.
```
Exemplo:
    ts=123456789  
    apikey=a32s634756767g96g87
    hash=jytcyti6676fg6gy
```
>  **Note**
> : Todas essas informações estão no site da Marvel.api.

# Run

Primeiro você vai precisar criar uma `venv` para seu projeto utilizando o comando:
`python3 -m venv venv`

Depois você deve ativar sua venv.

Com a venv ativada você precisa instalar as libs para o projeto com o comando:
`pip install -r requeriments.txt`

Com todas as libs instaladas você só precisa entrar na pasta `api` e excutar o comando `flask run`

```