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
import cv2
import uuid  # do tworzenia unikalnych folderów
from flask import jsonify
from segment_anything import sam_model_registry, SamAutomaticMaskGenerator
import numpy as np
import time
import torch

#os.environ["PYTORCH_CUDA_ALLOC_CONF"] = "expandable_segments:True" # for better performance

load_dotenv()
app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY")

# MYSQL DATABASE CONFIG

BASE_DIR = Path(__file__).resolve().parent.parent
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:@localhost/SpermVizz'  #os.getenv("DATABASE_URL") # 'mysql+pymysql://root:@localhost/SpermVizz' 
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['MODEL_FOLDER'] = os.path.join(BASE_DIR, 'video_processing', 'models')

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'      # if not registered, go to login page

print(torch.cuda.is_available())

#print(torch.cuda.get_device_name(0))
# LOAD SEG MODEL
sam_checkpoint = BASE_DIR / "video_processing" / "models" / "sam_vit_b_01ec64.pth"      # or other one
model_type = "vit_b"
sam = sam_model_registry[model_type](checkpoint=sam_checkpoint)
sam.to("cuda")   # or cpu!!!  
mask_generator = SamAutomaticMaskGenerator(
    sam,
    pred_iou_thresh= 0.95,
    points_per_side=32
)

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

# EXTRACTING FRAMES FROM VIDEO
@app.route('/extract_frames_existing', methods=['POST'])
@login_required
def extract_frames_existing():
    filename = request.form['filename']
    video_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)


    # Name without .mp4 /  .avi
    name_without_ext = os.path.splitext(filename)[0]

    try:
        # Create new folder
        unique_folder = f"f_{name_without_ext}_{uuid.uuid4().hex[:3]}"
        frames_dir = os.path.join(app.config['UPLOAD_FOLDER'], unique_folder)
        os.makedirs(frames_dir, exist_ok=True)

        # Frames (OpenCV)
        interval = 1  # 1 sec
        cap = cv2.VideoCapture(video_path)
        fps = cap.get(cv2.CAP_PROP_FPS)
        frame_count = 0
        saved_count = 0
        interval_frames = int(fps * interval)
        frames_urls = []

        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            if frame_count % interval_frames == 0:
                frame_filename = f"frame_{saved_count+1}.jpg"
                frame_path = os.path.join(frames_dir, frame_filename)
                cv2.imwrite(frame_path, frame)
                frames_urls.append(url_for('static', filename=f"uploads/{unique_folder}/{frame_filename}"))
                saved_count += 1

            frame_count += 1

        cap.release()

        return jsonify({
            'success': True, 
            'frames': frames_urls,
            'folder': unique_folder
            })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

# SEGMENTATION FOR FRAMES
@app.route('/segment_frame/<folder>/<frame_name>', methods=['GET'])
@login_required
def segment_frame(folder, frame_name):
    try:
        frame_path = BASE_DIR / "app" / "static" / "uploads" / folder / frame_name

        if not frame_path.exists():
            return jsonify({'success': False, 'error': 'Frame not found'})
 
        start = time.time()
        image = cv2.imread(str(frame_path))
        
        with torch.no_grad():                   # saves memory
            masks = mask_generator.generate(image)
       
        masks_sorted = sorted(masks, key=lambda x: x['predicted_iou'], reverse=True)
        best_mask = masks_sorted[0]['segmentation']
        print("Mask generation time:", time.time() - start)
        
        # Save mask
        mask_filename = f"m_{frame_name}_{folder}_{uuid.uuid4().hex[:6]}"
        mask_path = BASE_DIR / "app" / "static" / "masks" / mask_filename
        os.makedirs(mask_path.parent, exist_ok=True)

        mask_image = (1 - best_mask) * 255
        cv2.imwrite(str(mask_path), mask_image.astype(np.uint8))

        return jsonify({
            'success': True, 
            'mask_url': url_for('static', filename=f"masks/{mask_filename}")
            })

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})


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