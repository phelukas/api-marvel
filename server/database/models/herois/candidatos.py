from server.database import db


class Candidates(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    image = db.Column(db.LargeBinary)
    foto = db.Column(db.String(100))

    def __repr__(self):
        return f"<Candidate {self.name}>"
