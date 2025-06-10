from flask import Flask, render_template, request, redirect, url_for, session, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import os
import hashlib
from utils import calculate_sha256
from werkzeug.utils import secure_filename
from utils import send_file_socket, calculate_sha256
from flask import send_from_directory

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['DOWNLOAD_FOLDER'] = 'downloads'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['DOWNLOAD_FOLDER'], exist_ok=True)

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(150))

class FileHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sender = db.Column(db.String(150))
    receiver = db.Column(db.String(150))
    filename = db.Column(db.String(200))
    sha256 = db.Column(db.String(64))

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
def index():
    return redirect('/login')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        user = User(username=request.form['username'], password=request.form['password'])
        db.session.add(user)
        db.session.commit()
        return redirect('/login')
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = User.query.filter_by(username=request.form['username'], password=request.form['password']).first()
        if user:
            login_user(user)
            return redirect('/dashboard')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect('/login')

@app.route('/dashboard', methods=['GET', 'POST'])
@login_required
def dashboard():
    users = User.query.filter(User.username != current_user.username).all()
    history = FileHistory.query.filter((FileHistory.sender==current_user.username) | (FileHistory.receiver==current_user.username)).all()
    return render_template('dashboard.html', users=users, history=history)

@app.route('/upload', methods=['POST'])
@login_required
def upload():
    file = request.files['file']
    receiver = request.form['receiver']
    filename = secure_filename(file.filename)
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(filepath)

    sha256 = calculate_sha256(filepath)

    new_entry = FileHistory(sender=current_user.username, receiver=receiver, filename=filename, sha256=sha256)
    db.session.add(new_entry)
    db.session.commit()

    return redirect('/dashboard')

@app.route('/download/<filename>')
@login_required
def download(filename):
    return send_from_directory(app.config['DOWNLOAD_FOLDER'], filename, as_attachment=True)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
