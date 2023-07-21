from flask_restx import Api

api = Api()


def init_app(app):
    api.init_app(app)
    from server.api import herois, user

    return api
