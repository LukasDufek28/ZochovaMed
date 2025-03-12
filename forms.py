from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField, SelectField, DateField
from wtforms.validators import DataRequired
from datetime import time

class NewsForm(FlaskForm):
    title = StringField('Názov', validators=[DataRequired()])
    content = TextAreaField('Obsah', validators=[DataRequired()])
    submit = SubmitField('Pridať článok')

class ReservationForm(FlaskForm):
    doctor = SelectField('Doktor', coerce=int, validators=[DataRequired()])
    date = DateField('Dátum', validators=[DataRequired()])
    time_choices = [
        ('09:00', '09:00'), ('09:30', '09:30'),
        ('10:00', '10:00'), ('10:30', '10:30'),
        ('11:00', '11:00'), ('11:30', '11:30'),
        ('12:00', '12:00'), ('12:30', '12:30'),
        ('13:00', '13:00'), ('13:30', '13:30'),
        ('14:00', '14:00'), ('14:30', '14:30'),
        ('15:00', '15:00')
    ]
    time = SelectField('Čas', choices=time_choices, validators=[DataRequired()])
    description = TextAreaField('Popis problému', validators=[DataRequired()])
    submit = SubmitField('Rezervovať')

class SessionRecordForm(FlaskForm):
    diagnosis = TextAreaField('Diagnóza', validators=[DataRequired()])
    medication = StringField('Liek', validators=[DataRequired()])
    submit = SubmitField('Odoslať')