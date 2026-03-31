@echo off
echo ==============================================
echo       Starting Coach Siham AI Writer...
echo ==============================================
echo.
echo Installing requirements...
pip install -r requirements.txt
echo.
echo Launching the application...
streamlit run app.py
pause
