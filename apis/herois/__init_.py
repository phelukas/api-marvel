from flask_restx import Api

api = Api()


def init_app(app):
    return api
