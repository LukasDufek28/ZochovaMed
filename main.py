from flask import Flask, render_template, redirect, url_for, request, flash
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from forms import NewsForm, ReservationForm, SessionRecordForm
from models import db, User, Session, News
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Vytvorenie databázy a testovacích používateľov
# Vytvorenie databázy a testovacích používateľov
with app.app_context():
    db.create_all()
    if not User.query.filter_by(email="doktor@test.com").first():
        # Pridanie doktorských účtov
        doctors = [
            User(firstname="Jan", lastname="Doktor", email="doktor@test.com", password_hash=generate_password_hash("heslo123"), role="doktor"),
            User(firstname="Anna", lastname="Zdravotnik", email="anna.doktor@test.com", password_hash=generate_password_hash("heslo123"), role="doktor"),
            User(firstname="Martin", lastname="Lekar", email="martin.doktor@test.com", password_hash=generate_password_hash("heslo123"), role="doktor"),
            User(firstname="Eva", lastname="Doktorka", email="eva.doktor@test.com", password_hash=generate_password_hash("heslo123"), role="doktor"),
        ]
        
        # Pridanie pacientskych účtov
        patients = [
            User(firstname="Peter", lastname="Pacient", email="pacient@test.com", password_hash=generate_password_hash("heslo123"), role="pacient"),
            User(firstname="Jana", lastname="Pacientova", email="jana.pacient@test.com", password_hash=generate_password_hash("heslo123"), role="pacient"),
            User(firstname="Viktor", lastname="Pacient", email="viktor.pacient@test.com", password_hash=generate_password_hash("heslo123"), role="pacient"),
            User(firstname="Maria", lastname="Pacientka", email="maria.pacient@test.com", password_hash=generate_password_hash("heslo123"), role="pacient"),
            User(firstname="Tomas", lastname="Pacient", email="tomas.pacient@test.com", password_hash=generate_password_hash("heslo123"), role="pacient"),
            User(firstname="Sima", lastname="Pacientka", email="sima.pacient@test.com", password_hash=generate_password_hash("heslo123"), role="pacient"),
            User(firstname="Ada", lastname="Pacientova", email="ada.pacient@test.com", password_hash=generate_password_hash("heslo123"), role="pacient"),
            User(firstname="Filip", lastname="Pacient", email="filip.pacient@test.com", password_hash=generate_password_hash("heslo123"), role="pacient"),
            User(firstname="Lara", lastname="Pacientka", email="lara.pacient@test.com", password_hash=generate_password_hash("heslo123"), role="pacient"),
            User(firstname="Riso", lastname="Pacient", email="riso.pacient@test.com", password_hash=generate_password_hash("heslo123"), role="pacient"),
            User(firstname="Barbora", lastname="Pacientka", email="barbora.pacient@test.com", password_hash=generate_password_hash("heslo123"), role="pacient"),
        ]

        # Uloženie všetkých používateľov do databázy
        db.session.add_all(doctors + patients)
        db.session.commit()


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            return redirect(url_for('main_page'))
        flash('Nesprávny email alebo heslo.')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/')
@login_required
def main_page():
    if current_user.role == 'doktor':
        sessions = Session.query.filter_by(doctor_id=current_user.id, valid=True).filter(Session.diagnosis.is_(None), Session.medication.is_(None)).order_by(Session.date).all()
    else:
        sessions = Session.query.filter_by(patient_id=current_user.id, valid=True).filter(Session.diagnosis.is_(None), Session.medication.is_(None)).order_by(Session.date).all()
    return render_template('main.html', sessions=sessions)

@app.route('/news', methods=['GET', 'POST'])
@login_required
def news():
    form = NewsForm()
    if form.validate_on_submit() and current_user.role == 'doktor':
        news = News(title=form.title.data, content=form.content.data, author_id=current_user.id)
        db.session.add(news)
        db.session.commit()
        flash('Článok pridaný.')
        form.title.data = ''  # Vyčistenie formulára
        form.content.data = ''
    articles = News.query.order_by(News.id.desc()).all()
    return render_template('news.html', form=form, articles=articles)

@app.route('/reservation', methods=['GET', 'POST'])
@login_required
def reservation():
    if current_user.role != 'pacient':
        return redirect(url_for('main_page'))
    form = ReservationForm()
    form.doctor.choices = [(d.id, f"{d.firstname} {d.lastname}") for d in User.query.filter_by(role='doktor').all()]
    
    if form.validate_on_submit():
        selected_date = form.date.data
        selected_time_str = form.time.data
        selected_time = datetime.strptime(selected_time_str, '%H:%M').time()
        selected_doctor_id = form.doctor.data
        today = datetime.now().date()

        # Check if a session already exists with the same doctor, date, and time
        existing_session = Session.query.filter_by(
            doctor_id=selected_doctor_id,
            date=selected_date,
            time=selected_time
        ).first()

        if selected_date < today:
            flash('You cannot book a session in the past.')
        elif selected_date.weekday() >= 5:
            flash('Sessions can only be booked on weekdays.')
        elif existing_session:
            flash('This time slot is already booked with the selected doctor.')
        else:
            session = Session(
                doctor_id=selected_doctor_id,
                patient_id=current_user.id,
                date=selected_date,
                time=selected_time,
                description=form.description.data
            )
            db.session.add(session)
            db.session.commit()
            flash('Your session has been successfully booked.')
            return redirect(url_for('main_page'))
    return render_template('reservation.html', form=form)

@app.route('/confirm', methods=['GET', 'POST'])
@login_required
def confirm():
    if current_user.role != 'doktor':
        return redirect(url_for('main_page'))
    sessions = Session.query.filter_by(doctor_id=current_user.id, valid=False).all()
    return render_template('confirm.html', sessions=sessions)

@app.route('/confirm_session/<int:session_id>', methods=['POST'])
@login_required
def confirm_session(session_id):
    if current_user.role != 'doktor':
        return redirect(url_for('main_page'))
    session = Session.query.get_or_404(session_id)
    if session.doctor_id != current_user.id:
        flash('Nemôžete potvrdiť tento termín.')
    else:
        session.valid = True
        db.session.commit()
        flash('Termín bol potvrdený.')
    sessions = Session.query.filter_by(doctor_id=current_user.id, valid=False).all()
    return render_template('confirm.html', sessions=sessions)

@app.route('/session_record/<int:session_id>', methods=['GET', 'POST'])
@login_required
def session_record(session_id):
    if current_user.role != 'doktor':
        return redirect(url_for('main_page'))
    session = Session.query.get_or_404(session_id)
    form = SessionRecordForm()
    if form.validate_on_submit():
        session.diagnosis = form.diagnosis.data
        session.medication = form.medication.data
        db.session.commit()
        flash('Zápis odoslaný.')
        form.diagnosis.data = ''  # Vyčistenie formulára
        form.medication.data = ''
    return render_template('session_record.html', form=form, session=session)

@app.route('/pickup', methods=['GET', 'POST'])
@login_required
def pickup():
    if current_user.role != 'pacient':
        return redirect(url_for('main_page'))
    if request.method == 'POST':
        session_id = request.form['session_id']
        session = Session.query.get_or_404(session_id)
        if session.patient_id == current_user.id:
            db.session.delete(session)
            db.session.commit()
            flash('Liek vyzdvihnutý.')
    sessions = Session.query.filter_by(patient_id=current_user.id).filter(Session.diagnosis.isnot(None), Session.medication.isnot(None)).all()
    return render_template('pickup.html', sessions=sessions)

if __name__ == '__main__':
    app.run(debug=True)