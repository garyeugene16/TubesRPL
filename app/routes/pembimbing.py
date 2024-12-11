from flask import Blueprint, jsonify, render_template,session, url_for, redirect, request
import sqlite3

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

# @pembimbing_bp.route('/info')
# def info():
#     nama = session.get('nama', None)
#     role = session.get('role', None)
#     return render_template('pembimbing/pembimbing-info.html', nama = nama)
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

@pembimbing_bp.route('/bap')
def bap():
    nama = session.get('nama', None)
    role = session.get('role', None)
    return render_template('pembimbing/pembimbing-bap.html', nama = nama)
        
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


# @pembimbing_bp.route('/nilai')
# def nilai():
#     nama = session.get('nama', None)
#     role = session.get('role', None)
#     return render_template('pembimbing/pembimbing-inputnilai.html', nama = nama)