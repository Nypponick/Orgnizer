@echo off
cd /d %~dp0
echo Iniciando JGR Broker Follow-Up...
python -m streamlit run app.py
pause