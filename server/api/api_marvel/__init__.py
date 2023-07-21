import requests

import hashlib
import time


def generate_marvel_api_hash(public_key, private_key):
    timestamp = str(int(time.time()))
    hash_string = timestamp + private_key + public_key
    hash_md5 = hashlib.md5(hash_string.encode()).hexdigest()
    return hash_md5


def consulta_api():
    public_key = "9c18ce40e88cc12edc7fc6b2fc90fbf4"
    private_key = "bfacac2be5ae424a9b15f74acb9f7e03fdd65a10"

    hash = generate_marvel_api_hash(public_key, private_key)

    base_url = "https://gateway.marvel.com/v1/public/characters"
    params = {
        "apikey": public_key,
        "ts": str(int(time.time())),
        "hash": hash,
        "limit": 5,
    }

    try:
        response = requests.get(base_url, params=params)
    except Exception as E:
        raise str(E)

    if response.status_code == 200:
        data = response.json()

        characters = data["data"]["results"]
        for character in characters:
            print(character["name"])
    else:
        print(response)
        print("Erro ao consultar a API da Marvel.")

    return data["data"]["results"]
