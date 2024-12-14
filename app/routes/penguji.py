from flask import Blueprint, render_template, session, redirect, url_for, request, jsonify
import sqlite3

penguji_bp = Blueprint('penguji', __name__)


def get_db_connection():
    conn = sqlite3.connect('database/database.db') 
    conn.row_factory = sqlite3.Row 
    return conn

@penguji_bp.route('/')
def dashboard():
    return "Halaman Dashboard Mahasiswa"

@penguji_bp.before_request
def require_login():
    allowed_routes = ['login', 'static']
    if 'email' not in session and request.endpoint not in allowed_routes:
        return redirect(url_for('login'))

@penguji_bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@penguji_bp.route('/home')
def home():
    nama = session.get('nama', None)
    role = session.get('role', None)
    return render_template('penguji/penguji-home.html', nama = nama, role=role)

@penguji_bp.route('/info')
def info():
    nama = session.get('nama', None)
    role = session.get('role', None)
    id = session.get('id', None)
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("select * from InfoPengujiView where nik_penguji = ?", (id,))
    info = cursor.fetchall()
    return render_template('penguji/penguji-info.html', nama = nama, info=info)

@penguji_bp.route('/bap')
def bap():
    nama = session.get('nama', None)
    nik = session.get('id', None)
    if(request.method == 'GET'):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("select * from InfoPengujiView where nik_penguji = ?", (nik,))
        info = cursor.fetchall()
        return render_template('penguji/penguji-bap.html', nama = nama, info=info)
    

@penguji_bp.route('/nilai', methods=['GET', 'POST'])
def nilai():
    nik = session.get('id', None)
    nama = session.get('nama', None)
    if(request.method == 'GET'):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("select * from InfoPengujiView where nik_penguji = ?", (nik,))
        info = cursor.fetchall()
        return render_template('penguji/penguji-inputnilai.html', nama = nama, info=info)
    else:
        if(request.is_json):
            data = request.get_json()
            id_sidang = data['id_sidang']
            session['id_sidang'] = id_sidang
            print('id sidang: ' + id_sidang)
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("select * from nilai_penguji where nik = ? and ID_Sidang = ?", (nik, id_sidang,))
            rows = cursor.fetchall()
            nilai = [dict(row) for row in rows]
            return jsonify(nilai)
        
        else:
            tata_tulis = request.form.get('tata_tulis')
            kelengkapan_materi = request.form.get('kelengkapan_materi')
            pencapaian_tujuan = request.form.get('pencapaian_tujuan')
            penguasaan_materi = request.form.get('penguasaan_materi')
            presentasi = request.form.get('presentasi')

            print("testing")

            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("select * from nilai_penguji where nik = ? and id_sidang = ?", (nik, session['id_sidang'],))
            if(cursor.fetchone() == None):
                cursor.execute("insert into nilai_penguji (tata_tulis, kelengkapan_materi, pencapaian_tujuan, penguasaan_materi, presentasi, nik, id_sidang) values (?, ?, ?, ?, ?, ?, ?)", (tata_tulis, kelengkapan_materi, pencapaian_tujuan, penguasaan_materi, presentasi, nik, session['id_sidang']))
                conn.commit()
                session.pop('id_sidang', None)
            else:
                cursor.execute("UPDATE nilai_penguji SET tata_tulis = ?, kelengkapan_materi = ?, pencapaian_tujuan = ?, penguasaan_materi = ?, presentasi = ? WHERE nik = ? and ID_Sidang = ?", (tata_tulis, kelengkapan_materi, pencapaian_tujuan, penguasaan_materi, presentasi, nik, session['id_sidang']))
                conn.commit()
            cursor.execute("select * from InfoPengujiView where nik_penguji = ?", (nik,))
            info = cursor.fetchall()
            return render_template('penguji/penguji-inputnilai.html', nama = nama, info=info)