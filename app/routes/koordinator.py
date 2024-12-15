from flask import Blueprint, render_template, session, redirect, url_for, request, jsonify
import sqlite3
from flask import Blueprint, jsonify, render_template,session, url_for, redirect, request, flash
import sqlite3
import os
from flask import Blueprint, Flask, render_template, send_from_directory, session, redirect, url_for, request
import sqlite3
from werkzeug.utils import secure_filename

UPLOAD_FOLDER = 'uploads/bap'
ALLOWED_EXTENSIONS = {'pdf'}

koordinator_bp = Blueprint('koordinator', __name__)

def get_db_connection():
    conn = sqlite3.connect('database/database.db') 
    conn.row_factory = sqlite3.Row 
    return conn

@koordinator_bp.before_request
def require_login():
    allowed_routes = ['login', 'static']
    if 'email' not in session and request.endpoint not in allowed_routes:
        return redirect(url_for('login'))

@koordinator_bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@koordinator_bp.route('/')
def dashboard():
    return redirect(url_for('home'))

@koordinator_bp.route('/home')
def home():
    nama = session.get('nama', None)
    role = session.get('role', None)
    return render_template('koordinator/koordinator-home.html', nama = nama, role=role)

@koordinator_bp.route('/info', methods=['GET', 'POST'])
def info():
    nama = session.get('nama', None)
    if(request.method == 'GET'):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("select * from InfoSidang")
        info = cursor.fetchall()

        cursor.execute("select * from Penguji")
        penguji = cursor.fetchall()

        cursor.execute("select * from Pembimbing")
        pembimbing = cursor.fetchall()

        cursor.execute("select npm, nama from Mahasiswa")  # Fetch mahasiswa data
        mahasiswa_list = cursor.fetchall()
        print('fdafa')
        conn.close()
        return render_template('koordinator/koordinator-info.html', nama=nama, info=info, penguji=penguji, pembimbing=pembimbing, mahasiswa_list=mahasiswa_list) 
   
    else:
        if request.is_json:
            data = request.get_json()
            npm = data.get('npm')
            id_sidang = data.get('id_sidang')
            session['id_sidang'] = id_sidang
            print('npm nya adalah: ' + npm)
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM InfoSidang WHERE npm_mahasiswa = ? and status = ?", (npm, 'active',))
            sidang_details = cursor.fetchall()
            conn.close()
            if sidang_details:
                return jsonify([dict(row) for row in sidang_details])
            else:
                return jsonify([])

        else:
            id_sidang = session.get('id_sidang', None)
            judul_ta = request.form.get('judul_ta')
            nik_penguji1 = request.form.get('penguji1')
            nik_penguji2 = request.form.get('penguji2')
            nik_pembimbing = request.form.get('pembimbing1')
            jenis_ta = request.form.get('jenis_ta')
            print(id_sidang)
            print(judul_ta)
            print(nik_penguji1)
            print(nik_penguji2)
            print(nik_pembimbing)
            print(jenis_ta)

            conn = get_db_connection()
            cursor = conn.cursor()
            
            
            cursor.execute("""
                UPDATE Mahasiswa
                SET judul_ta = ?, jenis_ta = ?
                WHERE npm IN (SELECT npm FROM Sidang WHERE ID_Sidang = ?)
            """, (judul_ta, jenis_ta, id_sidang))
            conn.commit()
            
            cursor.execute("""
                UPDATE Sidang
                SET 
                    nik_penguji = ?,
                    nik_penguji2 = ?,
                    nik_pembimbing = ?,
                WHERE ID_Sidang = ?
            """, (nik_penguji1, nik_penguji2, nik_pembimbing,id_sidang))
            conn.commit()
            
            cursor = conn.cursor()
            cursor.execute("select * from InfoSidang")
            info = cursor.fetchall()
            
            cursor.execute("select * from Penguji")
            penguji = cursor.fetchall()

            cursor.execute("select * from Pembimbing")
            pembimbing = cursor.fetchall()
            conn.close()
            return render_template('koordinator/koordinator-info.html', nama = nama, info=info, penguji=penguji, pembimbing=pembimbing, success = 'true')



