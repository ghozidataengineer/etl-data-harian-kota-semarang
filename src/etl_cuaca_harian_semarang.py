import os
import pandas as pd
import requests
from supabase import create_client, Client

# Mengambil kredensial secara aman dari sistem/environment
URL_SUPABASE = os.environ.get("SUPABASE_URL")
ANON_KEY_SUPABASE = os.environ.get("SUPABASE_KEY")

# Cek jika variabel kosong (misal lupa dikonfigurasi)
if not URL_SUPABASE or not ANON_KEY_SUPABASE:
    raise ValueError("Kredensial Supabase tidak ditemukan di Environment Variables!")

supabase: Client = create_client(URL_SUPABASE, ANON_KEY_SUPABASE)

def jalankan_etl():
    print("=== Memulai Proses ETL Harian ===")
    
    # --- FASE 1: EXTRACT (Ambil Data) ---
    url_api = "https://api.open-meteo.com/v1/forecast?latitude=-7.0114&longitude=110.4111&daily=weather_code,rain_sum,temperature_2m_max,temperature_2m_min&timezone=auto"
    
    try:
        respon = requests.get(url_api)
        respon.raise_for_status()
        data_mentah = respon.json()
        print("1. Extract: Data berhasil diambil dari API.")
    except Exception as e:
        print(f"Gagal mengambil data dari API: {e}")
        return

    # --- FASE 2: TRANSFORM (Mengolah dengan Pandas) ---
    try:
        # Masuk langsung ke key 'daily' untuk membuat DataFrame
        df = pd.DataFrame(data_mentah["daily"])
        
        # Mapping kamus WMO Code ke teks bahasa Indonesia
        wmo_huruf = {
            0: "Cerah Sempurna",
            1: "Cerah Berawan", 2: "Berawan", 3: "Mendung Total",
            45: "Kabut", 48: "Kabut Tebal",
            51: "Gerimis Ringan", 53: "Gerimis Sedang", 55: "Gerimis Lebat",
            61: "Hujan Ringan", 63: "Hujan Sedang", 65: "Hujan Lebat",
            80: "Hujan Lokal Ringan", 81: "Hujan Lokal Sedang", 82: "Hujan Lokal Lebat",
            95: "Hujan Badai Petir"
        }
        
        # Lakukan transformasi kolom
        df["kondisi_cuaca"] = df["weather_code"].map(wmo_huruf).fillna("Cuaca Lainnya")
        df["kota"] = "Semarang"
        
        # Rename kolom agar sesuai dengan kolom di tabel database Supabase
        df = df.rename(columns={
            "time": "tanggal",
            "temperature_2m_max": "suhu_max",
            "temperature_2m_min": "suhu_min",
            "rain_sum": "curah_hujan_mm"
        })
        
        # Konversi DataFrame menjadi format list dictionary untuk dikirim ke Supabase
        data_siap_load = df[["tanggal", "kota", "weather_code", "kondisi_cuaca", "suhu_max", "suhu_min", "curah_hujan_mm"]].to_dict(orient="records")
        print(f"2. Transform: Berhasil memproses {len(data_siap_load)} baris data harian.")
    except Exception as e:
        print(f"Gagal melakukan transformasi data: {e}")
        return

    # --- FASE 3: LOAD (Kirim ke Supabase menggunakan UPSERT) ---
    # INDENTASI DIPERBAIKI: Sejajar dengan blok try-except sebelumnya
    try:
        data_input = supabase.table("data_cuaca_semarang").upsert(
            data_siap_load, 
            on_conflict="kota,tanggal"
        ).execute()
        
        print("3. Load: Semua data sukses diperbarui (UPSERT) ke database Supabase!")
    except Exception as e:
        print(f"Gagal menyimpan data ke Supabase: {e}")


if __name__ == "__main__":
    jalankan_etl()
