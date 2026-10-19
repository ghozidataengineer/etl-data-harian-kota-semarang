# Automated Weather ETL Pipeline (API to Supabase Data Warehouse)

[![Python](https://shields.io)](https://python.org)
[![Pandas](https://shields.io)](https://pydata.org)
[![Supabase](https://shields.io)](https://supabase.com)

Repositori ini berisi proyek **Data Engineering** berskala kecil yang mengimplementasikan *pipeline* ETL (Extract, Transform, Load) harian secara otomatis. Proyek ini mengekstraksi data prakiraan cuaca kota Semarang dari API publik, mentransformasikannya menggunakan **Pandas**, dan menyimpannya ke **Supabase Data Warehouse** menggunakan metode *Upsert* untuk mencegah duplikasi data.

## Arsitektur Data & Alur Kerja

```text
┌───────────┐         ┌───────────┐         ┌──────────────┐
│  Open-    │ Extract │  Pandas   │  Load   │   Supabase   │
│ Meteo API ├────────>│ DataFrame ├────────>│  (PostgreSQL │
│   (Raw)   │ (JSON)  │ (Cleaned) │(Upsert) │ Cloud DB)    │
└───────────┘         └───────────┘         └──────────────┘
```

1. **Extract**: Mengambil data cuaca mentah berbentuk JSON secara berkala dari Open-Meteo API (koordinat kota Semarang).
2. **Transform**: 
   * Mengonversi kode cuaca WMO (World Meteorological Organization) numerik menjadi teks deskriptif Bahasa Indonesia (contoh: `61` -> `Hujan Ringan`).
   * Membersihkan, memetakan, dan mengubah nama kolom agar sesuai dengan standar skema *database*.
3. **Load**: Memasukkan data ke Supabase dengan operasi **UPSERT** berbasis *constraint* gabungan `(kota, tanggal)` untuk memastikan data harian selalu terbarui tanpa ada duplikasi baris.

## Teknologi yang Digunakan
* **Bahasa Pemrograman:** Python 3.x
* **Library Utama:** `pandas` (Manipulasi Data), `requests` (API Client), `supabase-py` (Database Connector)
* **Penyimpanan Data:** Cloud PostgreSQL (Supabase)
* **Keamanan:** Environment Variables (`os.environ`) untuk melindungi kredensial database.

## Skema Tabel Database (`data_cuaca_semarang`)

Tabel pada database Supabase dikonfigurasi menggunakan skema berikut:

| Nama Kolom | Tipe Data | Keterangan |
| :--- | :--- | :--- |
| `tanggal` (PK) | Date | Tanggal prakiraan cuaca |
| `kota` (PK) | Text | Nama kota (Semarang) |
| `weather_code` | Integer | Kode cuaca standar WMO |
| `kondisi_cuaca`| Text | Deskripsi cuaca dalam Bahasa Indonesia |
| `suhu_max` | Float | Suhu maksimum (°C) |
| `suhu_min` | Float | Suhu minimum (°C) |
| `curah_hujan_mm`| Float | Total curah hujan harian (mm) |

> *Catatan: `tanggal` dan `kota` dikonfigurasi sebagai **Composite Primary Key** atau Unique Constraint untuk mendukung fitur Upsert.*

## Cara Menjalankan Proyek Lokal

### 1. Kloning Repositori
```bash
git clone https://github.com
cd nama-repo-kamu
```

### 2. Instalasi Dependensi
Pastikan Anda sudah menginstal pustaka yang diperlukan:
```bash
pip install -r requirements.txt
```

### 3. Konfigurasi Environment Variables
Salin file `.env.example` menjadi `.env` dan isi dengan kredensial Supabase Anda:
```bash
cp .env.example .env
```
Isi di dalam file `.env`:
```env
SUPABASE_URL=https://supabase.co
SUPABASE_KEY=your-anon-key-here
```

### 4. Eksekusi Skrip ETL
Jalankan perintah berikut untuk mengeksekusi pipeline:
```bash
python src/etl_cuaca_harian_semarang.py
```

## Fitur Keamanan & Penanganan Error
* **Kredensial Aman:** Token akses database tidak pernah ditulis keras (*hardcoded*) di dalam kode, melainkan dibaca via sistem operasi demi keamanan tingkat produksi.
* **Robust Error Handling:** Menggunakan blok `try-except` dan `raise_for_status()` untuk mendeteksi kegagalan API atau gangguan jaringan sejak dini, mencegah rusaknya integritas data pada *warehouse*.
