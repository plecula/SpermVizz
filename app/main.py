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
from segment_anything import sam_model_registry, SamAutomaticMaskGenerator, SamPredictor
import numpy as np
import time
import torch
import math

os.environ["PYTORCH_CUDA_ALLOC_CONF"] = "expandable_segments:True" # for better performance

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


# LOAD MODELS

loaded_models = {}

def get_mask_generator(model_name):
    if model_name in loaded_models:
        return loaded_models[model_name]

    model_type = 'vit_l' if 'vit_l' in model_name else 'vit_b'
    sam_checkpoint = BASE_DIR / "video_processing" / "models" / model_name
    sam = sam_model_registry[model_type](checkpoint=sam_checkpoint)
    
    sam.to("cpu")
        
    mask_generator = SamAutomaticMaskGenerator(
        sam,
        pred_iou_thresh=0.95,
        points_per_side=32
    )
    mask_generator.model = sam  # reference for fallback

    loaded_models[model_name] = mask_generator
    return mask_generator


def segment_frame_with_fallback(mask_generator, image):
   
    sam_model = mask_generator.model

    try:
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
            sam_model.to("cuda")
        else:
            sam_model.to("cpu")

        with torch.no_grad():
            masks = mask_generator.generate(image)

    except torch.cuda.OutOfMemoryError:
        print("OOM during generating — switching to CPU")

        if torch.cuda.is_available():
            torch.cuda.empty_cache()

        sam_model.to("cpu")

        with torch.no_grad():
            masks = mask_generator.generate(image)

    finally:
        sam_model.to("cpu")
        torch.cuda.empty_cache()

    return masks

# TRACKING SEGMENTATION

def track_and_segment_sperm(folder, point_coords, model_name):
    frame_folder = BASE_DIR / "app" / "static" / "uploads" / folder
    frame_files = sorted([f for f in os.listdir(frame_folder) if f.lower().endswith('.jpg')])

    sam_checkpoint = BASE_DIR / "video_processing" / "models" / model_name
    model_type = 'vit_l' if 'vit_l' in model_name else 'vit_b'
    sam = sam_model_registry[model_type](checkpoint=sam_checkpoint)
    
    # if torch.cuda.is_available():
    #     torch.cuda.empty_cache()
    #     sam.to("cuda")
    # else:
    #     sam.to("cpu")

    predictor = SamPredictor(sam)

    result_urls = []

    sam.to("cpu")       # or cuda

    for frame_file in frame_files:
        frame_path = frame_folder / frame_file
        image = cv2.imread(str(frame_path))
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

        predictor.set_image(image_rgb)

        input_points = np.array(point_coords)
        input_labels = np.array([1] * len(point_coords))

        masks, scores, logits = predictor.predict(
            point_coords=input_points,
            point_labels=input_labels,
            multimask_output=True
        )

        overlay = np.zeros_like(image_rgb, dtype=np.uint8)

        # Nakładamy maski — na przykład maskę o najwyższym score:
        best_mask = masks[0]

        overlay[:,:,0] = (best_mask * 255).astype(np.uint8)
        blended = cv2.addWeighted(image_rgb, 0.6, overlay, 0.3, 0)

        mask_filename = f"tracked_{frame_file}_{uuid.uuid4().hex[:6]}.png"
        mask_path = BASE_DIR / "app" / "static" / "masks" / mask_filename
        os.makedirs(mask_path.parent, exist_ok=True)

        cv2.imwrite(str(mask_path), cv2.cvtColor(blended, cv2.COLOR_RGB2BGR))

        result_urls.append(url_for('static', filename=f"masks/{mask_filename}"))

    return result_urls



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
    if torch.cuda.is_available() :
        torch.cuda.empty_cache()
    try:
        model_name = request.args.get('model')
        if not model_name:
            return jsonify({'success': False, 'error': 'No model specified!'})
    
        
        mask_generator = get_mask_generator(model_name)

        frame_path = BASE_DIR / "app" / "static" / "uploads" / folder / frame_name

        if not frame_path.exists():
            return jsonify({'success': False, 'error': 'Frame not found'})
 
        start = time.time()
        image = cv2.imread(str(frame_path))
        

        print(f"Processing frame: {frame_path}")
        print(f"Image shape: {image.shape}")

        with torch.no_grad():                   # saves memory
            #masks = mask_generator.generate(image)
            masks = segment_frame_with_fallback(mask_generator, image)

        print(f"Generated {len(masks)} masks")


        if not masks:
            return jsonify({'success': False, 'error': 'No masks found, maybe try lower pred_iou_thresh'})

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


# TRACKING SPERM CELL
@app.route('/track_and_segment_sperm', methods=['POST'])
@login_required
def track_and_segment_api():
    try:
        data = request.get_json()
        folder = data['folder']
        model_name = data['model']
        points = data['points']  # [[x1,y1],[x2,y2]]

        if not (folder and model_name and points):
            return jsonify({'success': False, 'error': 'Missing parameters'})

        result_urls = track_and_segment_sperm(folder, points, model_name)

        return jsonify({'success': True, 'results': result_urls})

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