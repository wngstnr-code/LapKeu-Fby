# 💰 AI Keuangan Bulanan - Talita Feby

Aplikasi web berbasis AI untuk mencatat dan mengelola pengeluaran bulanan secara otomatis menggunakan Google Gemini AI dan Google Sheets.

## ✨ Fitur Utama

### 📷 Scan Nota Otomatis
- Upload foto nota belanja (JPG, PNG, JPEG)
- AI otomatis membaca dan mengekstrak data:
  - Nama toko
  - Tanggal transaksi
  - Daftar barang yang dibeli
  - Jumlah, harga satuan, dan total per item
- Data langsung tersimpan ke Google Sheets

### ✍️ Input Manual
- Input transaksi secara manual jika tidak punya foto nota
- Tambah/kurangi jumlah barang dengan mudah
- Mobile-friendly dengan tombol yang besar

### 📊 Google Sheets Integration
- **Sheet otomatis per bulan** (Januari 2026, Februari 2026, dst)
- **Format Rupiah otomatis** untuk kolom harga
- **Baris TOTAL otomatis** yang menghitung total pengeluaran
- Header dengan format bold dan background abu-abu
- Timestamp setiap input data

## 🚀 Demo

**Live App:** [https://lapkeu-fby.streamlit.app](https://lapkeu-fby.streamlit.app)

## 🛠️ Teknologi yang Digunakan

- **Streamlit** - Framework web app Python
- **Google Gemini AI** (gemini-2.5-flash) - AI untuk scan nota
- **Google Sheets API** - Database cloud
- **gspread** - Python library untuk Google Sheets
- **PIL (Pillow)** - Image processing

## 📦 Instalasi Lokal

### 1. Clone Repository
```bash
git clone https://github.com/wngstnr-code/LapKeu-Fby.git
cd LapKeu-Fby
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Setup Google Cloud Credentials

#### a. Google Gemini API Key
1. Buka [Google AI Studio](https://aistudio.google.com/app/apikey)
2. Generate API Key
3. Copy API Key

#### b. Google Sheets Service Account
1. Buka [Google Cloud Console](https://console.cloud.google.com/)
2. Buat project baru atau pilih project yang ada
3. Enable **Google Sheets API** dan **Google Drive API**
4. Buat Service Account:
   - IAM & Admin → Service Accounts → Create Service Account
   - Download JSON key file
   - Simpan sebagai `credentials.json` di folder project

5. Share Google Sheets:
   - Buat spreadsheet dengan nama: **"Laporan Keuangan Feby"**
   - Share ke email service account (lihat di `credentials.json` → `client_email`)
   - Set sebagai **Editor**

### 4. Setup Secrets (Lokal)

Buat file `.streamlit/secrets.toml`:
```toml
GOOGLE_API_KEY = "YOUR_GEMINI_API_KEY"
```

### 5. Jalankan Aplikasi
```bash
streamlit run app.py
```

Aplikasi akan terbuka di browser: `http://localhost:8501`

## 🌐 Deploy ke Streamlit Cloud

### 1. Push ke GitHub
```bash
git add .
git commit -m "Initial commit"
git push origin main
```

### 2. Deploy
1. Buka [share.streamlit.io](https://share.streamlit.io/)
2. Login dengan GitHub
3. Klik **New app**
4. Pilih repository: `wngstnr-code/LapKeu-Fby`
5. Branch: `main`
6. Main file: `app.py`
7. Klik **Advanced settings** → **Secrets**

### 3. Setup Secrets (Cloud)
Paste konfigurasi ini di **Secrets**:

```toml
GOOGLE_API_KEY = "YOUR_GEMINI_API_KEY"

[gcp_json]
type = "service_account"
project_id = "YOUR_PROJECT_ID"
private_key_id = "YOUR_PRIVATE_KEY_ID"
private_key = """-----BEGIN PRIVATE KEY-----
YOUR_PRIVATE_KEY_HERE
-----END PRIVATE KEY-----"""
client_email = "YOUR_SERVICE_ACCOUNT_EMAIL"
client_id = "YOUR_CLIENT_ID"
auth_uri = "https://accounts.google.com/o/oauth2/auth"
token_uri = "https://oauth2.googleapis.com/token"
auth_provider_x509_cert_url = "https://www.googleapis.com/oauth2/v1/certs"
client_x509_cert_url = "YOUR_CERT_URL"
universe_domain = "googleapis.com"
```

**⚠️ Catatan:** Ambil data dari file `credentials.json` yang sudah di-download

### 4. Deploy
Klik **Deploy** dan tunggu 2-3 menit!

## 📱 Cara Penggunaan

### Scan Nota
1. Buka tab **"📷 Scan Nota"**
2. Upload foto nota belanja
3. Klik tombol **"SIKATSSS"**
4. AI akan otomatis membaca dan menyimpan data
5. Cek Google Sheets untuk melihat hasilnya

### Input Manual
1. Buka tab **"✍️ Input Manual"**
2. Isi nama toko dan tanggal
3. Isi detail barang (nama, jumlah, harga)
4. Klik **"➕ Tambah Barang"** jika ingin tambah item
5. Klik **"💾 Simpan"** untuk menyimpan ke Google Sheets

## 📊 Format Google Sheets

Setiap bulan akan otomatis dibuatkan sheet baru dengan format:

| Tanggal | Toko | Nama Barang | Jumlah | Harga Satuan | Total Item | Input Time |
|---------|------|-------------|--------|--------------|------------|------------|
| 2026-01-08 | Indomaret | Indomie | 5 | Rp 3.500 | Rp 17.500 | 2026-01-08 10:30 |
| | | | | **TOTAL PENGELUARAN:** | **Rp 47.500** | |

## 🔒 Keamanan

- File `credentials.json` **TIDAK** akan ter-upload ke GitHub (sudah di `.gitignore`)
- Secrets disimpan aman di Streamlit Cloud
- Service Account hanya punya akses ke Google Sheets yang di-share

## 🤝 Kontribusi

Kontribusi, issues, dan feature requests sangat diterima!

## 📝 License

MIT License - Bebas digunakan untuk keperluan pribadi atau komersial

## 👨‍💻 Author

**Wangsit Nursahada**
- GitHub: [@wngstnr-code](https://github.com/wngstnr-code)

## 🙏 Acknowledgments

- Google Gemini AI untuk teknologi AI
- Streamlit untuk framework yang mudah digunakan
- Google Sheets API untuk database cloud gratis

---

**Made with ❤️ for Talita Feby**