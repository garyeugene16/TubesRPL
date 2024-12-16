-- SQLite
CREATE TABLE BAP (
    id_bap INTEGER PRIMARY KEY AUTOINCREMENT,
    idSidang INTEGER,
    status_koordinator TEXT CHECK(status_koordinator IN ('belum', 'sudah')) DEFAULT 'belum',
    status_penguji1 TEXT CHECK(status_penguji1 IN ('belum', 'sudah')) DEFAULT 'belum',
    status_penguji2 TEXT CHECK(status_penguji2 IN ('belum', 'sudah')) DEFAULT 'belum',
    status_pembimbing TEXT CHECK(status_pembimbing IN ('belum', 'sudah')) DEFAULT 'belum',
    status_mahasiswa TEXT CHECK(status_mahasiswa IN ('belum', 'sudah')) DEFAULT 'belum',
    file_path TEXT, -- lokasi file BAP
    FOREIGN KEY (idSidang) REFERENCES Sidang (ID_Sidang)
);


INSERT INTO BAP (idSidang, status_koordinator, status_penguji1, status_penguji2, status_pembimbing, status_mahasiswa, file_path)
VALUES 
(1, 'sudah', 'sudah', 'sudah', 'sudah', 'sudah', '/Users/garyeugene/Documents/Rekayasa Perangkat Lunak/RPL-MahasiswaFinal/app/routes/uploads/bap/bap_sidang_1.pdf')

INSERT INTO Nilai_Pembimbing (ID_Nilai_Pembimbing, ID_Sidang, tata_tulis, kelengkapan_materi, proses_bimbingan, penguasaan_materi, nik)
VALUES (2, 1, 77, 77, 77, 77, 'P001')

INSERT INTO Nilai_Penguji(ID_Sidang, tata_tulis, kelengkapan_materi, pencapaian_tujuan, penguasaan_materi, presentasi, nik)
VALUES (9, 77, 77, 77, 77, 77, 'P001')

UPDATE BAP
SET file_path = 'uploads/bap/bap_31.pdf'
WHERE id_bap = 20;

SELECT pg_get_serial_sequence('Bobot_PerTahun_ajaran', 'ID_Tahun_Ajaran');

