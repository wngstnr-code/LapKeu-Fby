import streamlit as st
import google.generativeai as genai
from PIL import Image
import json
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime

# --- FUNGSI LOAD CREDENTIALS (AMAN UNTUK DEPLOY) ---
def load_secrets():
    """
    Fungsi pintar ini akan mengecek:
    1. Apakah jalan di Streamlit Cloud? (Pakai st.secrets)
    2. Apakah jalan di Lokal? (Pakai file credentials.json & secrets.toml)
    """
    # Cek API KEY
    if "GOOGLE_API_KEY" in st.secrets:
        api_key = st.secrets["GOOGLE_API_KEY"]
    else:
        # Fallback manual jika belum setting secrets (opsional)
        api_key = "GANTI_DENGAN_API_KEY_GEMINI_JIKA_ERROR" 
        
    # Cek Google Sheet Credentials
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    
    if "gcp_json" in st.secrets:
        # Jika di Cloud
        creds_dict = dict(st.secrets["gcp_json"])
        creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
    else:
        # Jika di Lokal (Laptop sendiri)
        creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
        
    return api_key, creds

# --- KONFIGURASI AWAL ---
SHEET_NAME = "Laporan Keuangan Feby" 

try:
    API_KEY, CREDS = load_secrets()
    genai.configure(api_key=API_KEY)
    model = genai.GenerativeModel('gemini-2.5-flash')
    client = gspread.authorize(CREDS)
except Exception as e:
    st.error(f"Error Konfigurasi: {e}. Pastikan file credentials.json ada atau Secrets sudah diatur.")
    st.stop()

# --- FUNGSI UTAMA ---
def save_to_gsheet(data_json):
    try:
        clean_json = data_json.replace("```json", "").replace("```", "").strip()
        data = json.loads(clean_json)
        
        # Logika Ganti Sheet per Bulan
        tgl_str = data.get('tanggal', datetime.now().strftime('%Y-%m-%d'))
        try:
            tgl_obj = datetime.strptime(tgl_str, '%Y-%m-%d')
        except:
            tgl_obj = datetime.now()
            
        nama_bulan_indo = ["Januari", "Februari", "Maret", "April", "Mei", "Juni", "Juli", "Agustus", "September", "Oktober", "November", "Desember"]
        sheet_title = f"{nama_bulan_indo[tgl_obj.month - 1]} {tgl_obj.year}"

        sh = client.open(SHEET_NAME)

        # Cek/Buat Sheet
        try:
            worksheet = sh.worksheet(sheet_title)
        except gspread.exceptions.WorksheetNotFound:
            worksheet = sh.add_worksheet(title=sheet_title, rows="100", cols="20")
            worksheet.append_row(["Tanggal", "Toko", "Nama Barang", "Jumlah", "Harga Satuan", "Total Item", "Input Time"])
            worksheet.format('A1:G1', {'textFormat': {'bold': True}})

        # Masukkan Data
        rows_to_add = []
        waktu = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        for item in data['items']:
            row = [data.get('tanggal'), data.get('toko'), item.get('nama'), item.get('jumlah'), item.get('harga_satuan'), item.get('total'), waktu]
            rows_to_add.append(row)
            
        if rows_to_add:
            worksheet.append_rows(rows_to_add)
        return True, f"Masuk ke sheet: {sheet_title}"

    except Exception as e:
        return False, f"Gagal: {e}"

def process_receipt(image):
    prompt = """Analisis nota ini. Output JSON valid: {"toko": "Str", "tanggal": "YYYY-MM-DD", "items": [{"nama": "Str", "jumlah": Int, "harga_satuan": Int, "total": Int}]}"""
    response = model.generate_content([prompt, image])
    return response.text

# --- TAMPILAN WEB ---
st.title("🧾 AI Keuangan Bulanan")

# Pilihan metode input
tab1, tab2 = st.tabs(["📷 Scan Nota", "✍️ Input Manual"])

# TAB 1: SCAN NOTA
with tab1:
    st.subheader("Upload dan Scan Nota Belanja")
    uploaded_file = st.file_uploader("Upload Nota", type=["jpg", "png", "jpeg"])
    if uploaded_file:
        img = Image.open(uploaded_file)
        st.image(img, width=250)
        if st.button("Proses", key="btn_scan"):
            with st.spinner('AI sedang bekerja...'):
                res = process_receipt(img)
                success, msg = save_to_gsheet(res)
                if success: st.success(msg)
                else: st.error(msg)

# TAB 2: INPUT MANUAL
with tab2:
    st.subheader("Input Transaksi Manual")
    
    # Inisialisasi session state untuk tracking jumlah items
    if 'num_items' not in st.session_state:
        st.session_state.num_items = 1
    
    with st.form("form_manual"):
        col1, col2 = st.columns(2)
        
        with col1:
            toko = st.text_input("Nama Toko", placeholder="Contoh: Indomaret")
        
        with col2:
            tanggal = st.date_input("Tanggal Transaksi", value=datetime.now())
        
        st.write("---")
        st.write("**Detail Barang**")
        
        items_data = []
        for i in range(st.session_state.num_items):
            st.write(f"**Barang #{i+1}**")
            col_a, col_b, col_c = st.columns(3)
            
            with col_a:
                nama_barang = st.text_input(f"Nama Barang", key=f"nama_{i}", placeholder="Contoh: Indomie Goreng")
            with col_b:
                jumlah = st.number_input(f"Jumlah", key=f"jumlah_{i}", min_value=1, value=1, step=1)
            with col_c:
                harga_satuan = st.number_input(f"Harga Satuan (Rp)", key=f"harga_{i}", min_value=0, value=0, step=100)
            
            if nama_barang:  # Hanya tambahkan jika ada nama barang
                total = jumlah * harga_satuan
                items_data.append({
                    "nama": nama_barang,
                    "jumlah": int(jumlah),
                    "harga_satuan": int(harga_satuan),
                    "total": int(total)
                })
        
        st.write("---")
        submitted = st.form_submit_button("💾 Simpan ke Google Sheet", use_container_width=True)
        
        if submitted:
            if not toko:
                st.error("Nama toko harus diisi!")
            elif len(items_data) == 0:
                st.error("Minimal 1 barang harus diisi!")
            else:
                # Buat JSON manual
                manual_data = {
                    "toko": toko,
                    "tanggal": tanggal.strftime('%Y-%m-%d'),
                    "items": items_data
                }
                
                # Simpan ke Google Sheet
                success, msg = save_to_gsheet(json.dumps(manual_data))
                if success: 
                    st.success(msg)
                    st.balloons()
                    # Reset setelah berhasil
                    st.session_state.num_items = 1
                else: 
                    st.error(msg)
    
    # Tombol tambah/kurang barang DI LUAR form
    st.write("---")
    col_btn1, col_btn2 = st.columns(2)
    with col_btn1:
        if st.button("➕ Tambah Barang", use_container_width=True):
            st.session_state.num_items += 1
            st.rerun()
    with col_btn2:
        if st.button("➖ Kurangi Barang", use_container_width=True, disabled=(st.session_state.num_items <= 1)):
            st.session_state.num_items -= 1
            st.rerun()