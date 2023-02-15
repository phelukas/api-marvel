import os
import requests
import base64
from flask import Flask, render_template, request, url_for, redirect, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import func
from wtforms import Form, StringField, TextAreaField, BooleanField, validators
from wtforms_sqlalchemy.fields import QuerySelectMultipleField, QuerySelectField
from urllib.request import urlopen 



basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] =\
    'sqlite:///' + os.path.join(basedir, 'database.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)


class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    firstname = db.Column(db.String(100), nullable=False)
    lastname = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(80), unique=True, nullable=False)
    age = db.Column(db.Integer)
    created_at = db.Column(db.DateTime(timezone=True),
                           server_default=func.now())
    bio = db.Column(db.Text)

    def __repr__(self):
        return f'<Student {self.firstname}>'


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
        
    time = QuerySelectField("Nome do Time", validators=[validators.DataRequired()], get_label='name', query_factory=get_team)


def make_url(category, name=None):
    ts = "1675897305"
    apikey = "9c18ce40e88cc12edc7fc6b2fc90fbf4"
    hash = "3a418c4ca6453ea6b61f4a99a63a782c"
    url_base = "https://gateway.marvel.com:443/v1/public"
    url = f"{url_base}/{category}?ts={ts}&apikey={apikey}&hash={hash}"
    if name:
        url = f"{url_base}/{category}?name={name}&ts={ts}&apikey={apikey}&hash={hash}"
    return url


def render_picture(data):
    render_pic = base64.b64encode(urlopen(data).read())
    return render_pic

@app.route('/list/')
def list():
    url = make_url(category="characters")
    response = requests.request("GET", url)
    return response.json()


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
            image=render_picture(data['foto'])
        )

        db.session.add(candidato)
        db.session.commit()
        candidatos = []
        candidatos.append(candidato)
        print("aqui")
        print(candidatos)
        print(type(candidatos))
        print("aqui")

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

    # hero = Candidates.query.get_or_404(hero_id)
    return jsonify({'htmlresponse': render_template('hero.html', employeelist=response)})


# @app.route('/team/<int:team_id>/hero/', methods=('GET', 'POST'))
# def add_hero_team(team_id):
#     team = Team.query.get_or_404(team_id)
#     form = FormAddHeroTeam()
#     return render_template('')

    # if request.method == 'POST':


@app.route('/teams/')
def list_teams():
    teams = Team.query.all()
    return render_template('team_list.html', teams=teams)


@app.route('/teams/add/', methods=('GET', 'POST'))
def create_team():
    if request.method == 'POST':
        teamname = request.form['teamName']
        teamtype = request.form['teamTipo']

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


@app.route('/')
def index():
    students = Student.query.all()
    return render_template('index.html', students=students)


@app.route('/<int:student_id>/')
def student(student_id):
    student = Student.query.get_or_404(student_id)
    return render_template('student.html', student=student)


@app.route('/create/', methods=('GET', 'POST'))
def create():
    if request.method == 'POST':
        firstname = request.form['firstname']
        lastname = request.form['lastname']
        email = request.form['email']
        age = int(request.form['age'])
        bio = request.form['bio']
        student = Student(firstname=firstname,
                          lastname=lastname,
                          email=email,
                          age=age,
                          bio=bio)
        db.session.add(student)
        db.session.commit()

        return redirect(url_for('index'))

    return render_template('create.html')


@app.route('/<int:student_id>/edit/', methods=('GET', 'POST'))
def edit(student_id):
    student = Student.query.get_or_404(student_id)

    if request.method == 'POST':
        firstname = request.form['firstname']
        lastname = request.form['lastname']
        email = request.form['email']
        age = int(request.form['age'])
        bio = request.form['bio']

        student.firstname = firstname
        student.lastname = lastname
        student.email = email
        student.age = age
        student.bio = bio

        db.session.add(student)
        db.session.commit()

        return redirect(url_for('index'))

    return render_template('edit.html', student=student)


@app.post('/<int:student_id>/delete/')
def delete(student_id):
    student = Student.query.get_or_404(student_id)
    db.session.delete(student)
    db.session.commit()
    return redirect(url_for('index'))

    # <svg class="bd-placeholder-img rounded-circle" width="140" height="140"
    #     xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Placeholder: 140x140"
    #     preserveAspectRatio="xMidYMid slice" focusable="false">
    #     <title>Placeholder</title>
    #     <rect width="100%" height="100%" fill="#777" /><text x="50%" y="50%" fill="#777"
    #         dy=".3em">140x140</text>
    # </svg>
