"""
Database Setup Script for AgenKampus

This script creates the SQLite database and populates it with dummy data
for the educational demo.

Usage:
    python setup_database.py
"""

import sqlite3
import os
from pathlib import Path


def setup_database():
    """Create and initialize the kampus.db database."""

    # Get the directory where this script is located
    script_dir = Path(__file__).parent
    db_path = script_dir / "kampus.db"
    schema_path = script_dir / "schema.sql"

    # Remove existing database if it exists (for clean setup)
    if db_path.exists():
        print(f"Removing existing database at {db_path}")
        os.remove(db_path)

    # Create new database
    print(f"Creating database at {db_path}")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Read and execute schema file
    print(f"Executing schema from {schema_path}")
    with open(schema_path, 'r') as f:
        schema_sql = f.read()

    cursor.executescript(schema_sql)
    conn.commit()

    # Verify tables were created
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    print(f"\nCreated tables: {[t[0] for t in tables]}")

    # Verify data was inserted
    print("\nVerifying data insertion:")

    cursor.execute("SELECT COUNT(*) FROM dosen")
    dosen_count = cursor.fetchone()[0]
    print(f"  - Dosen: {dosen_count} records")

    cursor.execute("SELECT COUNT(*) FROM mahasiswa")
    mahasiswa_count = cursor.fetchone()[0]
    print(f"  - Mahasiswa: {mahasiswa_count} records")

    cursor.execute("SELECT COUNT(*) FROM mata_kuliah")
    matkul_count = cursor.fetchone()[0]
    print(f"  - Mata Kuliah: {matkul_count} records")

    cursor.execute("SELECT COUNT(*) FROM transkrip")
    transkrip_count = cursor.fetchone()[0]
    print(f"  - Transkrip: {transkrip_count} records")

    # Test a sample query (will be used in demo)
    print("\nTesting sample query:")
    cursor.execute("""
        SELECT m.nama_mahasiswa, d.nama_dosen
        FROM mahasiswa m
        JOIN dosen d ON m.id_dospem = d.id
        WHERE m.nama_mahasiswa = 'Agus Setiawan'
    """)
    result = cursor.fetchone()
    if result:
        print(f"  ✓ Query successful: {result[0]} -> Dospem: {result[1]}")

    conn.close()
    print(f"\n✅ Database setup complete! Database file: {db_path}")
    return db_path


if __name__ == "__main__":
    setup_database()
