# Dokumen Spesifikasi: Demo Stack Agentic AI & MCP
**Proyek:** "AgenKampus" - Demo 1 Jam untuk Pemula
**Versi:** 1.0
**Tujuan:** Membangun tumpukan (stack) minimalis namun realistis untuk mendemonstrasikan konsep *Agentic AI*, *Model Context Protocol (MCP)*, dan *RAG-for-Tools*. Tumpukan ini harus mudah di-setup dan berfokus pada visualisasi alur kerja AI.

## 1. 🎯 Visi & Konsep Kunci (untuk Diajarkan)

Kita tidak sedang membangun *chatbot*. Kita sedang membangun **Agent**, yaitu sebuah program yang dapat **membuat keputusan** dan **menggunakan alat (tools)** untuk menyelesaikan tugas.

Konsep Kunci yang akan didemokan:

1.  **Agent (Otak):** "Manajer" yang cerdas (ditenagai oleh Gemini) yang menerima tugas, membuat rencana, dan mendelegasikannya.
2.  **MCP (Jembatan Aman):** "Manajer" tidak pernah menyentuh database. Ia berbicara dengan "Asisten" (MCP Server) melalui protokol standar. Ini adalah **konsep keamanan utama**.
3.  **Tool (Pekerja):** "Asisten" (MCP Server) memiliki "Tim Pekerja" (Tools) yang melakukan pekerjaan nyata, seperti `query_database` atau `get_time`.
4.  **RAG-for-Tools (Pustakawan):** Saat "Manajer" memiliki 1000 "Pekerja", ia tidak mengingat semuanya. Ia bertanya pada "Pustakawan" (ChromaDB) untuk menemukan pekerja yang relevan terlebih dahulu.

## 2. 🏗️ Arsitektur Sistem

Arsitektur ini dirancang untuk kesederhanaan demo, menggunakan komponen berbasis file (SQLite, ChromaDB) untuk menghindari kebutuhan server eksternal.



**Diagram Alur Kerja (Skenario Paling Kompleks):**

1.  **User** bertanya: `"Siapa dosen pembimbing Agus?"`
2.  **Agent (LangChain)** menerima kueri.
3.  **Agent** bertanya ke **Tool Retriever (RAG)**: `"Tool apa yang cocok untuk 'dosen pembimbing'?"`
4.  **Tool Retriever** (menggunakan **ChromaDB**) mencari dan menjawab: `"Tool 'get_dosen_pembimbing' adalah yang paling relevan."`
5.  **Agent** (ditenagai **Gemini**) kini tahu tool yang harus digunakan. Ia memanggil **MCP Server "Akademik"** dan mengeksekusi tool `get_dosen_pembimbing(nama_mahasiswa="Agus")`.
6.  **MCP Server "Akademik"** menerima panggilan, terhubung ke **SQLite**, menjalankan *query* SQL yang aman, dan mendapatkan nama dosen.
7.  **Server** mengembalikan nama dosen ke **Agent**.
8.  **Agent** merumuskan jawaban akhir untuk **User**.

## 3. 🧩 Spesifikasi Komponen

### A. Orkestrator Agent (Otak)
* **Teknologi:** Python, LangChain.
* **Logika Inti:** Mengimplementasikan alur kerja **RAG-for-Tools (2-langkah)**.
* **LLM API:** **Google Gemini** (misalnya, `gemini-1.5-flash` atau `pro`) melalui Google AI Studio.
* **Kebutuhan Setup:** `GOOGLE_API_KEY` disimpan sebagai *environment variable*.

### B. Tool Retriever (Pustakawan Vektor)
* **Tujuan:** Menyimpan dan mengambil *deskripsi* tool.
* **Vector DB:** **ChromaDB**.
    * **Alasan:** Sempurna untuk demo. Dapat berjalan *in-memory* atau berbasis file (persisten) tanpa perlu server. Sangat ringan.
* **Model Embedding:** **HuggingFace Embeddings** (misalnya, `all-MiniLM-L6-v2`).
    * **Alasan:** Gratis, cepat, dan berjalan 100% lokal. Menghindari ketergantungan API eksternal hanya untuk *embeddings*.

