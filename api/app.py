import os
import base64
import requests
from urllib.request import urlopen
from wtforms import Form, validators
from flask_sqlalchemy import SQLAlchemy
from wtforms_sqlalchemy.fields import QuerySelectField
from flask import Flask, render_template, request, jsonify


basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] =\
    'sqlite:///' + os.path.join(basedir, 'database.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)


@app.before_first_request
def init_database():
    db.create_all()


teams = db.Table(
    'teams',
    db.Column('candidate_id', db.Integer, db.ForeignKey(
        'candidates.id'), primary_key=True),
    db.Column('team_id', db.Integer, db.ForeignKey(
        'team.id'), primary_key=True)
)


class Candidates(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    image = db.Column(db.LargeBinary)
    foto = db.Column(db.String(100))

    def __repr__(self):
        return f"<Candidate {self.name}>"


class Team(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    tipo_time = db.Column(db.String(100), nullable=False)
    candidates = db.relationship(
        'Candidates', secondary=teams, lazy='subquery', backref=db.backref('teams', lazy=True))

    def __repr__(self):
        return f"<Team {self.name}>"


class FormAddHeroTeam(Form):

    def get_team():
        return Team.query

    time = QuerySelectField("Nome do Time", validators=[
                            validators.DataRequired()], get_label='name', query_factory=get_team)


def make_url(category, name=None):
    ts = os.getenv('ts')
    apikey = os.getenv('apikey')
    hash = os.getenv('hash')
    url_base = "https://gateway.marvel.com:443/v1/public"

    url = f"{url_base}/{category}?ts={ts}&apikey={apikey}&hash={hash}"
    if name:
        url = f"{url_base}/{category}?name={name}&ts={ts}&apikey={apikey}&hash={hash}"
    return url


def render_picture(data):
    render_pic = base64.b64encode(urlopen(data).read())
    return render_pic


@app.route('/heroes/', methods=('GET', 'POST'))
def list_heroes():
    url = make_url(category="characters")
    request_ = requests.request("GET", url)

    if request_.status_code != 200:
        return {"erro": str(request_.json()['message'])}

    results = request_.json()['data']['results']
    response = []

    for result in results:
        data = {}
        data['nome'] = result['name']
        data['descricao'] = result['description']
        data['foto'] = result['thumbnail']['path']
        data['extensao_foto'] = result['thumbnail']['extension']
        response.append(data)

    form = FormAddHeroTeam()

    if request.method == 'POST':
        name_hero = request.form['heroName']
        team_id = request.form['teamId']
        team = Team.query.get_or_404(team_id)

        url = make_url(category="characters", name=str(name_hero))
        results = requests.request("GET", url).json()['data']['results']

        for result in results:
            data = {}
            data['nome'] = result['name']
            data['descricao'] = result['description']
            data['foto'] = f"{result['thumbnail']['path']}.{result['thumbnail']['extension']}"
            data['extensao_foto'] = result['thumbnail']['extension']

        candidato = Candidates(
            name=data['nome'],
            description=data['descricao'],
            image=render_picture(data['foto']),
            foto=data['foto']
        )

        db.session.add(candidato)
        db.session.commit()
        candidatos = []
        candidatos.append(candidato)

        team.candidates += candidatos

        db.session.add(team)
        db.session.commit()

    return render_template('heroes_list.html', heroes=response, form=form)


@app.route('/hero/', methods=["POST"])
def hero():
    if request.method == 'POST':
        heroname = request.form['heroname']

        url = make_url(category="characters", name=str(heroname))
        results = requests.request("GET", url).json()['data']['results']
        response = []

        for result in results:
            data = {}
            data['nome'] = result['name']
            data['descricao'] = result['description']
            data['foto'] = result['thumbnail']['path']
            data['extensao_foto'] = result['thumbnail']['extension']
            response.append(data)

    return jsonify({'htmlresponse': render_template('hero.html', employeelist=response)})


@app.route('/teams/')
def list_teams():
    teams = Team.query.all()
    return render_template('team_list.html', teams=teams)


@app.route('/teams/add/', methods=('GET', 'POST'))
def create_team():

    if request.method == 'POST':
        teamname = request.form['teamName']
        teamtype = request.form['teamTipo']

        if teamtype == 1:
            teamtype = "Equipe"
        else:
            teamtype = "Vingadores"

        data = {
            "time_nome": teamname,
            "time_tipo": teamtype
        }

        team = Team(
            name=teamname,
            tipo_time=teamtype
        )

        db.session.add(team)
        db.session.commit()
        return data

    return render_template('team_create.html')


@app.route('/teams/edit/<int:team_id>/', methods=('GET', 'POST'))
def edit_team(team_id):
    team = Team.query.get_or_404(team_id)

    if request.method == 'POST':
        teamname = request.form['teamName']
        teamtype = request.form['teamTipo']

        if teamtype == 1:
            teamtype = "Equipe"
        else:
            teamtype = "Vingadores"

        team.name = teamname
        team.tipo_time = teamtype

        db.session.add(team)
        db.session.commit()

        data = {
            "time_nome": teamname,
            "time_tipo": teamtype
        }

        return data

    return render_template('team_edit.html', team=team)
