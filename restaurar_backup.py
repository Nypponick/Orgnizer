"""
Script para restaurar os dados originais a partir do backup mais recente.
Isso removerá os processos gerados automaticamente.
"""

import os
import json
import glob
from datetime import datetime

def obter_backup_mais_recente():
    """Encontra o arquivo de backup mais recente"""
    arquivos_backup = glob.glob("data_backup_*.json")
    
    if not arquivos_backup:
        print("Nenhum arquivo de backup encontrado!")
        return None
    
    # Ordenar por data de modificação (mais recente primeiro)
    arquivos_backup.sort(key=lambda x: os.path.getmtime(x), reverse=True)
    return arquivos_backup[0]

def restaurar_dados():
    """Restaura os dados do backup mais recente"""
    backup_file = obter_backup_mais_recente()
    
    if not backup_file:
        return False
    
    try:
        # Ler dados do backup
        with open(backup_file, 'r') as f:
            dados_backup = json.load(f)
        
        # Criar backup do arquivo atual (por precaução)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        current_backup = f"data_pre_restauracao_{timestamp}.json"
        
        with open("data.json", 'r') as atual:
            with open(current_backup, 'w') as backup:
                backup.write(atual.read())
                print(f"Backup do estado atual criado em {current_backup}")
        
        # Restaurar dados do backup
        with open("data.json", 'w') as f:
            json.dump(dados_backup, f, indent=2)
        
        print(f"Dados restaurados com sucesso a partir de {backup_file}")
        
        # Exibir informações sobre processos
        processos = dados_backup.get("processes", [])
        print(f"Restaurados {len(processos)} processos")
        
        # Contar tipos de processos
        importacao = sum(1 for p in processos if p.get('type') == 'importacao')
        exportacao = sum(1 for p in processos if p.get('type') == 'exportacao')
        print(f"- {importacao} processos de importação")
        print(f"- {exportacao} processos de exportação")
        
        return True
    except Exception as e:
        print(f"Erro ao restaurar dados: {str(e)}")
        return False

if __name__ == "__main__":
    restaurar_dados()