from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from datetime import date
import sqlite3
import os
from datetime import datetime
import re
from app.routes.mahasiswa import mahasiswa_bp
from app.routes.koordinator import koordinator_bp
from app.routes.penguji import penguji_bp
from app.routes.pembimbing import pembimbing_bp

app = Flask(__name__)
app.secret_key = os.urandom(24)
import os
UPLOAD_FOLDER = os.path.join(os.path.dirname(app.root_path), 'uploads', 'bap')


app.register_blueprint(mahasiswa_bp, url_prefix='/mahasiswa')
app.register_blueprint(koordinator_bp, url_prefix='/koordinator')
app.register_blueprint(penguji_bp, url_prefix='/penguji')
app.register_blueprint(pembimbing_bp, url_prefix='/pembimbing')

def get_db_connection():
    conn = sqlite3.connect('database/database.db') 
    conn.row_factory = sqlite3.Row 
    return conn

@app.before_request
def require_login():
    allowed_routes = ['login', 'static']
    if 'email' not in session and request.endpoint not in allowed_routes:
        return redirect(url_for('login'))

@app.route('/')
def index():
    return redirect(url_for('/login'))

@app.route('/login', methods=['GET','POST'])
def login():
    if(request.method == 'GET'):
        return render_template('login.html')
    else:
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')
        if(request.is_json):
            data = request.get_json()
            email = data.get('email')
            password = data.get('password')
            print(email)
            print(password)
            conn = get_db_connection()
            cursor = conn.cursor()

            cursor.execute("SELECT * FROM Mahasiswa WHERE email = ? AND password = ?", (email, password))
            mahasiswa = cursor.fetchone()
            

            cursor.execute("SELECT * FROM Penguji WHERE email = ? AND password = ?", (email, password))
            penguji = cursor.fetchone()
            
            cursor.execute("SELECT * FROM Pembimbing WHERE email = ? AND password = ?", (email, password))
            pembimbing = cursor.fetchone()

            cursor.execute("SELECT * FROM Koordinator WHERE email = ? AND password = ?", (email, password))
            koordinator = cursor.fetchone()

            if(mahasiswa or penguji or pembimbing or koordinator):
                print('tes')
                session['email'] = email
                session['password'] = password
                if(mahasiswa):
                    session['role'] = "mahasiswa"
                    session['nama'] = mahasiswa['nama']
                    session['id'] = mahasiswa['npm']
                    return jsonify({'info': 'mahasiswa'})
                elif(penguji):
                    session['role'] = "penguji"
                    session['nama'] = penguji['nama']
                    session['id'] = penguji['nik']
                    return jsonify({'info': 'penguji'})
                elif(pembimbing):
                    print('dia pembimbing')
                    session['role'] = "pembimbing"
                    session['nama'] = pembimbing['nama']
                    session['id'] = pembimbing['nik']
                    return jsonify({'info': 'pembimbing'})
                elif(koordinator):
                    print('dia koordinator')
                    session['role'] = "koordinator"
                    session['nama'] = koordinator['nama']
                    session['id'] = koordinator['nik']
                    return jsonify({'info': 'koordinator'})
                
            else:
                return jsonify({'info': 'not found'})

if __name__ == '__main__':
    os.makedirs('database', exist_ok=True)
    app.run(debug=True)