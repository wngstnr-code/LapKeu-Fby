import streamlit as st
import google.generativeai as genai
from PIL import Image
import json
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime

def load_css(style_css):
    with open(style_css) as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

load_css("style.css")

def load_secrets():
    if "GOOGLE_API_KEY" in st.secrets:
        api_key = st.secrets["GOOGLE_API_KEY"]
    else:
        api_key = "GANTI_DENGAN_API_KEY_GEMINI_JIKA_ERROR" 
        
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    
    if "gcp_json" in st.secrets:
        creds_dict = dict(st.secrets["gcp_json"])
        creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
    else:
        creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
        
    return api_key, creds

SHEET_NAME = "Laporan Keuangan Feby"
KATEGORI_LIST = ["Fashion", "Food & Drink","Snack", "Grocery", "Alat Tulis Kantor", "Skincare", "Bodycare", "Make Up", "House Hold"] 

try:
    API_KEY, CREDS = load_secrets()
    genai.configure(api_key=API_KEY)
    model = genai.GenerativeModel('gemini-2.5-flash')
    client = gspread.authorize(CREDS)
except Exception as e:
    st.error(f"Error Konfigurasi: {e}. Pastikan file credentials.json ada atau Secrets sudah diatur.")
    st.stop()

def save_to_gsheet(data_json):
    try:
        clean_json = data_json.replace("```json", "").replace("```", "").strip()
        data = json.loads(clean_json)
        
        # Sheet per bulan
        tgl_str = data.get('tanggal', datetime.now().strftime('%Y-%m-%d'))
        try:
            tgl_obj = datetime.strptime(tgl_str, '%Y-%m-%d')
        except:
            tgl_obj = datetime.now()
            
        nama_bulan_indo = ["Januari", "Februari", "Maret", "April", "Mei", "Juni", "Juli", "Agustus", "September", "Oktober", "November", "Desember"]
        sheet_title = f"{nama_bulan_indo[tgl_obj.month - 1]} {tgl_obj.year}"

        sh = client.open(SHEET_NAME)

        try:
            worksheet = sh.worksheet(sheet_title)
        except gspread.exceptions.WorksheetNotFound:
            worksheet = sh.add_worksheet(title=sheet_title, rows="100", cols="20")
            worksheet.append_row(["Tanggal", "Toko", "Kategori", "Nama Barang", "Jumlah", "Harga Satuan", "Total Item", "Input Time"])
            worksheet.format('A1:H1', {'textFormat': {'bold': True}})

        # Insert data
        rows_to_add = []
        waktu = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        for item in data['items']:
            row = [data.get('tanggal'), data.get('toko'), item.get('kategori', '-'), item.get('nama'), item.get('jumlah'), item.get('harga_satuan'), item.get('total'), waktu]
            rows_to_add.append(row)
            
        if rows_to_add:
            worksheet.append_rows(rows_to_add)
        return True, f"Masuk ke sheet: {sheet_title}"

    except Exception as e:
        return False, f"Gagal: {e}"

def process_receipt(image):
    prompt = """Analisis gambar ini dengan sangat teliti:

1. VALIDASI DULU:
   - Apakah ini foto nota belanja yang jelas terbaca?
   - Jika foto blur/tidak jelas/tidak bisa dibaca, jawab: {"error": "Foto terlalu blur atau tidak jelas, mohon upload foto yang lebih tajam"}
   - Jika bukan nota belanja, jawab: {"error": "Ini bukan foto nota belanja, mohon upload foto nota yang valid"}
   - Jika nota kosong/tidak ada item, jawab: {"error": "Nota tidak memiliki item belanja yang dapat dibaca"}

2. Jika VALID, output JSON: {"toko": "Str", "tanggal": "YYYY-MM-DD", "items": [{"kategori": "Str", "nama": "Str", "jumlah": Int, "harga_satuan": Int, "total": Int}]}

Kategori yang tersedia: Fashion, Food & Drink, Snack, Grocery, Alat Tulis Kantor, Skincare, Bodycare, Make Up, House Hold.
Pilih kategori yang paling sesuai untuk setiap barang."""
    
    response = model.generate_content([prompt, image])
    result_text = response.text.replace("```json", "").replace("```", "").strip()
    
    # Cek apakah ada error dari AI
    try:
        parsed = json.loads(result_text)
        if "error" in parsed:
            raise ValueError(parsed["error"])
        # Validasi struktur data
        if "toko" not in parsed or "items" not in parsed:
            raise ValueError("Format nota tidak valid atau tidak dapat dibaca dengan jelas")
        if not parsed["items"] or len(parsed["items"]) == 0:
            raise ValueError("Tidak ada item yang dapat dibaca dari nota ini")
    except json.JSONDecodeError:
        raise ValueError("Foto tidak dapat diproses sebagai nota - mungkin blur, terpotong, atau bukan nota belanja")
    
    return result_text

