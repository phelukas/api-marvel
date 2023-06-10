from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate


def init_app(app):
    print("aqui viuuuuuuuu")
    db.init_app(app)
    with app.app_context():
        print("oioioi")
        s = db.create_all()
        print("ssssssssssss")
        print(db)
    return db
