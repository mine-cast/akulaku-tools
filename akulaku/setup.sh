#!/bin/bash
# Quick setup script for Akulaku Dropship

echo "🚀 Setting up Akulaku Dropship..."
echo ""

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 not found. Please install Python 3.8+"
    exit 1
fi

echo "✓ Python3 found: $(python3 --version)"

# Install dependencies
echo ""
echo "📦 Installing dependencies..."
pip install -r requirements.txt

# Setup environment
if [ ! -f config/.env ]; then
    echo ""
    echo "⚙️ Creating .env file..."
    cp config/.env.example config/.env
    echo "✓ .env file created"
    echo ""
    echo "⚠️  IMPORTANT: Edit config/.env with your credentials:"
    echo "    - AKULAKU_APP_KEY"
    echo "    - AKULAKU_APP_SECRET"
    echo ""
else
    echo "✓ .env file exists"
fi

# Create necessary directories
echo ""
echo "📁 Creating directories..."
mkdir -p data logs
echo "✓ Directories created"

# Test API connection
echo ""
echo "🔍 Testing API connection..."
python3 -c "
import sys
sys.path.insert(0, '.')
from src.akulaku_utils import setup_credentials
if setup_credentials():
    print('✓ API credentials configured')
else:
    print('⚠️  API credentials not set. Edit config/.env')
"

echo ""
echo "✅ Setup complete!"
echo ""
echo "📖 Next steps:"
echo "   1. Edit config/.env with your Akulaku API credentials"
echo "   2. Run: python3 api/main.py"
echo "   3. Open: http://localhost:8000"
echo ""
echo "📚 Documentation:"
echo "   - README.md - Overview"
echo "   - PLAN.md - Development roadmap"
echo "   - INSTRUCTIONS.md - Step-by-step guide"
echo ""
