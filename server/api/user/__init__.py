from flask import Flask
from flask_restx import Api, Resource, fields
from server.api import api
from server.database import db
from server.database.models.usuarios import Usuario
import bcrypt
import app


np_user = api.namespace("user", description="user")

# Definindo o modelo do usuário
user_model = api.model(
    "User",
    {
        "name": fields.String(required=True),
        "email": fields.String(required=True),
        "password": fields.String(required=True),
    },
)

user_model_get = api.model(
    "User",
    {
        "id": fields.String(required=True),
        "nome": fields.String(required=True),
        "email": fields.String(required=True),
        "senha": fields.String(required=True),
    },
)


# Rota para obter todos os usuários
@np_user.route("/")
class UsersResource(Resource):
    @np_user.marshal_with(user_model_get)
    def get(self):
        users = Usuario.query.all()
        return users

    @np_user.expect(user_model)
    @np_user.marshal_with(user_model, code=201)
    def post(self):
        user = api.payload
        hashed_password = bcrypt.hashpw(
            user["password"].encode("utf-8"), bcrypt.gensalt()
        )
        user["password"] = hashed_password.decode("utf-8")
        with app.app.app_context():
            try:
                obj = Usuario()
                obj.email = user["email"]
                obj.nome = user["name"]
                obj.senha = user["password"]
                db.session.add(obj)
                db.session.commit()
            except Exception as error:
                raise (str(error))
        return user, 201


# Rota para obter um usuário específico
@np_user.route("/<int:user_id>/")
class UserResource(Resource):
    @np_user.marshal_with(user_model_get)
    def get(self, user_id):
        try:
            user = Usuario.query.filter_by(id=user_id).first()
            return user
        except:
            api.abort(404, message="Usuário não encontrado")

    # @np_user.expect(user_model)
    # @np_user.marshal_with(user_model)
    # def put(self, user_id):
    #     user_data = api.payload
    #     for user in users:
    #         if user["id"] == user_id:
    #             user.update(user_data)
    #             return user
    #     api.abort(404, message="Usuário não encontrado")

    # @np_user.response(204, "Usuário excluído com sucesso")
    # def delete(self, user_id):
    #     for user in users:
    #         if user["id"] == user_id:
    #             users.remove(user)
    #             return "", 204
    #     api.abort(404, message="Usuário não encontrado")
