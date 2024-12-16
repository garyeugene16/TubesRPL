import os
from flask import Blueprint, Flask, jsonify, render_template, send_from_directory, session, redirect, url_for, request
import sqlite3
from werkzeug.utils import secure_filename

app = Flask(__name__)
mahasiswa_bp = Blueprint('mahasiswa', __name__)

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
    
    bobots = conn.execute('SELECT * FROM Bobot_PerTahun_Ajaran').fetchall()

    
    # # Ambil informasi sidang
    # sidang_info = conn.execute('''
    #     SELECT s.ID_Sidang, s.tempat_sidang, s.tanggal_sidang, s.waktu_mulai, s.waktu_selesai, s.catatan
    #     FROM InfoSidang s
    #     WHERE s.npm_mahasiswa = ? AND s.status = ?
    # ''', (npm, 'active')).fetchone()
    
    
    sidang_info = conn.execute('''
        SELECT s.ID_Sidang, s.tempat_sidang, s.tanggal_sidang, s.waktu_mulai, s.waktu_selesai, s.catatan
        FROM Sidang s
        WHERE s.npm = ?
        LIMIT 1
    ''', (npm,)).fetchone()


    tahun_ajaran = request.args.get('tahun_ajaran', None)
    print(tahun_ajaran)
    if tahun_ajaran:
        # Filter berdasarkan tahun ajaran jika dipilih
        # Ambil informasi sidang
        sidang_info = conn.execute('''
            SELECT s.ID_Sidang, s.tempat_sidang, s.tanggal_sidang, s.waktu_mulai, s.waktu_selesai, s.catatan
            FROM Sidang s
            WHERE s.ID_Tahun_Ajaran = ? AND s.npm = ?
        ''', (tahun_ajaran, npm)).fetchone()
        
    print(sidang_info)
        
    # Query gabungan untuk menghitung nilai total sidang berdasarkan bobot
    # Query gabungan untuk menghitung nilai total sidang berdasarkan bobot
    nilai_detail_query = '''
        SELECT 
            np1.tata_tulis AS nilai_tata_tulis_penguji1,
            np1.kelengkapan_materi AS nilai_kelengkapan_materi_penguji1,
            np1.pencapaian_tujuan AS nilai_pencapaian_tujuan_penguji1,
            np1.penguasaan_materi AS nilai_penguasaan_materi_penguji1,
            np1.presentasi AS nilai_presentasi_penguji1,
            np2.tata_tulis AS nilai_tata_tulis_penguji2,
            np2.kelengkapan_materi AS nilai_kelengkapan_materi_penguji2,
            np2.pencapaian_tujuan AS nilai_pencapaian_tujuan_penguji2,
            np2.penguasaan_materi AS nilai_penguasaan_materi_penguji2,
            np2.presentasi AS nilai_presentasi_penguji2,
            (np1.tata_tulis + np2.tata_tulis) / 2 AS nilai_tata_tulis_penguji,
            (np1.kelengkapan_materi + np2.kelengkapan_materi) / 2 AS nilai_kelengkapan_materi_penguji,
            (np1.pencapaian_tujuan + np2.pencapaian_tujuan) / 2 AS nilai_pencapaian_tujuan_penguji,
            (np1.penguasaan_materi + np2.penguasaan_materi) / 2 AS nilai_penguasaan_materi_penguji,
            (np1.presentasi + np2.presentasi) / 2 AS nilai_presentasi_penguji,
            nb.tata_tulis AS nilai_tata_tulis_pembimbing,
            nb.kelengkapan_materi AS nilai_kelengkapan_materi_pembimbing,
            nb.proses_bimbingan AS nilai_proses_bimbingan_pembimbing,
            nb.penguasaan_materi AS nilai_penguasaan_materi_pembimbing,
            nk.nilai AS nilai_koordinator,
            (
                (((np1.tata_tulis + np2.tata_tulis) / 2) * b.tata_tulis_penguji +
                ((np1.kelengkapan_materi + np2.kelengkapan_materi) / 2) * b.kelengkapan_materi_penguji +
                ((np1.pencapaian_tujuan + np2.pencapaian_tujuan) / 2) * b.pencapaian_tujuan_penguji +
                ((np1.penguasaan_materi + np2.penguasaan_materi) / 2) * b.penguasaan_materi_penguji +
                ((np1.presentasi + np2.presentasi) / 2) * b.presentasi_penguji) * b.bobot_penguji
            ) +
            ((nb.tata_tulis * b.tata_tulis_pembimbing +
            nb.kelengkapan_materi * b.kelengkapan_materi_pembimbing +
            nb.proses_bimbingan * b.proses_bimbingan_pembimbing +
            nb.penguasaan_materi * b.penguasaan_materi_pembimbing) * b.bobot_pembimbing) +
            (nk.nilai * b.bobot_koordinator) AS total_nilai
        FROM Sidang s
        JOIN Nilai_Penguji np1 ON np1.ID_Sidang = s.ID_Sidang
        JOIN Nilai_Penguji np2 ON np2.ID_Sidang = s.ID_Sidang
        JOIN Nilai_Pembimbing nb ON nb.ID_Sidang = s.ID_Sidang
        JOIN Nilai_Koordinator nk ON nk.id_sidang = s.ID_Sidang
        JOIN Bobot_PerTahun_Ajaran b ON s.ID_Tahun_Ajaran = b.ID_Tahun_Ajaran
        WHERE s.npm = ?
    '''

    # Jika tahun_ajaran diberikan, tambahkan kondisi filter untuk tahun_ajaran
    if tahun_ajaran:
        nilai_detail_query += ' AND s.ID_Tahun_Ajaran = ?'

    # Menjalankan query dengan parameter
    nilai_detail = conn.execute(nilai_detail_query, (npm, tahun_ajaran) if tahun_ajaran else (npm,)).fetchone()
    conn.close()
    print(nilai_detail)
    
    if not sidang_info or not nilai_detail:
        return f"Tidak ada data nilai sidang untuk mahasiswa dengan NPM '{npm}'", 404
    
    # Format data menjadi dictionary
    sidang_dict = dict(sidang_info) if sidang_info else {}
    nilai_dict = dict(nilai_detail) if nilai_detail else {}

    # Cek apakah pengguna meminta JSON
    if request.args.get('format') == 'json':
        return jsonify({
            'sidang': sidang_dict,
            'nilai_detail': nilai_dict
        })

    # Jika tidak, render template HTML
    return render_template(
        'mahasiswa/mahasiswa-nilai.html', 
        nama=nama, 
        sidang=sidang_info, 
        nilai_detail=nilai_detail,
        bobots=bobots
    )

    
    # return render_template('mahasiswa/mahasiswa-nilai.html', nama = nama, sidang=sidang_info, nilai_detail=nilai_detail)


