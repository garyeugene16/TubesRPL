from flask import Blueprint, jsonify, render_template,session, url_for, redirect, request, flash
import sqlite3
import os
from flask import Blueprint, Flask, render_template, send_from_directory, session, redirect, url_for, request
import sqlite3
from werkzeug.utils import secure_filename

UPLOAD_FOLDER = 'uploads/bap'
ALLOWED_EXTENSIONS = {'pdf'}

pembimbing_bp = Blueprint('pembimbing', __name__)

def get_db_connection():
    conn = sqlite3.connect('database/database.db') 
    conn.row_factory = sqlite3.Row 
    return conn

@pembimbing_bp.route('/')
def dashboard():
    return redirect(url_for('home'))

@pembimbing_bp.before_request
def require_login():
    allowed_routes = ['login', 'static']
    if 'email' not in session and request.endpoint not in allowed_routes:
        return redirect(url_for('login'))
    
@pembimbing_bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@pembimbing_bp.route('/home')
def home():
    nama = session.get('nama', None)
    role = session.get('role', None)
    return render_template('pembimbing/pembimbing-home.html', nama = nama, role=role)

@pembimbing_bp.route('/info')
def info():
    nama = session.get('nama', None)
    role = session.get('role', None)
    id = session.get('id', None)
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("select * from InfoSidang where nik_pembimbing = ?", (id,))
    info = cursor.fetchall()
    return render_template('pembimbing/pembimbing-info.html', nama = nama, info=info)
        
@pembimbing_bp.route('/nilai', methods=['GET', 'POST'])
def nilai():
    nik = session.get('id', None)
    nama = session.get('nama', None)
    if(request.method == 'GET'):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("select * from InfoSidang where nik_pembimbing = ?", (nik,))
        info = cursor.fetchall()
        return render_template('pembimbing/pembimbing-inputnilai.html', nama = nama, info=info)
    else:
        if(request.is_json):
            data = request.get_json()
            id_sidang = data['id_sidang']
            session['id_sidang'] = id_sidang
            print('id sidang: ' + id_sidang)
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("select * from nilai_pembimbing where nik = ? and ID_Sidang = ?", (nik, id_sidang,))
            rows = cursor.fetchall()
            nilai = [dict(row) for row in rows]
            return jsonify(nilai)
        
        else:
            tata_tulis = request.form.get('tata_tulis')
            kelengkapan_materi = request.form.get('kelengkapan_materi')
            proses_bimbingan = request.form.get('proses_bimbingan')
            penguasaan_materi = request.form.get('penguasaan_materi')

            print("testing")

            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("select * from nilai_pembimbing where nik = ? and id_sidang = ?", (nik, session['id_sidang'],))
            if(cursor.fetchone() == None):
                cursor.execute("insert into nilai_pembimbing (tata_tulis, kelengkapan_materi, proses_bimbingan, penguasaan_materi, nik, id_sidang) values (?, ?, ?, ?, ?, ?)", (tata_tulis, kelengkapan_materi, proses_bimbingan, penguasaan_materi, nik, session['id_sidang']))
                conn.commit()
                session.pop('id_sidang', None)
            else:
                cursor.execute("UPDATE nilai_pembimbing SET tata_tulis = ?, kelengkapan_materi = ?, proses_bimbingan = ?, penguasaan_materi = ? WHERE nik = ? and ID_Sidang = ?", (tata_tulis, kelengkapan_materi, proses_bimbingan, penguasaan_materi, nik, session['id_sidang']))
                conn.commit()
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("select * from InfoSidang where nik_pembimbing = ?", (nik,))
            info = cursor.fetchall()
            return render_template('pembimbing/pembimbing-inputnilai.html', nama = nama,info=info)