### C. MCP Server #1: "Utilitas" (Tool Sederhana)
* **Tujuan:** Mendemonstrasikan tool sederhana non-database.
* **Teknologi:** Python, FastAPI, FastMCP.
* **Daftar Tool:**
    1.  `get_waktu_saat_ini()`
        * **Deskripsi:** "Gunakan tool ini untuk mendapatkan waktu dan tanggal saat ini. Tidak menerima argumen."
        * **Logika:** Mengembalikan `datetime.now()`.
    2.  `kalkulator_sederhana(ekspresi_matematika: str)`
        * **Deskripsi:** "Gunakan untuk menghitung ekspresi matematika sederhana seperti '2+2' atau '5*10'. Hanya menerima string."
        * **Logika:** Menggunakan `eval()` dalam *sandbox* yang aman (atau library parser).

### D. MCP Server #2: "Akademik" (Tool Database Realistis)
* **Tujuan:** Mendemonstrasikan interaksi database yang aman dan realistis.
* **Teknologi:** Python, FastAPI, FastMCP, `sqlite3`.
* **Database:** **SQLite** (File: `kampus.db`).
    * **Alasan:** Tidak perlu setup server Postgres. Cukup satu file, sangat portabel untuk demo.
* **Daftar Tool:**
    1.  `get_dosen_pembimbing(nama_mahasiswa: str)`
        * **Deskripsi:** "Gunakan untuk mencari nama dosen pembimbing (dospem) dari seorang mahasiswa. Membutuhkan nama lengkap mahasiswa."
        * **Logika:** Menjalankan *query* SQL dengan `JOIN` antara tabel `mahasiswa` dan `dosen`.
    2.  `get_mata_kuliah_mahasiswa(nama_mahasiswa: str)`
        * **Deskripsi:** "Gunakan untuk mendapatkan daftar semua mata kuliah yang diambil oleh seorang mahasiswa. Membutuhkan nama lengkap mahasiswa."
        * **Logika:** Menjalankan *query* SQL dengan `JOIN` 3-tabel (`mahasiswa`, `transkrip`, `mata_kuliah`).

## 4. Realistic" Database Schema (SQLite: `kampus.db`)

Ini penting untuk memberikan "feel"-nya. Data harus saling terkait.

### Tabel
1.  **`dosen`**
    * `id` (INTEGER, PRIMARY KEY)
    * `nama_dosen` (TEXT)
    * `nidn` (TEXT, UNIQUE)
2.  **`mahasiswa`**
    * `id` (INTEGER, PRIMARY KEY)
    * `nama_mahasiswa` (TEXT)
    * `nim` (TEXT, UNIQUE)
    * `id_dospem` (INTEGER, FOREIGN KEY ke `dosen.id`)
3.  **`mata_kuliah`**
    * `id` (INTEGER, PRIMARY KEY)
    * `nama_matkul` (TEXT)
    * `sks` (INTEGER)
4.  **`transkrip`**
    * `id_mahasiswa` (INTEGER, FOREIGN KEY ke `mahasiswa.id`)
    * `id_matkul` (INTEGER, FOREIGN KEY ke `mata_kuliah.id`)
    * `nilai_huruf` (TEXT)

### Konten Data Dummy
* **Dosen:**
    * (1, 'Dr. Budi Santoso', '001')
    * (2, 'Prof. Siti Aminah', '002')
* **Mata Kuliah:**
    * (101, 'Kecerdasan Buatan', 3)
    * (102, 'Basis Data Lanjut', 3)
    * (103, 'Pemrograman Web', 3)
* **Mahasiswa:**
    * (1001, 'Agus Setiawan', '12345', 1)  *(Dospem: Dr. Budi)*
    * (1002, 'Rini Wijaya', '12346', 2)    *(Dospem: Prof. Siti)*
