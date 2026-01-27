@echo off
title TAstock Dashboard
cd /d "%~dp0"
echo 🚀 Starting TAstock Dashboard...
echo 📱 Browser will open automatically
echo ⏹️  Press Ctrl+C to stop the server
echo 🔗 URL: http://localhost:8501
echo.
streamlit run streamlit_app_tastock.py --server.headless=false
echo.
echo 👋 TAstock stopped. Port 8501 is now free.
echo Press any key to close...
pause >nul