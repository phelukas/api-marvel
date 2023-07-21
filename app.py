import subprocess
import random

# Define o caminho do arquivo config.sh
caminho_arquivo = "./config.sh"

# Chama o arquivo config.sh com o parâmetro usando o comando 'bash'
subprocess.call(["bash", caminho_arquivo, "meu_sql_server", "SQL_SERVER_HOST"])
subprocess.call(["bash", caminho_arquivo, "rabbitmq", "RABBITMQ_HOST"])

from dotenv import load_dotenv

load_dotenv(".env", override=True)

from flask_alembic import Alembic
from server import Servidor
from server.workers import ColetorWorker, DesafioWork


app = Servidor()
app.init_api()
app.init_database()
alembic = Alembic()
alembic.init_app(app)

# agendador()

coletor = ColetorWorker()
print(f"No começo eu tenho {coletor.get_erros} erros")
for _ in range(6):
    coletor.add_herois(limit=1, offset=random.randint(1, 1561))

coletor.get_heroi()
print(f"No final eu tenho {coletor.get_erros} erros")


print(" MONTANDO DESAFIO ")
desafio = DesafioWork()
herois = desafio.catch_five_heroes
desafio.add_fila(herois)
desafio.get_desafio()
print(" FIM -- MONTANDO DESAFIO ")


if __name__ == "__main__":
    app.run()
