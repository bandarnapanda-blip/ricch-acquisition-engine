#!/bin/bash

# Ri2ch Digital - AWS VPS Lead Engine Setup Script
# Target OS: Ubuntu 22.04 LTS (AWS EC2 / Lightsail)

echo "🚀 Starting Ri2ch Digital Lead Engine Setup..."

# 1. Update system and install base dependencies
sudo apt-get update && sudo apt-get upgrade -y
sudo apt-get install -y python3-pip python3-venv git curl nodejs npm

# 2. Install PM2 globally (Process Manager)
sudo npm install -g pm2

# 3. Create project directory and virtual environment
mkdir -p ~/ri2ch-digital
cd ~/ri2ch-digital
python3 -m venv venv
source venv/bin/activate

# 4. Install Python requirements
# Note: requirements.txt should exist in the project root
pip install --upgrade pip
pip install requests beautifulsoup4 playwright python-dotenv openai pandas streamlit flask gunicorn

# 5. Install Playwright Browsers & Linux Dependencies
playwright install chromium
playwright install-deps

# 6. Success message
echo "✅ Setup Complete!"
echo "Next steps:"
echo "1. Upload your .env file to ~/ri2ch-digital/"
echo "2. Start the engines using PM2:"
echo "   pm2 start 'venv/bin/python3 find_leads.py' --name the-hound"
echo "   pm2 start 'venv/bin/python3 auto_submit.py' --name the-ghost"
echo "   pm2 start 'venv/bin/python3 inbox_monitor.py' --name the-monitor"
echo "   pm2 start 'venv/bin/python3 paystack_webhook.py' --name success-bot"
