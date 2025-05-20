@echo off
echo ====================================================
echo Instalando sem compilacao (somente binarios pre-compilados)
echo ====================================================
echo.

cd /d "C:\Users\JOSY RIBEIRO\Downloads\JGRFUP\ImportTrackerDashboard"

echo Criando ambiente virtual Python...
python -m venv venv

echo Ativando ambiente virtual...
call venv\Scripts\activate.bat

echo Atualizando pip...
python -m pip install --upgrade pip

echo Instalando dependencias (usando apenas pacotes pre-compilados)...
pip install --only-binary=:all: --no-cache-dir streamlit==1.31.0
pip install --only-binary=:all: --no-cache-dir pandas==2.1.4
pip install --only-binary=:all: --no-cache-dir openpyxl==3.1.2
pip install --only-binary=:all: --no-cache-dir xlsxwriter==3.1.2
pip install --only-binary=:all: --no-cache-dir twilio==8.5.0

echo.
echo ====================================================
echo Instalacao concluida!
echo ====================================================
echo.
echo Para iniciar o aplicativo, execute o arquivo "iniciar_app_local.bat"
echo.
pause