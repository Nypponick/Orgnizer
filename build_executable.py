import os
import sys
import shutil
import subprocess
import json

def create_executable():
    print("Preparando para criar executável do aplicativo JGR Broker Importação...")
    
    # Criar diretório para o executável se não existir
    if not os.path.exists("dist"):
        os.makedirs("dist")
    
    # Verificar se tem o PyInstaller instalado
    try:
        import PyInstaller
        print("PyInstaller encontrado, versão:", PyInstaller.__version__)
    except ImportError:
        print("PyInstaller não encontrado. Por favor, instale-o primeiro com 'pip install pyinstaller'")
        return
    
    # Copiar dados necessários para a pasta dist
    data_files = ["data.json", "users.json", "shared_links.json"]
    for file in data_files:
        if os.path.exists(file):
            shutil.copy(file, os.path.join("dist", file))
            print(f"Arquivo {file} copiado para dist/")
    
    # Criar pastas necessárias para a operação do aplicativo
    for folder in ["html_exports", "assets"]:
        dist_folder = os.path.join("dist", folder)
        if not os.path.exists(dist_folder):
            os.makedirs(dist_folder)
            print(f"Pasta {folder} criada em dist/")
    
    # Preparar argumentos para o PyInstaller
    pyinstaller_args = [
        "pyinstaller",
        "--name=JGRBrokerImportacao",
        "--onefile",  # Cria um único arquivo executável
        "--windowed",  # Oculta a janela do console
        "--icon=generated-icon.png" if os.path.exists("generated-icon.png") else "",
        "--add-data=data.json:.",
        "--add-data=users.json:.",
        "--add-data=shared_links.json:.",
        "--add-data=components:components",
        "--hidden-import=pandas",
        "--hidden-import=streamlit",
        "--hidden-import=xlsxwriter",
        "app.py"
    ]
    
    # Remover argumentos vazios
    pyinstaller_args = [arg for arg in pyinstaller_args if arg]
    
    # Executar PyInstaller
    print("Executando PyInstaller com os seguintes argumentos:")
    print(" ".join(pyinstaller_args))
    
    try:
        subprocess.run(pyinstaller_args, check=True)
        
        # Criar arquivo de configuração para o StreamLit
        streamlit_config_dir = os.path.join("dist", ".streamlit")
        if not os.path.exists(streamlit_config_dir):
            os.makedirs(streamlit_config_dir)
        
        # Criar arquivo de configuração do Streamlit
        config_path = os.path.join(streamlit_config_dir, "config.toml")
        with open(config_path, "w") as f:
            f.write("""
[server]
headless = true
port = 5000
enableCORS = false
enableXsrfProtection = false
            """)
        
        print(f"Arquivo de configuração Streamlit criado em {config_path}")
        
        # Criar um arquivo batch para iniciar o aplicativo no Windows
        with open(os.path.join("dist", "Start_JGR_Broker.bat"), "w") as f:
            f.write('@echo off\ncd /d "%~dp0"\nstart "" "JGRBrokerImportacao.exe"\nstart http://localhost:5000\n')
        
        print("Executável criado com sucesso! Você pode encontrá-lo em dist/JGRBrokerImportacao.exe")
        print("Para iniciar o aplicativo, execute o arquivo 'Start_JGR_Broker.bat' na pasta 'dist'")
    
    except subprocess.CalledProcessError as e:
        print(f"Erro ao criar executável: {e}")
        return

if __name__ == "__main__":
    create_executable()