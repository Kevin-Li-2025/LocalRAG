#!/bin/bash

# Local RAG System Setup Script
echo "🚀 Setting up Local RAG System..."

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8+ first."
    exit 1
fi

echo "✅ Python found: $(python3 --version)"

# Install Python dependencies
echo "📦 Installing Python dependencies..."
pip3 install -r requirements.txt

# Check if Ollama is installed
if ! command -v ollama &> /dev/null; then
    echo "⚠️  Ollama not found. Installing Ollama..."
    
    # Detect OS and install Ollama
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        if command -v brew &> /dev/null; then
            brew install ollama
        else
            echo "Please install Homebrew first or download Ollama from https://ollama.ai"
            exit 1
        fi
    elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
        # Linux
        curl -fsSL https://ollama.ai/install.sh | sh
    else
        echo "Please install Ollama manually from https://ollama.ai"
        exit 1
    fi
else
    echo "✅ Ollama found: $(ollama --version)"
fi

# Start Ollama service
echo "🔄 Starting Ollama service..."
ollama serve &
sleep 3

# Download a default model
echo "📥 Downloading default model (llama2)..."
ollama pull llama2

echo "✅ Setup complete!"
echo ""
echo "🎉 To start the RAG system, run:"
echo "   streamlit run app.py"
echo ""
echo "📖 The application will open at http://localhost:8501"
echo ""
echo "💡 Recommended models to try:"
echo "   ollama pull mistral      # Fast and efficient"
echo "   ollama pull codellama    # Good for code questions"
echo "   ollama pull llama2:13b   # More capable (larger download)" 