@koordinator_bp.route('/tambah_sidang', methods=['POST'])
def tambah_sidang():
    try:
        npm_mahasiswa = request.form.get('mahasiswa')
        judul_ta = request.form.get('judul')
        nik_penguji1 = request.form.get('penguji1')
        nik_penguji2 = request.form.get('penguji2')
        nik_pembimbing = request.form.get('pembimbing')
        jenis_ta = request.form.get('jenis')
        tempat_sidang = request.form.get('tempat')
        tanggal_sidang = request.form.get('tanggal')
        waktu_mulai = request.form.get('waktu_mulai')
        waktu_selesai = request.form.get('waktu_selesai')
        id_tahun_ajaran = request.form.get('id_tahun_ajaran')
        nilai_total = request.form.get('nilai_total')

        conn = get_db_connection()
        cursor = conn.cursor()
        
        print("npm_mahasiswa:", npm_mahasiswa)
        print("judul_ta:", judul_ta)
        print("nik_penguji1:", nik_penguji1)
        print("nik_penguji2:", nik_penguji2)
        print("nik_pembimbing:", nik_pembimbing)
        print("jenis_ta:", jenis_ta)
        print("tempat_sidang:", tempat_sidang)
        print("tanggal_sidang:", tanggal_sidang)
        print("waktu_mulai:", waktu_mulai)
        print("waktu_selesai:", waktu_selesai)
        cursor.execute("""
            INSERT INTO Sidang (npm, nik_penguji, nik_penguji2, nik_pembimbing, tempat_sidang, tanggal_sidang, waktu_mulai, waktu_selesai, ID_Tahun_Ajaran, nilai_total, status) 
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'active')
        """, (npm_mahasiswa, nik_penguji1, nik_penguji2, nik_pembimbing, tempat_sidang, tanggal_sidang, waktu_mulai, waktu_selesai, id_tahun_ajaran, nilai_total))
        conn.commit()

        cursor.execute("""
            UPDATE Mahasiswa
            SET judul_ta = ?, jenis_ta = ?
            WHERE npm = ?
        """, (judul_ta, jenis_ta, npm_mahasiswa))
        conn.commit()

        conn.close()

        return redirect(url_for('koordinator.info')) 

    except Exception as e:
        print(f"Error adding sidang: {e}")
        return "An error occurred", 500


@koordinator_bp.route('/pengaturan_waktu_dan_lokasi', methods=['GET', 'POST'])
def pengaturan_waktu_dan_lokasi():
    nama = session.get('nama', None)
    if request.method == 'GET':
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM InfoSidang")
        info = cursor.fetchall()
        return render_template('koordinator/koordinator-atur.html', nama=nama, info=info)
    else:
        if(request.is_json):
            data = request.get_json()
            id_sidang = data.get('id_sidang')
            session['id_sidang'] = id_sidang
            return jsonify('true')
        
        else:
            tanggal = request.form.get('tanggal')
            mulai = request.form.get('mulai')
            selesai = request.form.get('selesai')
            tempat = request.form.get('tempat')
            id_sidang = session.get('id_sidang', None)


            print(id_sidang)
            print(tanggal)
            print(mulai)
            print(selesai)
            print(tempat)


            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM Sidang WHERE ID_Sidang = ? ", (id_sidang,))
            sidang = cursor.fetchone()
            conn.close()
            if(sidang is None):
                conn = get_db_connection()
                cursor = conn.cursor()
                cursor.execute("INSERT INTO Sidang (tanggal_sidang, waktu_mulai, waktu_selesai, tempat_sidang) VALUES (?, ?, ?, ?)", (tanggal, mulai, selesai, tempat,))
                conn.commit()
                conn.close()
            else:
                conn = get_db_connection()
                cursor = conn.cursor()
                cursor.execute("update sidang Set tanggal_sidang = ?, waktu_mulai = ?, waktu_selesai = ?, tempat_sidang = ? WHERE ID_Sidang = ?", (tanggal, mulai, selesai, tempat, id_sidang))
                conn.commit()
                conn.close()

            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM InfoSidang")
            session.pop('id_sidang')
            info = cursor.fetchall()
            return render_template('koordinator/koordinator-atur.html', nama=nama, info=info)
        
