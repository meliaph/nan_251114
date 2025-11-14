import streamlit as st
import pandas as pd
import json
import io

def process_log_data(file_content):
    """
    Memproses konten file log (asumsi format JSON Lines) dan meratakan data.
    """
    processed_records = []
    
    # Memproses konten baris demi baris (untuk menangani JSON Lines)
    for i, raw_line in enumerate(file_content.splitlines()):
        line_number = i + 1
        line = raw_line.strip()
        
        if not line:
            continue
            
        try:
            # Mengurai setiap baris sebagai objek JSON
            record = json.loads(line)
        except json.JSONDecodeError as e:
            # Melewatkan baris yang tidak valid dan memberikan informasi baris serta error
            # Mencetak konten baris, membatasi hingga 50 karakter
            content_preview = line[:50].replace('\n', '\\n').strip()
            st.warning(
                f"Baris {line_number} dilewati (Gagal Parse JSON). "
                f"Pesan Error: {e}. "
                f"Konten Baris: '{content_preview}...'"
            )
            continue
            
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
        
        # Meratakan detail status (mengambil elemen pertama dari array)
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
st.markdown("Unggah file teks (JSON Lines) log data Anda di sini untuk meratakan data dan mengunduh file CSV.")

# Mengunggah File
uploaded_file = st.file_uploader(
    "Pilih File Log (.txt atau .jsonl)",
    type=["txt", "jsonl"],
    help="Asumsikan setiap baris dalam file adalah objek JSON yang terpisah (JSON Lines)."
)

df = pd.DataFrame()

if uploaded_file is not None:
    try:
        # Membaca file sebagai string
        file_content = uploaded_file.getvalue().decode("utf-8")
        
        # Memproses data
        df = process_log_data(file_content)
        
        st.success(f"File berhasil diproses! Ditemukan {len(df)} baris data yang valid.")
        
        # Menampilkan preview DataFrame
        st.subheader("Pratinjau Data yang Diproses")
        st.dataframe(df.head(10), use_container_width=True)

        # Tombol Unduh
        if not df.empty:
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
        st.caption("Pastikan format file Anda adalah JSON Lines (satu objek JSON per baris).")

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
