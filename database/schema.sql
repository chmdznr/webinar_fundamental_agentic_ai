-- AgenKampus Database Schema
-- Educational demo database for Agentic AI with MCP

-- Table: dosen (Lecturers/Academic Advisors)
CREATE TABLE IF NOT EXISTS dosen (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nama_dosen TEXT NOT NULL,
    nidn TEXT UNIQUE NOT NULL
);

-- Table: mahasiswa (Students)
CREATE TABLE IF NOT EXISTS mahasiswa (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nama_mahasiswa TEXT NOT NULL,
    nim TEXT UNIQUE NOT NULL,
    id_dospem INTEGER NOT NULL,
    FOREIGN KEY (id_dospem) REFERENCES dosen(id)
);

-- Table: mata_kuliah (Courses)
CREATE TABLE IF NOT EXISTS mata_kuliah (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nama_matkul TEXT NOT NULL,
    sks INTEGER NOT NULL
);

-- Table: transkrip (Transcript - student course grades)
CREATE TABLE IF NOT EXISTS transkrip (
    id_mahasiswa INTEGER NOT NULL,
    id_matkul INTEGER NOT NULL,
    nilai_huruf TEXT NOT NULL,
    PRIMARY KEY (id_mahasiswa, id_matkul),
    FOREIGN KEY (id_mahasiswa) REFERENCES mahasiswa(id),
    FOREIGN KEY (id_matkul) REFERENCES mata_kuliah(id)
);

-- Insert dummy data for dosen
INSERT OR IGNORE INTO dosen (id, nama_dosen, nidn) VALUES
    (1, 'Dr. Budi Santoso', '001'),
    (2, 'Prof. Siti Aminah', '002');

-- Insert dummy data for mata_kuliah
INSERT OR IGNORE INTO mata_kuliah (id, nama_matkul, sks) VALUES
    (101, 'Kecerdasan Buatan', 3),
    (102, 'Basis Data Lanjut', 3),
    (103, 'Pemrograman Web', 3);

-- Insert dummy data for mahasiswa
INSERT OR IGNORE INTO mahasiswa (id, nama_mahasiswa, nim, id_dospem) VALUES
    (1001, 'Agus Setiawan', '12345', 1),
    (1002, 'Rini Wijaya', '12346', 2);

-- Insert dummy data for transkrip
INSERT OR IGNORE INTO transkrip (id_mahasiswa, id_matkul, nilai_huruf) VALUES
    (1001, 101, 'A'),  -- Agus takes AI, gets A
    (1001, 102, 'B'),  -- Agus takes Database, gets B
    (1002, 101, 'A'),  -- Rini takes AI, gets A
    (1002, 103, 'A');  -- Rini takes Web, gets A
