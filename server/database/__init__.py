from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()


def init_app(app):
    db.init_app(app)
    from server.database import models

    with app.app_context():
        db.create_all()
    return db
