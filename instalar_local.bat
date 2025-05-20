@echo off
echo ====================================================
echo Instalando ambiente local para JGR Broker Importacao
echo ====================================================
echo.

cd /d "C:\Users\JOSY RIBEIRO\Downloads\JGRFUP\ImportTrackerDashboard"

echo Criando ambiente virtual Python...
python -m venv venv

echo Ativando ambiente virtual...
call venv\Scripts\activate.bat

echo Atualizando pip...
python -m pip install --upgrade pip

echo Instalando dependencias (isso pode demorar alguns minutos)...
pip install streamlit==1.31.0 --no-cache-dir
pip install pandas --no-cache-dir
pip install openpyxl --no-cache-dir
pip install xlsxwriter --no-cache-dir
pip install twilio --no-cache-dir

echo.
echo ====================================================
echo Instalacao concluida!
echo ====================================================
echo.
echo Para iniciar o aplicativo, execute o arquivo "iniciar_app_local.bat"
echo.
pause