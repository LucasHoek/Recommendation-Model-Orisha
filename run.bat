@echo off
echo Starting Orisha Sales Agent (npm) in a new window...
start "" cmd /k "cd /d Orisha-Sales-Agent && npm run dev"

echo Starting Flask in this window...
call conda activate orisha-recommendation-model
python app.py