* **Transkrip:**
    * (1001, 101, 'A')  *(Agus ambil AI, dapat A)*
    * (1001, 102, 'B')  *(Agus ambil Basis Data, dapat B)*
    * (1002, 101, 'A')  *(Rini ambil AI, dapat A)*
    * (1002, 103, 'A')  *(Rini ambil Web, dapat A)*

## 5. 🎬 Rencana Sesi Demo (Alur 1 Jam)

* **[00:00 - 05:00] Pendahuluan & Arsitektur**
    * Tampilkan diagram arsitektur.
    * Jelaskan analogi: Manajer (Agent), Asisten (MCP), Pustakawan (RAG/ChromaDB), Pekerja (Tools), Lemari File (SQLite).
    * **Penekanan:** *Mengapa ini aman?* Karena Manajer (AI) tidak memegang kunci Lemari File (Database).

* **[05:00 - 15:00] Tinjau Kode MCP & Database**
    * Tunjukkan file `kampus.db` (misalnya di DB Browser for SQLite).
    * Tunjukkan `mcp_server_akademik.py`. Soroti *docstring* pada `get_dosen_pembimbing`.
    * Soroti *query* SQL di dalam fungsi. **Tekankan:** "SQL ditulis oleh kita, bukan oleh AI. Ini aman."

* **[15:00 - 25:00] Tinjau Kode Agent (Otak)**
    * Tunjukkan `agent_client.py`.
    * Tunjukkan bagian `ChromaDB` dan `HuggingFaceEmbeddings` (Pustakawan).
    * Tunjukkan inisialisasi `GoogleGenerativeAI` (Manajer).
    * Tunjukkan alur 2-langkah (RAG -> Eksekusi).

* **[25:00 - 55:00] Demo Interaktif & Debugging**
    * Jalankan MCP Server (Utilitas & Akademik) di dua terminal.
    * Jalankan `agent_client.py` di terminal ketiga (buat *verbose mode* aktif).
    * **Demo 1 (Simple Tool):** `User: "Jam berapa sekarang?"`
        * Tunjukkan log: Agent *tidak* perlu RAG (atau RAG menemukan 1 tool), langsung memilih `get_waktu_saat_ini`.
    * **Demo 2 (Database Tool):** `User: "Siapa dosen pembimbing Rini Wijaya?"`
        * **Momen Kunci:** Tunjukkan log RAG (Pustakawan) yang menemukan `get_dosen_pembimbing` dan `get_mata_kuliah_mahasiswa`.
        * Tunjukkan log Agent (Manajer) yang dengan cerdas memilih `get_dosen_pembimbing` dari 2 opsi itu.
        * Tunjukkan log di terminal MCP Server Akademik bahwa fungsi itu dipanggil.
    * **Demo 3 (Pertanyaan Gabungan):** `User: "Mata kuliah apa saja yang diambil Agus Setiawan?"`
        * Tunjukkan proses yang sama, tapi kali ini Agent memilih `get_mata_kuliah_mahasiswa`.
    * **Demo 4 (Pertanyaan "Jebakan"):** `User: "Ubah nilai Agus di mata kuliah AI menjadi C."`
        * **Demo Paling Penting:** Tunjukkan bahwa Agent akan gagal. Ia akan berkata, "Maaf, saya tidak punya tool untuk mengubah nilai." Ini membuktikan **keamanan** MCP. Kita hanya mengekspos `get_...` (Read), bukan `set_...` (Write).

* **[55:00 - 60:00] Penutup & Q/A**
    * **Rekap:** Kita membangun agent yang **Aman** (via MCP), **Cerdas** (via Gemini), dan **Efisien** (via RAG-for-Tools) dalam 1 jam.

## 6. 🛠️ Tumpukan Teknologi (Ringkasan)

* **Orkestrasi Agent:** LangChain (Python)
* **LLM API:** Google Gemini (via Google AI Studio)
* **Server Tool:** FastAPI, FastMCP
* **Database Vektor:** ChromaDB (file-based)
* **Database Relasional:** SQLite (file-based)
* **Model Embedding:** `sentence-transformers/all-MiniLM-L6-v2` (lokal)