@pembimbing_bp.route('/catatan', methods=['GET', 'POST'])
def catatan():
    nik = session.get('id', None)
    nama = session.get('nama', None)
    if(request.method == 'GET'):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("select * from InfoSidang where nik_pembimbing = ?", (nik,))
        info = cursor.fetchall()
        return render_template('pembimbing/pembimbing-catatan.html', nama = nama, info=info)
    else:
        if(request.is_json):
            data = request.get_json()
            id_sidang = data['id_sidang']
            session['id_sidang'] = id_sidang
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("select * from Sidang where ID_Sidang = ?", (id_sidang,))
            rows = cursor.fetchall()
            print(rows)
            catatan = [dict(row) for row in rows]
            return jsonify(catatan)
        
        else:
            catatan = request.form.get('catatan_pembimbing')
            conn = get_db_connection()
            cursor = conn.cursor()

            cursor.execute("UPDATE Sidang SET Catatan = ? WHERE id_sidang = ?",(catatan, session['id_sidang']))
            cursor.execute("select * from InfoSidang where nik_pembimbing = ?", (nik,))
            conn.commit()
            info = cursor.fetchall()
            return render_template('pembimbing/pembimbing-catatan.html', nama = nama, info=info)


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# ambil list mahasiswa
@pembimbing_bp.route('/bap')
def bap():
    print(UPLOAD_FOLDER)
    nama = session.get('nama', None)
    nik = session.get('id', None)
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM InfoSidang WHERE nik_pembimbing = ?", (nik,))
    info = cursor.fetchall()
    
    return render_template('pembimbing/pembimbing-bap.html', nama=nama, info=info)

@pembimbing_bp.route('/upload-bap', methods=['POST'])
def upload_bap():
    try:
        id_sidang = request.form.get('id_sidang')
        
        # Cek status penguji di tabel BAP
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT status_penguji2 FROM BAP WHERE idSidang = ?", (id_sidang,))
        result = cursor.fetchone()
        
        if not result or not result['status_penguji2']:
            flash('Tidak dapat mengupload BAP. Penguji belum menyetujui BAP.')
            return redirect(url_for('pembimbing.bap'))
        
        if 'bap' not in request.files:
            flash('Tidak ada file yang dipilih')
            return redirect(url_for('pembimbing.bap'))
        
        file = request.files['bap']
        
        if file.filename == '':
            flash('Tidak ada file yang dipilih')
            return redirect(url_for('pembimbing.bap'))
        
        if file and allowed_file(file.filename):
            if not os.path.exists(UPLOAD_FOLDER):
                os.makedirs(UPLOAD_FOLDER)
            
            filename = f"bap_{id_sidang}.pdf"
            file_path = os.path.join(UPLOAD_FOLDER, filename)
            
            file.save(file_path)
            
            if os.path.exists(file_path) and os.path.getsize(file_path) > 0:
                # Update status pembimbing di tabel BAP
                cursor.execute("""
                    UPDATE BAP 
                    SET file_path = ?, status_pembimbing = 'sudah'
                    WHERE idSidang = ?
                """, (file_path, id_sidang))
                conn.commit()
                flash('File berhasil diupload')
            else:
                flash('Gagal menyimpan file')
                
        return redirect(url_for('pembimbing.bap'))
    
    except Exception as e:
        print(f"Error: {str(e)}")
        flash('Terjadi kesalahan saat upload file')
        return redirect(url_for('pembimbing.bap'))
    finally:
        if conn:
            conn.close()

@pembimbing_bp.route('/get-bap/<id_sidang>')
def get_bap(id_sidang):
    print('getting bap...')
    conn = get_db_connection()
    cursor = conn.cursor()
    # Mengecek status penguji di tabel BAP
    cursor.execute("""
        SELECT b.file_path, b.status_penguji2 
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
        if (result['status_penguji2']=='sudah'):
            response['can_upload'] = True

    print(response['file_path'])
    print(response['can_upload'])
    return jsonify(response)

@pembimbing_bp.route('/download-bap/<id_sidang>')
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

@pembimbing_bp.route('/view-bap/<id_sidang>')
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