@mahasiswa_bp.route('/bap', methods=['GET'])
def bap():
    nama = session.get('nama', None)
    npm = session.get('id', None)
    conn = get_db_connection()

    # Ambil data BAP terkait dengan mahasiswa berdasarkan npm (melalui sidang yang terkait)
    cursor = conn.cursor()
    cursor.execute('''
        SELECT * FROM BAP
        WHERE idSidang IN (SELECT ID_Sidang FROM Sidang WHERE npm = ? and status = ?)
    ''', (npm, 'active'))
    bap_data = cursor.fetchone()
    print(bap_data)
    conn.close()
    
    # Jika BAP ditemukan, tampilkan data, jika tidak, beri notifikasi
    if not bap_data:
        return "BAP belum tersedia", 404

    return render_template('mahasiswa/mahasiswa-bap.html', nama=nama, bap_data=bap_data)


@mahasiswa_bp.route('/bap/unduh', methods=['POST'])
def unduh_bap():
    npm = session.get('id', None)
    if not npm:
        return "Anda tidak memiliki akses", 403

    conn = get_db_connection()

    # Ambil file_path BAP berdasarkan npm (melalui sidang yang terkait)
    cursor = conn.cursor()
    cursor.execute('''
        SELECT file_path FROM BAP
        WHERE idSidang IN (SELECT ID_Sidang FROM Sidang WHERE npm = ? and status = ?)
    ''', (npm, 'active'))
    bap_data = cursor.fetchone()

    conn.close()

    # Jika BAP ditemukan, unduh file
    if bap_data and bap_data['file_path']:
        file_path = bap_data['file_path']

        # Pastikan file_path valid
        if not os.path.isfile(file_path):
            return "File tidak ditemukan di server", 404

        # Ekstrak direktori dan nama file
        directory = os.path.dirname(file_path)
        filename = os.path.basename(file_path)

        # Kirim file ke pengguna
        return send_from_directory(directory=directory, path=filename, as_attachment=True)

    return "BAP tidak ditemukan", 404



@mahasiswa_bp.route('/bap/uploads', methods=['GET','POST'])
def upload_bap():
    npm = session.get('id', None)
    file = request.files.get('bap_file')

    if not file:
        return "Tidak ada file yang diunggah", 400

    # Cek apakah ekstensi file diizinkan
    if not allowed_file(file.filename):
        return "Ekstensi file tidak diizinkan", 400
    
     # Ambil ID sidang berdasarkan NPM mahasiswa
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT ID_Sidang FROM Sidang WHERE npm = ? AND status = ?
    ''', (npm, 'active'))
    sidang_info = cursor.fetchone()
    conn.close()

    # Tentukan nama file dan simpan di server
    id_sidang = sidang_info['ID_Sidang']
    filename = generate_filename(id_sidang)
    file_path = os.path.join(UPLOAD_FOLDER, filename)
    file.save(file_path)
    print(id_sidang)

    conn = get_db_connection()
    cursor = conn.cursor()

    # Cek status tanda tangan pembimbing
    cursor.execute('''
        SELECT status_pembimbing FROM BAP WHERE idSidang = ?
    ''', (id_sidang,))
    status_pembimbing = cursor.fetchone()

    if status_pembimbing and status_pembimbing['status_pembimbing'] == 'sudah':
        # Jika pembimbing sudah menandatangani, update status mahasiswa
        cursor.execute('''
            UPDATE BAP 
            SET file_path = ?, status_mahasiswa = 'sudah'
            WHERE idSidang = ?
        ''', (file_path, id_sidang))

        cursor.execute('''
            UPDATE Sidang 
            SET status = 'selesai'
            WHERE idSidang = ?
        ''', (id_sidang,))
    else:
        # Jika pembimbing belum menandatangani, beri pesan error
        return "BAP belum ditandatangani oleh pembimbing", 400

    conn.commit()
    conn.close()

    return redirect(url_for('mahasiswa.bap'))  # Arahkan kembali ke halaman BAP
