"""
Script para preparar os arquivos para deploy na Hostinger
Este script copia todos os arquivos necessários para a pasta jgr_hostinger_deploy
"""
import os
import shutil
import json
from datetime import datetime

DESTINO = 'jgr_hostinger_deploy'

# Lista de arquivos essenciais para o deploy
ARQUIVOS_ESSENCIAIS = [
    'app.py',
    'data.json',
    'users.json',
    'status_config.json',
    'data.py',
    'client_utils.py',
    'fixed_script.js',
    'new_script.js',
    'pagination.js',
    'pagination_simple.js',
    'micro_animations.js',
    'animation_styles.css',
    'mobile_styles.css',
    'resizable_columns.js',
    'html_generator.py',
    'html_export_pagination.py',
    'html_table_styles.py',
    'html_export_styles.py',
    'html_post_processor.py',
    'inline_mobile_styles.py',
    'custom_html_styles.py',
]

# Lista de pastas para copiar
PASTAS = [
    'components',
    'assets',
]

def verificar_existencia(arquivo):
    """Verifica se um arquivo existe"""
    if not os.path.exists(arquivo):
        print(f"⚠️ AVISO: Arquivo {arquivo} não encontrado!")
        return False
    return True

def copiar_arquivo(arquivo, destino):
    """Copia um arquivo para o destino"""
    if verificar_existencia(arquivo):
        destino_arquivo = os.path.join(destino, arquivo)
        # Criar diretórios se não existirem
        os.makedirs(os.path.dirname(destino_arquivo), exist_ok=True)
        shutil.copy2(arquivo, destino_arquivo)
        print(f"✓ Copiado: {arquivo}")
        return True
    return False

def copiar_pasta(pasta, destino):
    """Copia uma pasta inteira para o destino"""
    if os.path.exists(pasta) and os.path.isdir(pasta):
        destino_pasta = os.path.join(destino, pasta)
        if os.path.exists(destino_pasta):
            shutil.rmtree(destino_pasta)
        shutil.copytree(pasta, destino_pasta)
        print(f"✓ Copiada pasta: {pasta}/")
        return True
    else:
        print(f"⚠️ AVISO: Pasta {pasta} não encontrada!")
        return False

def criar_arquivo_info():
    """Cria um arquivo de informações sobre o deploy"""
    info = {
        "data_deploy": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
        "arquivos_incluidos": [],
        "pastas_incluidas": []
    }
    
    for arquivo in ARQUIVOS_ESSENCIAIS:
        if verificar_existencia(arquivo):
            info["arquivos_incluidos"].append(arquivo)
    
    for pasta in PASTAS:
        if os.path.exists(pasta) and os.path.isdir(pasta):
            info["pastas_incluidas"].append(pasta)
    
    # Salvar arquivo de informações
    with open(os.path.join(DESTINO, 'info_deploy.json'), 'w', encoding='utf-8') as f:
        json.dump(info, f, ensure_ascii=False, indent=4)
    
    print(f"✓ Criado arquivo de informações: info_deploy.json")

def preparar_deploy():
    """Prepara todos os arquivos para deploy"""
    print("🚀 Iniciando preparação para deploy na Hostinger...")
    
    # Verificar se a pasta de destino existe
    if not os.path.exists(DESTINO):
        os.makedirs(DESTINO)
        print(f"✓ Criada pasta: {DESTINO}/")
    
    # Copiar arquivos essenciais
    for arquivo in ARQUIVOS_ESSENCIAIS:
        copiar_arquivo(arquivo, DESTINO)
    
    # Copiar pastas
    for pasta in PASTAS:
        copiar_pasta(pasta, DESTINO)
    
    # Criar arquivo de informações
    criar_arquivo_info()
    
    print("\n✅ Preparação concluída! Os arquivos estão prontos para upload via FileZilla.")
    print(f"📁 Caminho: {os.path.abspath(DESTINO)}")
    print("\nDica: No servidor da Hostinger, execute 'docker-compose up -d' para iniciar a aplicação.")

if __name__ == "__main__":
    preparar_deploy()