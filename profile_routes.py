from flask import Blueprint, request, redirect, url_for, send_from_directory, session, current_app, render_template
from werkzeug.utils import secure_filename
import os
import mysql.connector

profile_bp = Blueprint('profile', __name__, static_folder='static')

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'static', 'uploaded_media')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_db_connection():
    return mysql.connector.connect(
        host        = current_app.config['MYSQL_HOST'],
        database    = current_app.config['MYSQL_DB'],
        user        = current_app.config['MYSQL_USER'],
        password    = current_app.config['MYSQL_PASSWORD']
    )

@profile_bp.route('/')
def profile():
    if 'username' in session:
        username = session['username']
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT profile_pic_url, banner_url FROM user WHERE username = %s", (username,))
        user_info = cursor.fetchone()
        return render_template('profile.html', username=username, profile_pic_url=user_info[0], banner_url=user_info[1])
    else:
        return redirect(url_for('index'))

@profile_bp.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return 'No file part', 400
    file = request.files['file']
    image_type = request.form.get('image_type', 'profile_pic')

    if file.filename == '':
        return 'No selected file', 400
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_path = os.path.join(UPLOAD_FOLDER, filename)
        file.save(file_path)

        conn = get_db_connection()
        cursor = conn.cursor()
        sql = "UPDATE user SET profile_pic_url = %s WHERE username = %s" if image_type == 'profile_pic' else "UPDATE user SET banner_url = %s WHERE username = %s"
        cursor.execute(sql, (filename, session['username']))
        conn.commit()
        return redirect(url_for('profile.profile'))
    return 'Invalid file', 400

@profile_bp.route('/uploads/<filename>')
def uploaded_file(filename):
    directory = os.path.join(current_app.root_path, current_app.static_folder, 'uploaded_media')
    return send_from_directory(directory, filename)

