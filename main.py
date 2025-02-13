from flask import Flask
from flask import render_template

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/doctors')
def doctors():
    return render_template('doctors.html')

@app.route('/services')
def services():
    return render_template('services.html')

@app.route('/schedule')
def schedule():
    return render_template('schedule.html')

@app.route('/news')
def news():
    return render_template('news.html')
