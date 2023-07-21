import requests
import hashlib
import time
import app
from server.rabbitmq import Rabbitmq
from server.database.models.herois import Heroi
from server.database.models.desafios import Desafio
from server.database import db
from sqlalchemy.exc import IntegrityError
from sqlalchemy import text
from datetime import datetime


class MarvelAPI:
    def __init__(self):
        self.public_key = "9c18ce40e88cc12edc7fc6b2fc90fbf4"
        self.private_key = "bfacac2be5ae424a9b15f74acb9f7e03fdd65a10"
        self.base_url = "https://gateway.marvel.com/v1/public"

    def __all_hereis(self, name=None):
        endpoint = "/characters"
        url = self.base_url + endpoint
        params = self._get_auth_params()
        if name:
            params["name"] = name
        params["limit"] = 100

        all_characters = []

        try:
            while True:
                response = requests.get(url, params=params)
                if response.status_code == 200:
                    data = response.json()
                    characters = data["data"]["results"]
                    all_characters.extend(characters)

                    if len(characters) < 100:
                        break  # Se o número de personagens retornados for menor que 100, chegamos ao final da lista

                    offset = params.get("offset", 0)
                    params["offset"] = (
                        offset + 100
                    )  # Atualiza o offset para obter os próximos 100 personagens

                else:
                    data = response.json()
                    return {"error": data}

        except Exception as error:
            raise Exception(str(error))

        all_characters.sort(key=lambda x: x["name"])  # Ordenar por ordem alfabética

        self.__save_characters(all_characters)

    def __save_characters(self, characters):
        file_name = "personagens.py"
        with open(file_name, "w") as file:
            file.write("personagens = [\n")
            for character in characters:
                file.write(f"    '{character['name']}',\n")
            file.write("]\n")

    def get_characters(self, name=None, limit=None, offset=None):
        endpoint = "/characters"
        url = self.base_url + endpoint
        params = self._get_auth_params()
        if name:
            params["name"] = name
        if limit:
            params["limit"] = limit
        if offset:
            params["offset"] = offset

        try:
            response = requests.get(url, params=params)
        except Exception as error:
            raise Exception(str(error))

        if response.status_code == 200:
            data = response.json()
            characters = data["data"]["results"]
        else:
            data = response.json()
            return {"error": data}

        return characters

    def _get_auth_params(self):
        timestamp = str(time.time())
        hash_str = hashlib.md5(
            (timestamp + self.private_key + self.public_key).encode()
        ).hexdigest()
        return {"ts": timestamp, "apikey": self.public_key, "hash": hash_str}


class ColetorWorker:
    def __init__(self) -> None:
        self._erro_add = 0
        self._api_marvel = MarvelAPI()
        self.__rabbitmq = Rabbitmq()

    @property
    def get_erros(self):
        """Retornar quantos erros teve no ultimo add"""
        return self._erro_add

    def add_herois(self, limit, offset=None):
        """Adiciona herois na fila"""
        herois = self._api_marvel.get_characters(limit=limit, offset=offset)
        for heroi in herois:
            data = {
                "id": heroi["id"],
                "nome": heroi["name"],
                "descricao": heroi["description"],
            }
            self.__rabbitmq.send_menssage(body=data, routing_key="add_hero")

    def salvar_heroi(self, heroi):
        """Salva um Heroi na tabela"""
        with app.app.app_context():
            try:
                obj = Heroi()
                obj.id = heroi["id"]
                obj.name = heroi["nome"]
                obj.description = heroi["descricao"]
                db.session.add(obj)
                db.session.commit()
            except IntegrityError as e:
                print("PERSSONAGEM JÁ EXISTE")
                self._erro_add += 1
            except Exception as e:
                print("OUTRO TIPO DE ERRO", str(e))
                self._erro_add += 1

    def get_heroi(self):
        """Adiciona herois no banco de dados"""
        self._erro_add = 0
        return self.__rabbitmq.consumer_queue(
            fila="add_heroi", callback=self.salvar_heroi
        )


class DesafioWork:
    def __init__(self) -> None:
        self.__rabbitmq = Rabbitmq()

    @property
    def catch_five_heroes(self):
        query = text(
            """
            SELECT TOP 5 *
            FROM Heroi
            WHERE NOT EXISTS (
                SELECT 1
                FROM Desafio
                WHERE Heroi.id = Desafio.heroi_id)
        """
        )
        with app.app.app_context():
            result = db.session.execute(query)
            herois = result.fetchall()

        resp = [{"id": obj[0], "name": obj[1], "description": obj[2]} for obj in herois]
        return resp

    def add_fila(self, herois: list):
        for hero in herois:
            self.__rabbitmq.send_menssage(body=hero, routing_key="challenge_day")

    def save_desafio(self, hero):
        with app.app.app_context():
            try:
                obj = Desafio()
                obj.data_desafio = datetime.now().date()
                obj.usado = 0
                obj.heroi_id = hero["id"]
                db.session.add(obj)
                db.session.commit()
            except Exception as e:
                print("OUTRO TIPO DE ERRO", str(e))

    def get_desafio(self):
        return self.__rabbitmq.consumer_queue(
            fila="challenge_day", callback=self.save_desafio
        )
