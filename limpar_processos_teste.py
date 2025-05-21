"""
Script para remover os processos de teste gerados anteriormente
"""
import os
import json
import datetime
from data import load_data, save_data

def fazer_backup_dados():
    """Fazer backup dos dados atuais antes de removê-los"""
    data = load_data()
    
    # Criar nome de arquivo com timestamp
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_filename = f"data_backup_antes_limpeza_{timestamp}.json"
    
    # Garantir que o diretório de backup exista
    backup_dir = "backups"
    if not os.path.exists(backup_dir):
        os.makedirs(backup_dir)
    
    # Salvar backup
    backup_path = os.path.join(backup_dir, backup_filename)
    with open(backup_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"Backup criado em: {backup_path}")
    return backup_path

def remover_processos_teste():
    """Remover processos de teste gerados pelo gerador automático"""
    # Primeiro, fazer backup
    backup_path = fazer_backup_dados()
    
    # Carregar dados
    data = load_data()
    
    # Contar processos antes
    total_processos_antes = len(data.get('processes', []))
    
    # Identificar processos para manter (os processos originais)
    # Assumimos que os processos ID 1000 e acima são os gerados automaticamente
    processos_originais = [p for p in data.get('processes', []) 
                          if not (p.get('id', '').isdigit() and int(p.get('id', 0)) >= 1000)]
    
    # Atualizar dados
    data['processes'] = processos_originais
    
    # Salvar dados
    save_data(data)
    
    # Contar processos depois
    total_processos_depois = len(data.get('processes', []))
    processos_removidos = total_processos_antes - total_processos_depois
    
    print(f"Limpeza concluída!")
    print(f"Total de processos antes: {total_processos_antes}")
    print(f"Total de processos depois: {total_processos_depois}")
    print(f"Processos removidos: {processos_removidos}")
    print(f"Backup salvo em: {backup_path}")

if __name__ == "__main__":
    remover_processos_teste()