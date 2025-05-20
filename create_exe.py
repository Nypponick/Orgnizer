"""
Script simplificado para criar o executável do JGR Broker
"""

import os
import shutil
import subprocess
import sys
import time


def create_exe():
    """Script simplificado para criar o executável do JGR Broker"""
    print("Iniciando criação do executável...")
    
    # Verificar se o PyInstaller está instalado
    try:
        import PyInstaller
    except ImportError:
        print("Instalando PyInstaller...")
        subprocess.run([sys.executable, "-m", "pip", "install", "pyinstaller"], check=True)
    
    # Criar o arquivo .spec necessário para o PyInstaller
    spec_content = """
# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['app.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('.streamlit', '.streamlit'),
        ('assets', 'assets'),
        ('components', 'components'),
        ('data.json', '.'),
        ('users.json', '.'),
        ('html_exports', 'html_exports'),
    ],
    hiddenimports=[
        'streamlit',
        'pandas',
        'openpyxl',
        'xlsxwriter',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='JGRBrokerImportacao',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='generated-icon.png',
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='JGRBrokerImportacao',
)
    """
    
    # Criar o arquivo .spec
    with open("JGRBrokerImportacao.spec", "w") as spec_file:
        spec_file.write(spec_content)
    
    # Criar o ícone se não existir
    if not os.path.exists("generated-icon.png"):
        # Usar um ícone padrão ou criar um básico
        with open("generated-icon.png", "wb") as icon_file:
            icon_file.write(b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x10\x00\x00\x00\x10\x08\x06\x00\x00\x00\x1f\xf3\xffa\x00\x00\x00\x04sBIT\x08\x08\x08\x08|\x08d\x88\x00\x00\x00\tpHYs\x00\x00\x0e\xc4\x00\x00\x0e\xc4\x01\x95+\x0e\x1b\x00\x00\x00\x19tEXtSoftware\x00www.inkscape.org\x9b\xee<\x1a\x00\x00\x01\x14IDAT8\x8d\xa5\x93\xbdJ\x031\x14\x86\xbf\x93\x1b\'O\'\xc1\xc1A\x1c\xc4\x17\x10\xf7\x16\x11\xab\x83\x83\xa3C\xa7\xbaY\x9c|\x00\x97\x16\x87\x0e\xdd\\\xc4]\xf0\x01\\\\\x04\xf1\x05\x04\'\x87\xba\xb8\t\xc1.\xdeK\xee\x1d\xc4\xe9\xd7\x84\xef\x07\x92\x93\xfe\xe1\x07\t\xe0q\x89\x99\xcd,U;I\x07\xdeu\x1c\xfeJ\x92\xa4\xe8\xee\xb7\x00\x92F\xe0\xd5\xdd\x87\xcd\xf3\xe64\x9e\xcd\xbc\n\xa0\xdd\x9a;@\x92\x04N\x80n\x08\xe1\xa3"\xc9f\xb6\x0f\\\x86\x10\xfa\xcbl\x03\x80\xa4\x1ep\x0b\x8c\xdd=\xd4\x80L\x02\xdd$I\xee#0\x98\xd9\x19p\x05\x0c\x80\xa3\xa5\xa7\x13\xe0\x01H\x81\xddj!\xc0\xcc\x8e\x81\x1e0t\xf7\x9b\x05\x93\x06\xf0\x0c\xec\x00\x07\xee>Z\x16\x0f\x01\x9a\xc0+\xb0\x11\xc3\xee\xfe\xb1\x1a\x88\xeb\xdc\xddW\x9a\xe7\x00\x97q?\xe8\xa9\xde[\xf4\xdd\xfdf\x95\xe2\x17@\x8e\x99]\x00\xe7\xd5\xa3\xfc\x1b\xd0\xa8\xce\x94\xf2SV\xd7\xddOk\x81\xb8\xbe\xc7\xf6G\xbfU\x0fy\xb1\xb6\xcd,\x8dN\xdd\x06\x9c\x02\xb9\xa4\xafY\xda\xca\xe21\xe7\x9f\xfa\x06/\xc4D\xc7\xc3\x88\xe0T\x00\x00\x00\x00IEND\xaeB`\x82')
    
    print("Criando executável com PyInstaller...")
    subprocess.run(["pyinstaller", "JGRBrokerImportacao.spec"], check=True)
    
    print("\nExecutável criado com sucesso!")
    print("Você pode encontrar o executável na pasta 'dist/JGRBrokerImportacao'")
    print("Para iniciar o programa, execute o arquivo 'JGRBrokerImportacao.exe' dentro dessa pasta")
    
    # Criar arquivo .bat para iniciar o executável
    bat_content = """@echo off
echo Iniciando JGR Broker Importacao...
start dist\\JGRBrokerImportacao\\JGRBrokerImportacao.exe
"""
    
    with open("iniciar_executavel.bat", "w") as bat_file:
        bat_file.write(bat_content)
    
    print("\nFoi criado também o arquivo 'iniciar_executavel.bat' para facilitar a execução")
    print("Pressione Enter para sair...")
    input()


if __name__ == "__main__":
    create_exe()