#!/bin/bash

# AgenKampus Interactive Demo Runner
# This script makes it easy to run the interactive agent

echo "🎓 Starting AgenKampus Interactive Demo"
echo "========================================="
echo ""

# Check if conda environment is activated
if [[ "$CONDA_DEFAULT_ENV" != "agenkampus" ]]; then
    echo "⚠️  Warning: conda environment 'agenkampus' is not activated"
    echo "Please run: conda activate agenkampus"
    echo ""
    exit 1
fi

# Check if .env file exists
if [ ! -f "../.env" ]; then
    echo "❌ Error: .env file not found!"
    echo "Please create .env file with OPENAI_API_KEY"
    echo ""
    exit 1
fi

# Check if database exists
if [ ! -f "../database/kampus.db" ]; then
    echo "📦 Database not found. Setting up..."
    cd ../database
    python setup_database.py
    cd ../scripts
    echo ""
fi

# Check if ChromaDB is initialized
if [ ! -d "../rag/chroma_db" ]; then
    echo "📚 ChromaDB not found. Initializing RAG..."
    cd ../rag
    python tool_retriever.py > /dev/null 2>&1
    cd ../scripts
    echo "✅ RAG initialized"
    echo ""
fi

# Run the interactive agent
echo "🚀 Launching Agent Orchestrator..."
echo "=================================="
echo ""
echo "Try asking:"
echo "  - Jam berapa sekarang?"
echo "  - Siapa dosen pembimbing Agus Setiawan?"
echo "  - Mata kuliah apa yang diambil Rini Wijaya?"
echo "  - Ubah nilai Agus menjadi C (this should fail - security demo!)"
echo ""
echo "Type 'exit' to quit"
echo ""

cd ../agent
python orchestrator.py
