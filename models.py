from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin

db = SQLAlchemy()

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    firstname = db.Column(db.String(50), nullable=False)
    lastname = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    role = db.Column(db.String(10), nullable=False)  # 'doktor' alebo 'pacient'

class Session(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    doctor_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    patient_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    time = db.Column(db.Time, nullable=False)
    medication = db.Column(db.String(100))  # Prázdne, kým lekár nevyplní
    diagnosis = db.Column(db.Text)  # Prázdne, kým lekár nevyplní
    valid = db.Column(db.Boolean, default=False)  # Čaká na potvrdenie
    description = db.Column(db.Text)  # Popis problému od pacienta
    doctor = db.relationship('User', foreign_keys=[doctor_id], backref='doctor_sessions')
    patient = db.relationship('User', foreign_keys=[patient_id], backref='patient_sessions')

class News(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    author = db.relationship('User', backref='news')