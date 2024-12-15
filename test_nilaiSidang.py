import unittest
from unittest.mock import patch, MagicMock
from main import app  # Pastikan `app` merujuk pada aplikasi Flask Anda

class TestNilaiRoute(unittest.TestCase):

    def setUp(self):
        # Konfigurasi untuk testing Flask
        self.app = app.test_client()
        self.app.testing = True

        # Simulasikan session
        with self.app.session_transaction() as sess:
            sess['email'] = 'siti@student.unpar.ac.id'
            sess['id'] = 'M001'
            sess['name'] = 'Siti Rahmawati'
            sess['password'] = '123'
            sess['role'] = 'mahasiswa'

    @patch('main.get_db_connection')
    def test_nilai_total_success(self, mock_get_db_connection):
        # Mocking database connection dan hasil query
        # mock_conn = MagicMock()
        # mock_get_db_connection.return_value = mock_conn

        # # Data mock untuk sidang dan nilai
        # mock_sidang_info = MagicMock()
        # mock_sidang_info.keys.return_value = ['ID_Sidang', 'tempat_sidang', 'tanggal_sidang', 'waktu_mulai', 'waktu_selesai', 'catatan']
        # mock_sidang_info.values.return_value = [1, 'Ruang 101', '2024-12-05', '08:00', '10:00', 'Sudah lancar, materi lengkap, siap untuk sidang. Test Alert']

        # mock_nilai_detail = MagicMock()
        # mock_nilai_detail.keys.return_value = ['total_nilai']
        # mock_nilai_detail.values.return_value = [82.1]

        # # Mock fetchone
        # mock_conn.execute.return_value.fetchone.side_effect = [
        #     mock_sidang_info,  # Hasil query untuk sidang
        #     mock_nilai_detail  # Hasil query untuk nilai
        # ]
        # print(f"Mock sidang info: {mock_sidang_info.values()}")
        # print(f"Mock nilai detail: {mock_nilai_detail.values()}")

        # Mengirimkan request GET ke endpoint dengan parameter JSON
        response = self.app.get('/mahasiswa/nilai?format=json')

        # Memastikan response status code adalah 200
        self.assertEqual(response.status_code, 200)

        # Memastikan data JSON sesuai
        response_data = response.get_json()
        print(response_data)
        self.assertIn('sidang', response_data)
        self.assertIn('nilai_detail', response_data)

        # Memastikan data sidang dan nilai sesuai
        self.assertEqual(response_data['sidang']['ID_Sidang'], 1)
        self.assertEqual(response_data['nilai_detail']['total_nilai'], 86.3)

if __name__ == '__main__':
    unittest.main()

