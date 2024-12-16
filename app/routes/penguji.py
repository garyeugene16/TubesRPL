from flask import Blueprint, flash, render_template, session, redirect, url_for, request, jsonify, Flask, send_from_directory
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
        
# ambil list mahasiswa
@penguji_bp.route('/bap')
def bap():
    print(UPLOAD_FOLDER)
    nama = session.get('nama', None)
    nik = session.get('id', None)
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM InfoSidang WHERE nik_penguji = ?", (nik,))
    info = cursor.fetchall()
    
    return render_template('penguji/penguji-bap.html', nama=nama, info=info)

@penguji_bp.route('/upload-bap', methods=['POST'])
def upload_bap():
    try:
        print('uploading...')
        id_sidang = request.form.get('id_sidang')
        
        # Cek status penguji di tabel BAP
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT status_koordinator FROM BAP WHERE idSidang = ?", (id_sidang,))
        result = cursor.fetchone()
        if not result or not result['status_koordinator']:
            print('log : not allowed')
            flash('Tidak dapat mengupload BAP. Koordinator belum menyetujui BAP.')
            return redirect(url_for('penguji.bap'))
        
        if 'bap' not in request.files:
            flash('Tidak ada file yang dipilih')
            return redirect(url_for('penguji.bap'))
        
        file = request.files['bap']
        
        if file.filename == '':
            flash('Tidak ada file yang dipilih')
            return redirect(url_for('penguji.bap'))
        
        if file and allowed_file(file.filename):
            if not os.path.exists(UPLOAD_FOLDER):
                os.makedirs(UPLOAD_FOLDER)
            
            filename = f"bap_{id_sidang}.pdf"
            file_path = os.path.join(UPLOAD_FOLDER, filename)
            print('file saved!')
            file.save(file_path)
            
            if os.path.exists(file_path) and os.path.getsize(file_path) > 0:
                # Update status penguji di tabel BAP
                cursor.execute("""
                    UPDATE BAP 
                    SET file_path = ?, status_penguji = 'sudah'
                    WHERE idSidang = ?
                """, (file_path, id_sidang))
                conn.commit()
                flash('File berhasil diupload')
            else:
                flash('Gagal menyimpan file')
                
        return redirect(url_for('penguji.bap'))
    
    except Exception as e:
        print(f"Error: {str(e)} (exception!) ")
        flash('Terjadi kesalahan saat upload file')
        return redirect(url_for('penguji.bap'))
    finally:
        if conn:
            conn.close()

@penguji_bp.route('/get-bap/<id_sidang>')
def get_bap(id_sidang):
    print('getting bap...')
    conn = get_db_connection()
    cursor = conn.cursor()
    # Mengecek status penguji di tabel BAP
    cursor.execute("""
        SELECT b.file_path, b.status_koordinator
        FROM BAP b 
        WHERE b.idSidang = ?
    """, (id_sidang,))
    result = cursor.fetchone()
    
    response = {
        'file_path': None,
        'can_upload': False
    }
    
    if result:
        if result['file_path'] and os.path.exists(result['file_path']):
            response['file_path'] = result['file_path']
        if (result['status_koordinator']=='sudah'):
            response['can_upload'] = True

    print(response['file_path'])
    print(response['can_upload'])
    return jsonify(response)

@penguji_bp.route('/download-bap/<id_sidang>')
def download_bap(id_sidang):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT file_path FROM BAP WHERE idSidang = ?", (id_sidang,))
        result = cursor.fetchone()
        
        if result and result['file_path'] and os.path.exists(result['file_path']):
            directory = os.path.dirname(result['file_path'])
            filename = os.path.basename(result['file_path'])
            return send_from_directory(
                directory,
                filename,
                as_attachment=True,
                mimetype='application/pdf'
            )
        return "", 404
        
    except Exception as e:
        print(f"Error downloading: {str(e)}")
        return "Gagal mengunduh BAP", 500

@penguji_bp.route('/view-bap/<id_sidang>')
def view_bap(id_sidang):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT file_path FROM BAP WHERE idSidang = ?", (id_sidang,))
        result = cursor.fetchone()
        print(result['file_path'])
        if result and result['file_path'] and os.path.exists(result['file_path']):
            directory = os.path.dirname(result['file_path'])
            filename = os.path.basename(result['file_path'])
            return send_from_directory(
                directory,
                filename,
                mimetype='application/pdf'
            )
        return "<h2>BAP belum di-upload<h2>", 404
        
    except Exception as e:
        print(f"Error viewing BAP: {str(e)}")
        return "Gagal menampilkan BAP", 500