#!/bin/bash
# Setup Script for KB Update System
# This script helps you set up and test the KB update system

set -e

echo "=" | head -c 70
echo ""
echo "🚀 Knowledge Base Update System - Setup"
echo "=" | head -c 70
echo ""

# Check if API key is set
if [ -z "$OPENAI_API_KEY" ]; then
    echo "⚠️  OPENAI_API_KEY not set"
    echo ""
    echo "Please set your API key:"
    echo "   export OPENAI_API_KEY='your-api-key-here'"
    echo ""
    echo "Or add it to your ~/.zshrc or ~/.bashrc:"
    echo "   echo 'export OPENAI_API_KEY=\"your-api-key-here\"' >> ~/.zshrc"
    echo "   source ~/.zshrc"
    echo ""
    read -p "Do you want to set it now? (y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        read -p "Enter your OpenAI API key: " api_key
        export OPENAI_API_KEY="$api_key"
        echo "✅ API key set for this session"
        echo "💡 To make it permanent, add it to your shell config file"
    else
        echo "❌ Cannot proceed without API key"
        exit 1
    fi
else
    echo "✅ OPENAI_API_KEY is set"
fi

echo ""
echo "=" | head -c 70
echo ""
echo "📊 Step 1: Checking System Status"
echo "=" | head -c 70
echo ""

# Check dependencies
echo "Checking dependencies..."
python3 -c "import openai, loguru, schedule" 2>/dev/null && echo "✅ All dependencies installed" || {
    echo "❌ Missing dependencies. Installing..."
    pip install openai loguru schedule
}

echo ""
echo "=" | head -c 70
echo ""
echo "📊 Step 2: Checking KB Update Status"
echo "=" | head -c 70
echo ""

python3 kb_update_optimizer.py --stats

echo ""
echo "=" | head -c 70
echo ""
echo "📊 Step 3: Testing Training Data Optimizer"
echo "=" | head -c 70
echo ""

python3 training_data_optimizer.py --stats

echo ""
echo "=" | head -c 70
echo ""
echo "🎯 Next Steps"
echo "=" | head -c 70
echo ""

echo "1. Run your first optimized update:"
echo "   python3 kb_update_optimizer.py --tier all"
echo ""
echo "2. Test training data processing:"
echo "   python3 training_data_optimizer.py --process"
echo ""
echo "3. Set up automated scheduling:"
echo "   python3 kb_auto_scheduler.py --daemon"
echo ""
echo "   Or use cron (recommended for production):"
echo "   crontab -e"
echo "   # Add the schedules from KB_UPDATE_QUICKSTART.md"
echo ""

read -p "Do you want to run the first update now? (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo ""
    echo "🔄 Running first optimized update..."
    python3 kb_update_optimizer.py --tier all
    echo ""
    echo "✅ Update complete!"
fi

echo ""
echo "=" | head -c 70
echo ""
echo "✅ Setup Complete!"
echo "=" | head -c 70
echo ""
echo "Your KB update system is ready to use."
echo "See KB_UPDATE_QUICKSTART.md for more details."
