from server.database import db


class Palpite(db.Model):
    __tablename__ = "palpite"

    id = db.Column(db.Integer, primary_key=True)

    usuario_id = db.Column(db.Integer, db.ForeignKey("usuario.id"), nullable=False)
    desafio_id = db.Column(db.Integer, db.ForeignKey("desafio.id"), nullable=True)

    resposta = db.Column(db.String(100))
    acertou = db.Column(db.Integer)

    usuario = db.relationship(
        "Usuario", backref=db.backref("usuario_palpite", lazy=True)
    )
    desafio = db.relationship(
        "Desafio", backref=db.backref("desafio_palpite", lazy=True)
    )
