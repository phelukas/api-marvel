from typing import Dict
import pika
import json
import os


class Rabbitmq:
    def __init__(self) -> None:
        self.__host = os.environ["RABBITMQ_HOST"]
        self.__port = os.environ["RABBITMQ_PORT"]
        self.__username = os.environ["RABBITMQ_USER"]
        self.__password = os.environ["RABBITMQ_PASSWORD"]
        self.__connection = self.__create_connection()
        self.__exchange = self.__create_exchange()
        self.__create_queues()

    def __create_connection(self):
        connection_parameters = pika.ConnectionParameters(
            host=self.__host,
            port=self.__port,
            credentials=pika.PlainCredentials(
                username=self.__username, password=self.__password
            ),
        )
        connection = pika.BlockingConnection(connection_parameters)
        return connection

    def __create_exchange(self):
        exchange_name = "marvel_exchanges"
        channel = self.__connection.channel()
        channel.exchange_declare(exchange=exchange_name, exchange_type="direct")
        channel.close()
        return exchange_name

    def __create_queues(self):
        queue_add_heroi = "add_heroi"
        queue_challenge_day = "challenge_day"
        channel = self.__connection.channel()
        channel.queue_declare(queue=queue_add_heroi)
        channel.queue_declare(queue=queue_challenge_day)
        channel.queue_bind(
            exchange=self.__exchange, queue=queue_add_heroi, routing_key="add_hero"
        )
        channel.queue_bind(
            exchange=self.__exchange,
            queue=queue_challenge_day,
            routing_key="challenge_day",
        )
        channel.close()

    def __send_message(self, body: Dict, routing_key: str):
        channel = self.__connection.channel()

        channel.basic_publish(
            exchange=self.__exchange,
            routing_key=routing_key,
            body=json.dumps(body),
            properties=pika.BasicProperties(delivery_mode=2),
        )
        channel.close()

    def __check_queue_exist(self, fila):
        channel = self.__connection
        fila_declare_ok = channel.queue_declare(queue=fila, passive=True)
        channel.close()
        return fila_declare_ok.method.queue == fila

    def __consumer_queue(self, fila, callback):
        print("estou aqui no inicio")
        try:
            channel = self.__connection.channel()

            while True:
                method_frame, properties, body = channel.basic_get(
                    queue=fila, auto_ack=True
                )

                if method_frame is None:
                    break

                callback(json.loads(body.decode("utf-8")))

        finally:
            channel.close()

    def send_menssage(self, body: Dict, routing_key: str):
        return self.__send_message(body, routing_key)

    def consumer_queue(self, fila: str, callback):
        return self.__consumer_queue(fila, callback)
