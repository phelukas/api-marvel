import pytz
from server.api.api_marvel import consulta_api
from apscheduler.schedulers.blocking import BlockingScheduler
import pika
import json


def agendador():
    print("INICIANDO SCHEDULAR")
    tz = pytz.timezone("America/Sao_Paulo")
    scheduler = BlockingScheduler()

    try:
        scheduler.add_job(enfileramento, "interval", minutes=1)

        scheduler.start()
    except Exception as E:
        print("*" * 100)
        print(E)
        print("*" * 100)
