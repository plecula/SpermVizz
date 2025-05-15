# tu backend Flask (lub potem FastAPI)

from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt     # for password protection
from flask_login import LoginManager, login_user, login_required, logout_user, UserMixin
from flask import session
from werkzeug.utils import secure_filename
import os
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY")

# MYSQL DATABASE CONFIG

app.config['SQLALCHEMY_DATABASE_URI'] = 'os.getenv("DATABASE_URL")' # os.getenv("DATABASE_URL")  #mysql+pymysql://root:@localhost/SpermVizz
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'static/uploads'

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'      # if not registered, go to login page


# USER MODEL
class User(db.Model, UserMixin):        # UserMixin for is_active() etc.
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    #videos = db.relationship('Video', backref='user', lazy=True)

# VIDEO MODEL
# class Video(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     filename = db.Column(db.String(200), nullable=False)
#     user_id = db.Column(db.Integer, db.ForeignKey('user_id'), nullable=False)

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
    if request.method == 'POST':
        file = request.files['file']
        if file.filename == '':
            flash('No file selected!')
            return redirect(request.url)
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

        flash('Upload successful!')
        #return redirect(url_for('video'))

        return render_template('segmentacja.html')

    # FILES LIST IN UPLOAD_FOLDER
    upload_folder = app.config['UPLOAD_FOLDER']
    files = os.listdir(upload_folder)
    files = [f for f in files if os.path.isfile(os.path.join(upload_folder, f))]

    # # FILE INFO COMMITED TO DATABASE
    # new_video = Video(filename=filename, user_id=session['user_id'])
    # db.session.add(new_video)
    # db.session.commit()

    return render_template('wideo.html', files =files)

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
