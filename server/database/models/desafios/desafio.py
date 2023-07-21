from server.database import db


class Desafio(db.Model):
    __tablename__ = "desafio"

    id = db.Column(db.Integer, primary_key=True)
    data_desafio = db.Column(db.Date, nullable=False)
    usado = db.Column(db.Integer)
    heroi_id = db.Column(db.Integer, db.ForeignKey("heroi.id"), nullable=False)

    heroi = db.relationship("Heroi", backref=db.backref("heroi", lazy=True))
