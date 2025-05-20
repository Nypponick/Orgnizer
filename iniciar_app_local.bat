@echo off
echo ====================================================
echo Iniciando JGR Broker Importacao
echo ====================================================
echo.

cd /d "C:\Users\JOSY RIBEIRO\Downloads\JGRFUP\ImportTrackerDashboard"

echo Ativando ambiente virtual...
call venv\Scripts\activate.bat

echo Iniciando aplicativo Streamlit...
streamlit run app.py

pause