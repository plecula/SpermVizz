# tu backend Flask (lub potem FastAPI)

from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt     # for password protection
from flask_login import LoginManager, login_user, login_required, logout_user, UserMixin
from flask import session
from werkzeug.utils import secure_filename
import os
from dotenv import load_dotenv
from pathlib import Path

load_dotenv()
app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY")

# MYSQL DATABASE CONFIG

BASE_DIR = Path(__file__).resolve().parent.parent
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:@localhost/SpermVizz' # os.getenv("DATABASE_URL")  #'mysql+pymysql://root:@localhost/SpermVizz'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['MODEL_FOLDER'] = os.path.join(BASE_DIR, 'video_processing', 'models')

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'      # if not registered, go to login page


# USER MODEL
class User(db.Model, UserMixin):        # UserMixin for is_active() etc.
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# HOME
@app.route('/')
@app.route('/index.html')
def home():
    return render_template('index.html')

# REGISTER
@app.route('/register.html', methods=['GET','POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

        # CHECK IF USER EXISTS
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash('THIS USERNAME ALREADY EXISTS')
            return redirect(url_for('register'))
        
        new_user = User(username=username, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        flash('REGISTERED SUCCESSFULLY')
        return redirect(url_for('login'))
    return render_template('register.html')

# LOGIN
@app.route('/logowanie.html', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()

        if user and bcrypt.check_password_hash(user.password, password):
            login_user(user)
            flash('LOGGED IN')
            session['username'] = username  # <- np. 'Anna'
            return redirect(url_for('video'))
        else:
            flash('WRONG DATA')
    return render_template('logowanie.html')

# UPLOAD
@app.route('/wideo.html', methods=['GET', 'POST'])
@login_required
def video():

     # FILES LIST IN UPLOAD_FOLDER
    upload_folder = app.config['UPLOAD_FOLDER']
    files = os.listdir(upload_folder)
    files = [f for f in files if os.path.isfile(os.path.join(upload_folder, f))]

    if request.method == 'POST':
        file = request.files['file']
        if file.filename == '':
            flash('No file selected!')
            return redirect(request.url)
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

        flash('Upload successful!')
        #return redirect(url_for('video'))

        return render_template('wideo.html', files =files)

    return render_template('wideo.html', files =files)

# MY ACCOUNT - SEGMENTATION INTERFACE
@app.route('/segmentacja.html', methods=['GET', 'POST'])
@login_required
def interface():

    # SEGMENTATION MODEL LIST IN MODEL FOLDER
    model_folder = app.config['MODEL_FOLDER']
    models = os.listdir(model_folder)
    models = [m for m in models if os.path.isfile(os.path.join(model_folder, m))]

    # FILE LIST IN UPLOAD FOLDER
    upload_folder = app.config['UPLOAD_FOLDER']
    files = os.listdir(upload_folder)
    files = [f for f in files if os.path.isfile(os.path.join(upload_folder, f))]

    return render_template('segmentacja.html',models=models, files=files)

# MY ACCOUNT - COMPARE MODELS
@app.route('/compare.html', methods=['GET', 'POST'])
@login_required
def compareUI():
    # SEGMENTATION MODEL LIST IN MODEL FOLDER
    model_folder = app.config['MODEL_FOLDER']
    models = os.listdir(model_folder)
    models = [m for m in models if os.path.isfile(os.path.join(model_folder, m))]

    # FILE LIST IN UPLOAD FOLDER
    upload_folder = app.config['UPLOAD_FOLDER']
    files = os.listdir(upload_folder)
    files = [f for f in files if os.path.isfile(os.path.join(upload_folder, f))]

    return render_template('compare.html',models=models, files=files)

# MY ACCOUNT - SPERM CELL TRACK
@app.route('/tracking.html', methods=['GET', 'POST'])
@login_required
def trackUI():
    # SEGMENTATION MODEL LIST IN MODEL FOLDER
    model_folder = app.config['MODEL_FOLDER']
    models = os.listdir(model_folder)
    models = [m for m in models if os.path.isfile(os.path.join(model_folder, m))]

    # FILE LIST IN UPLOAD FOLDER
    upload_folder = app.config['UPLOAD_FOLDER']
    files = os.listdir(upload_folder)
    files = [f for f in files if os.path.isfile(os.path.join(upload_folder, f))]

    return render_template('tracking.html',models=models, files=files)


# SEGMENTATION MODELS
@app.route('/video_processing/<path:modelname>')
@login_required
def video_processing(modelname):
    return f"Modle path: {modelname}"

# LOGOUT
@app.route('/logout', methods=['POST'])
@login_required
def logout():
    logout_user()
    flash('LOGGED OUT')
    session.pop('username', None)
    return redirect(url_for('home'))


if __name__ == '__main__':
    app.run(debug=True)

# with app.app_context():
#      db.create_all()  # tworzy tabele w bazie