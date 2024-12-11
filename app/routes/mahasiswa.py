from flask import Blueprint, render_template, session, redirect, url_for, request
import sqlite3

mahasiswa_bp = Blueprint('mahasiswa', __name__)


def get_db_connection():
    conn = sqlite3.connect('database/database.db') 
    conn.row_factory = sqlite3.Row 
    return conn

@mahasiswa_bp.before_request
def require_login():
    allowed_routes = ['login', 'static']
    if 'email' not in session and request.endpoint not in allowed_routes:
        return redirect(url_for('login'))
    
@mahasiswa_bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@mahasiswa_bp.route('/')
def dashboard():
    return redirect(url_for('home'))

@mahasiswa_bp.route('/home')
def home():
    nama = session.get('nama', None)
    role = session.get('role', None)
    return render_template('mahasiswa/mahasiswa-home.html', nama = nama, role=role)

@mahasiswa_bp.route('/info')
def info():
    nama = session.get('nama', None)
    npm = session.get('id', None)
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("select * from InfoSidang where npm_mahasiswa = ? and status = ?", (npm, 'active'))
    info_sidang = cursor.fetchone()
    print(info_sidang)
    return render_template('mahasiswa/mahasiswa-info.html', nama = nama, info = info_sidang)

@mahasiswa_bp.route('/bap')
def bap():
    nama = session.get('nama', None)
    role = session.get('role', None)
    npm = session.get('id', None)
    return render_template('mahasiswa/mahasiswa-bap.html', nama = nama)

@mahasiswa_bp.route('/catatan')
def catatan():
    nama = session.get('nama', None)
    role = session.get('role', None)
    npm = session.get('id', None)
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("select catatan from InfoSidang where npm_mahasiswa = ? and status = ?", (npm, 'active'))
    catatan = cursor.fetchall()
    return render_template('mahasiswa/mahasiswa-catatan.html', nama = nama, catatan=catatan)

@mahasiswa_bp.route('/nilai')
def nilai():
    conn = get_db_connection()  
    npm = session['id']
    print("npm kamu adalah: " + npm)
    nama = session.get('nama', None)
    role = session.get('role', None)
    # Ambil informasi sidang
    sidang_info = conn.execute('''
        SELECT s.ID_Sidang, s.tempat_sidang, s.tanggal_sidang, s.waktu_mulai, s.waktu_selesai, s.catatan
        FROM Sidang s
        WHERE s.npm = ?
    ''', (npm,)).fetchone()

    # Query gabungan untuk menghitung nilai total sidang berdasarkan bobot
    nilai_detail = conn.execute('''
        SELECT 
            np.tata_tulis AS nilai_tata_tulis_penguji,
            np.kelengkapan_materi AS nilai_kelengkapan_materi_penguji,
            np.pencapaian_tujuan AS nilai_pencapaian_tujuan_penguji,
            np.penguasaan_materi AS nilai_penguasaan_materi_penguji,
            np.presentasi AS nilai_presentasi_penguji,
            nb.tata_tulis AS nilai_tata_tulis_pembimbing,
            nb.kelengkapan_materi AS nilai_kelengkapan_materi_pembimbing,
            nb.proses_bimbingan AS nilai_proses_bimbingan_pembimbing,
            nb.penguasaan_materi AS nilai_penguasaan_materi_pembimbing,
            (((np.tata_tulis * b.tata_tulis_penguji +
             np.kelengkapan_materi * b.kelengkapan_materi_penguji +
             np.pencapaian_tujuan * b.pencapaian_tujuan_penguji +
             np.penguasaan_materi * b.penguasaan_materi_penguji +
             np.presentasi * b.presentasi_penguji)*b.bobot_penguji) +
             ((nb.tata_tulis * b.tata_tulis_pembimbing +
             nb.kelengkapan_materi * b.kelengkapan_materi_pembimbing +
             nb.proses_bimbingan * b.proses_bimbingan_pembimbing +
             nb.penguasaan_materi * b.penguasaan_materi_pembimbing)*b.bobot_pembimbing)) AS total_nilai
        FROM Sidang s
        JOIN Nilai_Penguji np ON np.ID_Sidang = s.ID_Sidang
        JOIN Nilai_Pembimbing nb ON nb.ID_Sidang = s.ID_Sidang
        JOIN Bobot_PerTahun_Ajaran b ON s.ID_Tahun_Ajaran = b.ID_Tahun_Ajaran
        WHERE s.npm = ?
    ''', (npm,)).fetchone()
    conn.close()

    # print(sidang_info)
    # if not sidang_info or not nilai_detail:
    #     return f"Tidak ada data nilai sidang untuk mahasiswa dengan NPM '{npm}'", 404
    
    return render_template('mahasiswa/mahasiswa-nilai.html', nama = nama, sidang=sidang_info, nilai_detail=nilai_detail)
