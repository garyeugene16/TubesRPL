from flask import Blueprint, render_template, session, redirect, url_for, request, jsonify, Flask, send_from_directory
import sqlite3
import os

penguji_bp = Blueprint('penguji', __name__)
app = Flask(__name__)

UPLOAD_FOLDER = os.path.join('uploads', 'bap')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
ALLOWED_EXTENSIONS = {'pdf'}
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Fungsi untuk membuat penamaan file tetap sama
def generate_filename(id_sidang):
    return f'bap_sidang_{id_sidang}.pdf'

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
    cursor.execute("select * from InfoSidang where nik_penguji = ? OR nik_penguji2 = ?", (id, id,))
    info = cursor.fetchall()
    return render_template('penguji/penguji-info.html', nama = nama, info=info)

@penguji_bp.route('/bap', methods=['GET', 'POST'])
def bap():
    nama = session.get('nama', None)
    nik = session.get('id', None)
    if(request.method == 'GET'):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("select * from InfoSidang where nik_penguji = ? or nik_penguji2 = ?", (nik, nik,))
        info = cursor.fetchall()
        return render_template('penguji/penguji-bap.html', nama = nama, info=info)
    else:
        if(request.is_json):
            data = request.get_json()
            print(data)
            npm = data['npm']
            id_sidang = data['id_sidang']
            print("nik kamu adalah " + nik)
            print("id sidangnya adalah " + id_sidang)
            return jsonify("true")


@penguji_bp.route('/nilai', methods=['GET', 'POST'])
def nilai():
    nik = session.get('id', None)
    nama = session.get('nama', None)
    if(request.method == 'GET'):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("select * from InfoSidang where nik_penguji = ? or nik_penguji2 = ?", (nik, nik,))
        info = cursor.fetchall()
        return render_template('penguji/penguji-inputnilai.html', nama = nama, info=info)
    else:
        if(request.is_json):
            data = request.get_json()
            print(data)
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
            cursor.execute("UPDATE nilai_penguji SET tata_tulis = ?, kelengkapan_materi = ?, pencapaian_tujuan = ?, penguasaan_materi = ?, presentasi = ? WHERE nik = ? and ID_Sidang = ?", (tata_tulis, kelengkapan_materi, pencapaian_tujuan, penguasaan_materi, presentasi, nik, session['id_sidang']))
            conn.commit()
            cursor.execute("select * from InfoSidang where nik_penguji = ?", (nik,))
            info = cursor.fetchall()
            return render_template('penguji/penguji-inputnilai.html', nama = nama, info=info)
        
@penguji_bp.route('/bap/unduh', methods=['POST'])
def unduh_bap():
    npm = request.form.get('npm_hidden')
    if not npm:
        return "Anda tidak memiliki akses", 403

    conn = get_db_connection()

    cursor = conn.cursor()
    cursor.execute('''
        SELECT file_path FROM BAP
        WHERE idSidang IN (SELECT ID_Sidang FROM Sidang WHERE npm = ? and status = ?)
    ''', (npm, 'active'))
    bap_data = cursor.fetchone()

    conn.close()

    if bap_data and bap_data['file_path']:
        file_path = bap_data['file_path']

        if not os.path.isfile(file_path):
            return "File tidak ditemukan di server", 404

        directory = os.path.dirname(file_path)
        filename = os.path.basename(file_path)

        return send_from_directory(directory=directory, path=filename, as_attachment=True)

    return "BAP tidak ditemukan", 404



@penguji_bp.route('/bap/uploads', methods=['GET','POST'])
def upload_bap():
    nik = session.get('id', None)
    npm = request.form.get('npm_hidden')
    file = request.files.get('bap_file')

    if not file:
        return "Tidak ada file yang diunggah", 400

    if not allowed_file(file.filename):
        return "Ekstensi file tidak diizinkan", 400
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT ID_Sidang FROM Sidang WHERE npm = ? AND status = ?
    ''', (npm, 'active'))
    sidang_info = cursor.fetchone()
    conn.close()

    id_sidang = sidang_info[0]
    filename = generate_filename(id_sidang)
    file_path = os.path.join(UPLOAD_FOLDER, filename)
    file.save(file_path)
    print(id_sidang)

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('''
        SELECT status_koordinator FROM BAP WHERE idSidang = ?
    ''', (id_sidang,))
    status_koordinator = cursor.fetchone()

    if status_koordinator and status_koordinator['status_koordinator'] == 'sudah':
        cursor.execute('''
            SELECT *  
            FROM Sidang
            WHERE ID_Sidang = ?
        ''', (id_sidang,))
        sidang = cursor.fetchone()

        if(nik == sidang['nik_penguji']):
            cursor.execute('''
                UPDATE BAP  
                SET status_penguji1 = 'sudah'
                WHERE idSidang = ?
            ''', (id_sidang,))
            sidang = cursor.fetchone()
        
        elif(nik == sidang['nik_penguji2']):
            cursor.execute('''
                UPDATE BAP  
                SET status_penguji2 = 'sudah'
                WHERE idSidang = ?
            ''', (id_sidang,))
            sidang = cursor.fetchone()

        cursor.execute('''
            UPDATE BAP 
            SET file_path = ?, status_mahasiswa = 'sudah'
            WHERE idSidang = ?
        ''', (file_path, id_sidang))

    else:
        return "BAP belum ditandatangani oleh koordinator", 400

    conn.commit()
    conn.close()

    return redirect(url_for('penguji.bap'))