@koordinator_bp.route('/pengaturan_nilai', methods = ['GET', 'POST'])
def pengaturan_nilai():
    nama = session.get('nama', None)
    nik = session.get('id', None)
    if(request.method == 'GET'):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM InfoSidang")
        info = cursor.fetchall()
        cursor.execute("SELECT * FROM nilai_koordinator")
        nilais = cursor.fetchall()
        id_sidang_in_nilai = [nilai["id_sidang"] for nilai in nilais]
        cursor.execute("SELECT * FROM bobot_pertahun_ajaran")
        all_bobot = cursor.fetchall()
        cursor.execute("SELECT * FROM bobot_pertahun_ajaran where id_tahun_ajaran IN (SELECT id_tahun_ajaran FROM Sidang WHERE status = 'active')")
        bobots = cursor.fetchall()


        print(bobots)
        bobot = [
                {
                    "id_tahun_ajaran": row["ID_Tahun_Ajaran"],  # Mengakses dengan nama kolom (pastikan nama cocok)
                    "bobot_penguji": row["bobot_penguji"] * 100,
                    "bobot_koordinator": row["bobot_koordinator"] * 100,
                    "tata_tulis_penguji": row["tata_tulis_penguji"] * 100,
                    "kelengkapan_materi_penguji": row["kelengkapan_materi_penguji"] * 100,
                    "pencapaian_tujuan_penguji": row["pencapaian_tujuan_penguji"] * 100,
                    "penguasaan_materi_penguji": row["penguasaan_materi_penguji"] * 100,
                    "presentasi_penguji": row["presentasi_penguji"] * 100,
                    "bobot_pembimbing": row["bobot_pembimbing"] * 100,
                    "tata_tulis_pembimbing": row["tata_tulis_pembimbing"] * 100,
                    "kelengkapan_materi_pembimbing": row["kelengkapan_materi_pembimbing"] * 100,
                    "proses_bimbingan_pembimbing": row["proses_bimbingan_pembimbing"] * 100,
                    "penguasaan_materi_pembimbing": row["penguasaan_materi_pembimbing"] * 100
                }
                for row in bobots
            ]
        return render_template('koordinator/koordinator-pengaturan.html', nama = nama, info=info, nilai=nilais, id_sidang_in_nilai=id_sidang_in_nilai, nik=nik, bobot=bobot, bobots = all_bobot)
    else:
        if(request.is_json):
            data = request.get_json()
            id_tahun = data.get('id_tahun')

            nik = data.get('nik')
            id_sidang = data.get('id_sidang')
            print(nik)
            print(id_sidang)
            print(id_tahun)
            if(id_tahun != None):
                conn = get_db_connection()
                cursor = conn.cursor()
                cursor.execute("select * from bobot_pertahun_ajaran where ID_Tahun_Ajaran = ?", (id_tahun,))
                info = cursor.fetchall()
                return jsonify([dict(row) for row in info])
            if(id_sidang != None):
                session['id_sidang'] = id_sidang
                return jsonify('berhasil mengirim nik dan id_sidang')
        else:
            id_tahun = request.form.get('tahun-ajaran')
            koor = request.form.get('koordinator')
            penguji = request.form.get('penguji')
            pembimbing = request.form.get('pembimbing')
            print(id_tahun)
            print(koor)
            print(penguji)
            print(pembimbing)

            ttu = request.form.get('ttu')
            kmu = request.form.get('kmu')
            ptu = request.form.get('ptu')
            pmu = request.form.get('pmu')
            pu = request.form.get('pu')

            ttb = request.form.get('ttb')
            kmb = request.form.get('kmb')
            pbb = request.form.get('pbb')
            pmb = request.form.get('pmb')

            nilai_koor = request.form.get('nilai')

            if(id_tahun != None):
                print("id_tahun berhasil")
                id_tahun = int(id_tahun)
                koor = float(koor)/100
                penguji = float(penguji)/100
                pembimbing = float(pembimbing)/100       
                if(id_tahun == 0):
                    print('halo')
                    conn = get_db_connection()
                    cursor = conn.cursor()
                    cursor.execute("insert into bobot_pertahun_ajaran (bobot_koordinator, bobot_penguji, bobot_pembimbing, tata_tulis_penguji, kelengkapan_materi_penguji, pencapaian_tujuan_penguji, penguasaan_materi_penguji, presentasi_penguji, tata_tulis_pembimbing, kelengkapan_materi_pembimbing, proses_bimbingan_pembimbing, penguasaan_materi_pembimbing) values (?, ?, ?, 0, 0, 0, 0, 0, 0, 0, 0, 0)", (koor, penguji, pembimbing,))
                    conn.commit()
                    conn.close()
                    print('sucess')
                    conn = get_db_connection()
                    cursor = conn.cursor()
                    cursor.execute("select MAX(id_tahun_ajaran) as max_id from bobot_pertahun_ajaran")
                    id_tahun_ajaran = cursor.fetchone()
                    conn.close()
                    print(id_tahun_ajaran[0])
                    conn = get_db_connection()
                    cursor = conn.cursor()
                    cursor.execute("update sidang set id_tahun_ajaran = ? where sidang.status = 'active'", (id_tahun_ajaran[0],))
                    conn.commit()
                    conn.close()
                else:
                    print('update')
                    conn = get_db_connection()
                    cursor = conn.cursor()
                    cursor.execute("update sidang set id_tahun_ajaran = ? where sidang.status = 'active'", (id_tahun,))
                    conn.commit()

            if(ttu != None):
                print("ttu berhasil")
                conn = get_db_connection()
                cursor = conn.cursor()
                cursor.execute("select id_tahun_ajaran from sidang where sidang.status = 'active'")
                id_tahuns = cursor.fetchone()

                ttu = float(ttu)/100
                kmu = float(kmu)/100
                ptu = float(ptu)/100
                pmu = float(pmu)/100
                pu = float(pu)/100

                cursor.execute("update bobot_pertahun_ajaran set tata_tulis_penguji = ?, kelengkapan_materi_penguji = ?, pencapaian_tujuan_penguji = ?, penguasaan_materi_penguji = ?, presentasi_penguji = ? where id_tahun_ajaran = ?", (ttu, kmu, ptu, pmu, pu, id_tahuns[0],))
                conn.commit()

            if(ttb != None):
                print("ttb berhasil")
                conn = get_db_connection()
                cursor = conn.cursor()
                cursor.execute("select id_tahun_ajaran from sidang where sidang.status = 'active'")
                id_tahuns = cursor.fetchone()

                ttb = float(ttb)/100
                kmb = float(kmb)/100
                pbb = float(pbb)/100
                pmb = float(pmb)/100

                cursor.execute("update bobot_pertahun_ajaran set tata_tulis_pembimbing = ?, kelengkapan_materi_pembimbing = ?, proses_bimbingan_pembimbing = ?, penguasaan_materi_pembimbing = ? where id_tahun_ajaran = ?", (ttb, kmb, pbb, pmb, id_tahuns[0],))
                conn.commit()

            if(nilai_koor != None):
                print("nilai_koor berhasil")
                id_sidang = session.get('id_sidang', None)
                nik = session.get('id', None)
                session.pop('id_sidang')
                conn = get_db_connection()
                cursor = conn.cursor()
                cursor.execute("select * from nilai_koordinator where id_sidang = ?", (id_sidang,))
                sidang = cursor.fetchone()

                if(sidang == None):
                    cursor.execute("insert into nilai_koordinator (nik_koordinator, id_sidang, nilai) values (?, ?, ?)", (nik, id_sidang, nilai_koor,))
                    conn.commit()
                else:
                    cursor.execute("update nilai_koordinator set nilai = ? where id_sidang = ?", (nilai_koor, id_sidang,))
                    conn.commit()

            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM InfoSidang")
            info = cursor.fetchall()
            cursor.execute("SELECT * FROM nilai_koordinator")
            nilais = cursor.fetchall()
            id_sidang_in_nilai = [nilai["id_sidang"] for nilai in nilais]
            cursor.execute("SELECT * FROM bobot_pertahun_ajaran")
            all_bobot = cursor.fetchall()
            cursor.execute("SELECT * FROM bobot_pertahun_ajaran where id_tahun_ajaran IN (SELECT id_tahun_ajaran FROM Sidang WHERE status = 'active')")
            bobots = cursor.fetchall()
            print(bobots)
            bobot = [
                    {
                        "id_tahun_ajaran": row["ID_Tahun_Ajaran"],  # Mengakses dengan nama kolom (pastikan nama cocok)
                        "bobot_penguji": row["bobot_penguji"] * 100,
                        "bobot_koordinator": row["bobot_koordinator"] * 100,
                        "tata_tulis_penguji": row["tata_tulis_penguji"] * 100,
                        "kelengkapan_materi_penguji": row["kelengkapan_materi_penguji"] * 100,
                        "pencapaian_tujuan_penguji": row["pencapaian_tujuan_penguji"] * 100,
                        "penguasaan_materi_penguji": row["penguasaan_materi_penguji"] * 100,
                        "presentasi_penguji": row["presentasi_penguji"] * 100,
                        "bobot_pembimbing": row["bobot_pembimbing"] * 100,
                        "tata_tulis_pembimbing": row["tata_tulis_pembimbing"] * 100,
                        "kelengkapan_materi_pembimbing": row["kelengkapan_materi_pembimbing"] * 100,
                        "proses_bimbingan_pembimbing": row["proses_bimbingan_pembimbing"] * 100,
                        "penguasaan_materi_pembimbing": row["penguasaan_materi_pembimbing"] * 100
                    }
                    for row in bobots
                ]
            return render_template('koordinator/koordinator-pengaturan.html', nama = nama, info=info, nilai=nilais, id_sidang_in_nilai=id_sidang_in_nilai, nik=nik, bobot=bobot, bobots = all_bobot)  
        
