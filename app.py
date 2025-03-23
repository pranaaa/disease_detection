from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import cv2
import csv
import numpy as np
from tensorflow.keras.applications.resnet50 import preprocess_input
from tensorflow.keras.models import load_model
from sklearn.preprocessing import LabelEncoder
from aixplain.factories import ModelFactory

app = Flask(__name__)
import secrets
secret_key = secrets.token_hex(24)
app.config['SECRET_KEY'] = secret_key  
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///yourdatabase.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    password = db.Column(db.String(80), nullable=False)
    is_active = db.Column(db.Boolean(), default=True)

    def __repr__(self):
        return f'<User {self.username}>'

# Routes
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
    
        if User.query.filter_by(username=username).first():
            flash("Username already exists!", "warning")
            return redirect(url_for('register'))
        
        
        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
        new_user = User(username=username, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        
        flash("Registered successfully. Please login.", "success")
        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        
        if user and check_password_hash(user.password, password):
            flash("Login successful!", "success")
            return redirect(url_for('index'))
        else:
            flash("Invalid username or password", "danger")
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    flash("You have been logged out.", "info")
    return redirect(url_for('login'))

@app.route('/')
def main_route():
    return redirect(url_for('login'))

@app.route('/index')
def index():
    return render_template('index.html')

@app.route('/about.html',methods=['GET'])
def about():
    
    return render_template('about.html')

@app.route('/contact.html',methods=['GET'])
def contact():
    
    return render_template('contact.html')

@app.route('/product.html',methods=['GET'])
def product():
    
    return render_template('product.html')

@app.route('/results.html',methods=['GET'])
def results():
    
    return render_template('results.html')
# AIXPLAIN_KEY="0fc6ca1e90db80b2855f7952d4e5e09499c05e0c375f0de32cfa4ecc49882e97"
@app.route('/results.html',methods=['POST'])
def predict_image_classification_sample():
    model = load_model('/Users/pranathiprabhala/Desktop/models/my_model.h5') 
    filename=request.files["fileipt"].read()
    nparr = np.fromstring(filename, np.uint8)
    '''
    model1 =  ModelFactory.get("61b097551efecf30109d32da")
    hindi_result = model1.run({"text": d})
    model2 = ModelFactory.get("61b097551efecf30109d32e3")
    kannada_result = model2.run({"text": d})
    '''
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    img = cv2.resize(img, (224,224))
    img = preprocess_input(np.array([img]))  
    predictions = model.predict(img)
    predicted_class_index = np.argmax(predictions)
    index_to_class = {}
    with open('label_mapping.csv', mode='r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            index_to_class[int(row['Index'])] = row['Class Name']
    col=index_to_class[predicted_class_index]
    confidence = np.max(predictions)
    d=col
    return render_template('results.html',disease=d,confidence=confidence)
print("starting..")

# Initialize the database if running for the first time
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(port=3000, debug=True)
