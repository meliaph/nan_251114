import streamlit as st
import pandas as pd
import json
import io

def process_log_data(file_content):
    """
    Memproses konten file log (asumsi format JSON Array) dan meratakan data.
    """
    processed_records = []
    
    try:
        # Menguraikan SELURUH konten file sebagai satu struktur JSON (asumsi: JSON Array)
        data_array = json.loads(file_content)
        
        # Memastikan data yang dimuat adalah sebuah list (array)
        if not isinstance(data_array, list):
            st.error("Format JSON tidak valid. Harap pastikan file Anda berisi array objek JSON (dimulai dengan '[' dan diakhiri dengan ']').")
            return pd.DataFrame()
            
    except json.JSONDecodeError as e:
        st.error(f"Gagal mengurai file JSON. Pastikan file Anda adalah JSON yang valid dan lengkap. Pesan Error: {e}")
        return pd.DataFrame()
    except Exception as e:
        st.error(f"Terjadi kesalahan tak terduga saat memproses file: {e}")
        return pd.DataFrame()
        
    # Memproses setiap record (objek) dalam array
    for record in data_array:
        
        # Data dasar
        data = {
            "item_id": record.get("item_id"),
            "item_name": record.get("item_name"),
            "item_status": record.get("item_status"),
            "deboost": record.get("deboost"),
            
            # Menyimpan seluruh array sebagai string JSON
            "item_status_details": json.dumps(record.get("item_status_details")),
            
            # Menyimpan seluruh deboost_details sebagai string JSON
            "deboost_details": json.dumps(record.get("deboost_details")),
            
            # Inisialisasi kolom yang diratakan sebagai None
            "violation_type": None,
            "violation_reason": None,
            "suggestion": None,
            "update_time": None,
            "fix_deadline_time": None,
        }
        
        # Meratakan detail status (mengambil elemen pertama dari array, jika ada)
        details = record.get("item_status_details")
        if details and isinstance(details, list) and len(details) > 0:
            first_detail = details[0]
            data["violation_type"] = first_detail.get("violation_type")
            data["violation_reason"] = first_detail.get("violation_reason")
            data["suggestion"] = first_detail.get("suggestion")
            data["update_time"] = first_detail.get("update_time")
            data["fix_deadline_time"] = first_detail.get("fix_deadline_time")
            
        processed_records.append(data)
        
    return pd.DataFrame(processed_records)

def convert_df_to_csv(df):
    """Mengubah DataFrame menjadi string CSV."""
    return df.to_csv(index=False).encode('utf-8')

st.set_page_config(
    page_title="JSON Log Flattener ke CSV",
    layout="centered",
    initial_sidebar_state="expanded"
)

st.title("Log JSON ke Konverter CSV")
st.markdown("Unggah file teks (JSON Array) log data Anda di sini untuk meratakan data dan mengunduh file CSV.")

# Mengunggah File
uploaded_file = st.file_uploader(
    "Pilih File Log (.txt atau .json)",
    type=["txt", "json"],
    help="Pastikan file Anda berisi array objek JSON (dimulai dengan '[' dan diakhiri dengan ']')."
)

df = pd.DataFrame()

if uploaded_file is not None:
    try:
        # Membaca file sebagai string
        file_content = uploaded_file.getvalue().decode("utf-8")
        
        # Memproses data
        df = process_log_data(file_content)
        
        if not df.empty:
            st.success(f"File berhasil diproses! Ditemukan {len(df)} baris data yang valid.")
            
            # Menampilkan preview DataFrame
            st.subheader("Pratinjau Data yang Diproses")
            st.dataframe(df.head(10), use_container_width=True)

            # Tombol Unduh
            csv_data = convert_df_to_csv(df)
            
            st.download_button(
                label="Unduh Data sebagai CSV",
                data=csv_data,
                file_name='processed_log_data.csv',
                mime='text/csv',
                key='download_csv_button',
                help="Klik untuk mengunduh DataFrame yang telah diproses sebagai file CSV."
            )
        
    except Exception as e:
        st.error(f"Terjadi kesalahan saat memproses file: {e}")
        st.caption("Pastikan format file Anda adalah JSON Array yang valid.")

# Menambahkan contoh format data untuk panduan
st.markdown("---")
st.subheader("Struktur Output CSV:")
st.markdown("""
| Kolom | Asal Data | Catatan |
| :--- | :--- | :--- |
| **item_id** | Tingkat Atas | |
| **item_name** | Tingkat Atas | |
| **item_status** | Tingkat Atas | |
| **deboost** | Tingkat Atas | |
| **item_status_details** | Tingkat Atas | Disimpan sebagai string JSON mentah. |
| **violation_type** | `item_status_details` | Diambil dari elemen pertama. |
| **violation_reason** | `item_status_details` | Diambil dari elemen pertama. |
| **suggestion** | `item_status_details` | Diambil dari elemen pertama. |
| **update_time** | `item_status_details` | Diambil dari elemen pertama. |
| **fix_deadline_time** | `item_status_details` | Diambil dari elemen pertama. |
| **deboost_details** | Tingkat Atas | Disimpan sebagai string JSON mentah. |
""")

st.caption("Kolom `violation_*` diratakan dari objek pertama di array `item_status_details`.")
