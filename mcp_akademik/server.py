"""
MCP Server: Akademik
Provides academic data access tools for the AgenKampus demo.

This server demonstrates safe database access through MCP protocol.
The AI agent NEVER directly accesses the database - it can only call
these predefined, safe tools.

Tools:
- get_dosen_pembimbing(nama_mahasiswa): Get student's academic advisor
- get_mata_kuliah_mahasiswa(nama_mahasiswa): Get student's course list with grades

Usage:
    python server.py
"""

from fastmcp import FastMCP
from database import get_db

# Initialize FastMCP server
mcp = FastMCP("Akademik")

# Get database connection instance
db = get_db()


@mcp.tool()
def get_dosen_pembimbing(nama_mahasiswa: str) -> str:
    """
    Find the academic advisor (dosen pembimbing) of a student.

    This tool queries the database to find which lecturer is assigned
    as the academic advisor for a given student. It performs a JOIN
    operation between the mahasiswa (student) and dosen (lecturer) tables.

    Args:
        nama_mahasiswa (str): Full name of the student (case-sensitive)

    Returns:
        str: Advisor's name or error message if student not found

    Examples:
        >>> get_dosen_pembimbing("Agus Setiawan")
        "Dosen pembimbing Agus Setiawan: Dr. Budi Santoso"

        >>> get_dosen_pembimbing("Rini Wijaya")
        "Dosen pembimbing Rini Wijaya: Prof. Siti Aminah"

        >>> get_dosen_pembimbing("Unknown Student")
        "Mahasiswa 'Unknown Student' tidak ditemukan dalam database"

    Security:
        - Uses parameterized queries (prevents SQL injection)
        - Read-only access (SELECT only, no INSERT/UPDATE/DELETE)
        - No direct database access by AI
    """
    # SQL query with JOIN to get advisor name
    query = """
        SELECT d.nama_dosen
        FROM mahasiswa m
        JOIN dosen d ON m.id_dospem = d.id
        WHERE m.nama_mahasiswa = ?
    """

    try:
        # Execute query with parameterized binding for security
        result = db.execute_query(query, (nama_mahasiswa,), fetch_one=True)

        if result:
            dosen_name = result[0]
            return f"Dosen pembimbing {nama_mahasiswa}: {dosen_name}"
        else:
            return f"Mahasiswa '{nama_mahasiswa}' tidak ditemukan dalam database"

    except Exception as e:
        return f"Error saat mencari dosen pembimbing: {str(e)}"


@mcp.tool()
def get_mata_kuliah_mahasiswa(nama_mahasiswa: str) -> str:
    """
    Get the list of all courses taken by a student with their grades.

    This tool performs a complex 3-table JOIN operation to retrieve
    a student's complete transcript: courses taken and grades received.

    Args:
        nama_mahasiswa (str): Full name of the student (case-sensitive)

    Returns:
        str: Formatted list of courses and grades, or error message

    Examples:
        >>> get_mata_kuliah_mahasiswa("Agus Setiawan")
        "Mata kuliah Agus Setiawan: Kecerdasan Buatan (A), Basis Data Lanjut (B)"

        >>> get_mata_kuliah_mahasiswa("Rini Wijaya")
        "Mata kuliah Rini Wijaya: Kecerdasan Buatan (A), Pemrograman Web (A)"

        >>> get_mata_kuliah_mahasiswa("Unknown Student")
        "Mahasiswa 'Unknown Student' tidak ditemukan dalam database"

    Database Schema:
        Joins: mahasiswa → transkrip → mata_kuliah
        Returns: course names + letter grades

    Security:
        - Uses parameterized queries (prevents SQL injection)
        - Read-only access (SELECT only)
        - No direct database access by AI
    """
    # Complex SQL query with 3-table JOIN
    query = """
        SELECT mk.nama_matkul, t.nilai_huruf
        FROM mahasiswa m
        JOIN transkrip t ON m.id = t.id_mahasiswa
        JOIN mata_kuliah mk ON t.id_matkul = mk.id
        WHERE m.nama_mahasiswa = ?
        ORDER BY mk.nama_matkul
    """

    try:
        # Execute query with parameterized binding for security
        results = db.execute_query(query, (nama_mahasiswa,))

        if results:
            # Format results as "Course Name (Grade), Course Name (Grade)"
            courses = [f"{course} ({grade})" for course, grade in results]
            courses_str = ", ".join(courses)
            return f"Mata kuliah {nama_mahasiswa}: {courses_str}"
        else:
            return f"Mahasiswa '{nama_mahasiswa}' tidak ditemukan dalam database"

    except Exception as e:
        return f"Error saat mengambil mata kuliah: {str(e)}"


@mcp.tool()
def list_all_students() -> str:
    """
    Get a list of all students in the database.

    This helper tool allows the agent to discover which students exist
    in the system. Useful for exploring available data.

    Returns:
        str: Comma-separated list of student names

    Example:
        >>> list_all_students()
        "Mahasiswa terdaftar: Agus Setiawan, Rini Wijaya"
    """
    query = "SELECT nama_mahasiswa FROM mahasiswa ORDER BY nama_mahasiswa"

    try:
        results = db.execute_query(query)

        if results:
            students = [row[0] for row in results]
            students_str = ", ".join(students)
            return f"Mahasiswa terdaftar: {students_str}"
        else:
            return "Tidak ada mahasiswa dalam database"

    except Exception as e:
        return f"Error saat mengambil daftar mahasiswa: {str(e)}"


if __name__ == "__main__":
    # Test database connection
    print("🔍 Testing database connection...")
    if db.test_connection():
        print("✅ Database connection successful!")
    else:
        print("❌ Database connection failed!")
        print("Please run database/setup_database.py first")
        exit(1)

    # Display available tools
    print("\n🚀 Starting MCP Server: Akademik")
    print("Available tools:")
    print("  - get_dosen_pembimbing(nama_mahasiswa): Find student's advisor")
    print("  - get_mata_kuliah_mahasiswa(nama_mahasiswa): Get student's courses")
    print("  - list_all_students(): List all registered students")
    print(f"\nDatabase: {db.db_path}")
    print("\nServer running...")

    # Start the FastMCP server
    mcp.run()