st.title("💰 AI Monthly Money Talita Feby 🤍")

tab1, tab2 = st.tabs(["📷 Scan Nota", "✍️ Input Manual"])

# TAB 1: SCAN NOTA
with tab1:
    st.subheader("Upload dan Scan Nota Belanja")
    uploaded_files = st.file_uploader("Upload Nota", type=["jpg", "png", "jpeg"], accept_multiple_files=True)
    if uploaded_files:
        # Tampilkan semua foto yang diupload dalam grid
        cols = st.columns(min(len(uploaded_files), 3))
        images = []
        for idx, uploaded_file in enumerate(uploaded_files):
            img = Image.open(uploaded_file)
            images.append(img)
            with cols[idx % 3]:
                st.image(img, width=200, caption=f"Nota {idx+1}")
        
        if st.button("🔍 Proses Nota", key="btn_scan"):
            with st.spinner(f'AI sedang memproses {len(images)} nota...'):
                success_count = 0
                error_count = 0
                for idx, img in enumerate(images):
                    try:
                        res = process_receipt(img)
                        success, msg = save_to_gsheet(res)
                        if success:
                            success_count += 1
                            st.success(f"✅ Nota {idx+1}: {msg}")
                        else:
                            error_count += 1
                            st.error(f"❌ Nota {idx+1}: {msg}")
                    except ValueError as e:
                        # Error dari validasi (blur, bukan nota, dll)
                        error_count += 1
                        st.error(f"❌ Nota {idx+1}: {str(e)}")
                    except Exception as e:
                        # Error lainnya
                        error_count += 1
                        st.error(f"❌ Nota {idx+1}: Terjadi kesalahan - {str(e)}")
                
                if success_count > 0:
                    st.balloons()
                st.info(f"🎯 Selesai! Berhasil: {success_count}, Gagal: {error_count}")

# TAB 2: INPUT MANUAL
with tab2:
    st.subheader("Input Transaksi Manual")
    
    if 'num_items' not in st.session_state:
        st.session_state.num_items = 1
    
    with st.form("form_manual"):
        col1, col2 = st.columns(2)
        
        with col1:
            toko = st.text_input("Nama Toko", placeholder="Contoh: Indomaret")
        
        with col2:
            tanggal = st.date_input("Tanggal Transaksi", value=datetime.now())
        
        st.write("---")
        
        items_data = []
        for i in range(st.session_state.num_items):
            st.write(f"**Barang {i+1}**")
            col_a, col_b, col_c, col_d = st.columns([2, 2, 1, 2])
            
            with col_a:
                nama_barang = st.text_input(f"Nama Barang", key=f"nama_{i}", placeholder="Contoh: Indomie Goreng")
            with col_b:
                kategori = st.selectbox(f"Kategori", KATEGORI_LIST, key=f"kategori_{i}")
            with col_c:
                jumlah = st.number_input(f"Jumlah", key=f"jumlah_{i}", min_value=1, value=1, step=1)
            with col_d:
                harga_satuan = st.number_input(f"Harga Satuan (Rp)", key=f"harga_{i}", min_value=0, value=0, step=100)
            
            if nama_barang:
                total = jumlah * harga_satuan
                items_data.append({
                    "nama": nama_barang,
                    "kategori": kategori,
                    "jumlah": int(jumlah),
                    "harga_satuan": int(harga_satuan),
                    "total": int(total)
                })
        
        st.write("---")
        submitted = st.form_submit_button("💾 Simpan", use_container_width=True)
        
        if submitted:
            if not toko:
                st.error("Nama toko harus diisi!")
            elif len(items_data) == 0:
                st.error("Minimal 1 barang harus diisi!")
            else:
                manual_data = {
                    "toko": toko,
                    "tanggal": tanggal.strftime('%Y-%m-%d'),
                    "items": items_data
                }
                
                success, msg = save_to_gsheet(json.dumps(manual_data))
                if success: 
                    st.success(msg)
                    st.balloons()
                    st.session_state.num_items = 1
                else: 
                    st.error(msg)
    
    # Tombol tambah/kurang barang
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