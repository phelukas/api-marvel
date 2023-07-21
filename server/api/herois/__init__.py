from flask_restx import Resource
from server.api import api
from server.database import db
from server.api.api_marvel import consulta_api
import requests


np_herois = api.namespace("herois", description="Herois")


class HeroisAPIView(Resource):
    def get(self):
        return {"consulta": consulta_api()}


np_herois.add_resource(HeroisAPIView, "/")