# HANDLE BAP :        
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@koordinator_bp.route('/bap')
def bap():
    nama = session.get('nama', None)
    nik = session.get('id', None)
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM InfoSidang")
    info = cursor.fetchall()
    
    return render_template('koordinator/koordinator-bap.html', nama=nama, info=info)

@koordinator_bp.route('/upload-bap', methods=['POST'])
def upload_bap():
    try:
        id_sidang = request.form.get('id_sidang')
        
        # Cek status penguji di tabel BAP
        conn = get_db_connection()
        cursor = conn.cursor()
        
        if 'bap' not in request.files:
            flash('Tidak ada file yang dipilih')
            return redirect(url_for('koordinator.bap'))
        
        file = request.files['bap']
        
        if file.filename == '':
            flash('Tidak ada file yang dipilih')
            return redirect(url_for('koordinator.bap'))
        
        if file and allowed_file(file.filename):
            if not os.path.exists(UPLOAD_FOLDER):
                os.makedirs(UPLOAD_FOLDER)
            # rename file bap
            filename = f"bap_{id_sidang}.pdf"
            file_path = os.path.join(UPLOAD_FOLDER, filename)
            
            file.save(file_path)
            
            if os.path.exists(file_path) and os.path.getsize(file_path) > 0:
                # Update status pembimbing di tabel BAP
                cursor.execute("""
                    UPDATE BAP 
                    SET file_path = ?, status_koordinator = 'sudah'
                    WHERE idSidang = ?
                """, (file_path, id_sidang))
                conn.commit()
                flash('File berhasil diupload')
            else:
                flash('Gagal menyimpan file')
                
        return redirect(url_for('koordinator.bap'))
    
    except Exception as e:
        print(f"Error: {str(e)}")
        flash('Terjadi kesalahan saat upload file')
        return redirect(url_for('koordinator.bap'))
    finally:
        if conn:
            conn.close()

@koordinator_bp.route('/get-bap/<id_sidang>')
def get_bap(id_sidang):
    conn = get_db_connection()
    cursor = conn.cursor()
    # Ambil File path dari BAP
    cursor.execute("""
        SELECT b.file_path
        FROM BAP b 
        WHERE b.idSidang = ?
    """, (id_sidang,))
    result = cursor.fetchone()
    
    response = {
        'file_path': None,
        'can_upload': True
    }
    
    if result:
        if result['file_path'] and os.path.exists(result['file_path']):
            response['file_path'] = result['file_path']
    
    return jsonify(response)

@koordinator_bp.route('/download-bap/<id_sidang>')
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

@koordinator_bp.route('/view-bap/<id_sidang>')
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

        return "<p>Path BAP tidak ada<p>", 404
        
    except Exception as e:
        print(f"Error viewing BAP: {str(e)}")
        return "Gagal menampilkan BAP", 500