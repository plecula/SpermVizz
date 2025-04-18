# tu backend Flask (lub potem FastAPI)

from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
@app.route('/index.html')
def home():
    return render_template('index.html')

@app.route('/logowanie.html')
def login():
    return render_template('logowanie.html')

@app.route('/wideo.html')
def video():
    return render_template('wideo.html')

if __name__ == '__main__':
    app.run(debug=True)
