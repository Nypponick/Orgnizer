"""
Script para gerar dados de teste para o sistema JGR Broker
Cria 100 processos fictícios com dados aleatórios
"""

import json
import random
from datetime import datetime, timedelta
import os

def gerar_data_aleatoria(inicio, fim):
    """Gera uma data aleatória entre duas datas"""
    delta = fim - inicio
    dias_aleatorios = random.randint(0, delta.days)
    return (inicio + timedelta(days=dias_aleatorios)).strftime("%d/%m/%Y")

def calcular_vencimento(data_inicio, dias):
    """Calcular data de vencimento a partir de data de início e dias"""
    if not data_inicio:
        return ""
    try:
        inicio = datetime.strptime(data_inicio, "%d/%m/%Y")
        return (inicio + timedelta(days=dias)).strftime("%d/%m/%Y")
    except:
        return ""

def calcular_dias_armazenados(entry_date):
    """Calcular dias de armazenamento"""
    if not entry_date:
        return 0
    try:
        entry = datetime.strptime(entry_date, "%d/%m/%Y")
        hoje = datetime.now()
        return (hoje - entry).days
    except:
        return 0

def gerar_processo_aleatorio(id_processo):
    """Gera um processo com dados aleatórios"""
    # Status possíveis
    status_opcoes = [
        "Em andamento", 
        "Pendente", 
        "Liberado", 
        "Chegada do navio alterada", 
        "Aguardando documentos",
        "Em desembaraço",
        "BL liberado",
        "Aguardando chegada",
        "Nacionalizado",
        "Novo Processo",
        "Concluído"
    ]
    
    # Tipos de processo
    tipo_processo = random.choice(["importacao", "exportacao"])
    
    # Origem/destino
    paises = ["CHINA", "EUA", "ALEMANHA", "JAPÃO", "COREIA DO SUL", "ÍNDIA", "VIETNÃ", "TAILÂNDIA", "ITÁLIA", "ESPANHA"]
    
    # Produtos
    produtos = [
        "FLONEX 9004 S", "MÁQUINAS CNC", "PEÇAS AUTOMOTIVAS", "EQUIPAMENTOS MÉDICOS",
        "PLÁSTICOS", "ELETRÔNICOS", "TECIDOS", "AÇO", "QUÍMICOS", "ALIMENTOS",
        "EQUIPAMENTOS INDUSTRIAIS", "PRODUTOS FARMACÊUTICOS", "MATERIAIS DE CONSTRUÇÃO"
    ]
    
    # Portos
    portos = ["SANTOS", "ITAJAÍ", "PARANAGUÁ", "RIO DE JANEIRO", "VITÓRIA", "ITAGUAÍ", "SUAPE", "MANAUS"]
    
    # Terminais
    terminais = ["SANTOS BRASIL", "DPW SANTOS", "BTP", "EMBRAPORT", "TCP", "PORTONAVE", "ITAPOÁ"]
    
    # Datas
    data_inicio = datetime.now() - timedelta(days=180)
    data_fim = datetime.now() + timedelta(days=90)
    
    # Gerar datas aleatórias
    eta = gerar_data_aleatoria(data_inicio, data_fim)
    
    # Free time
    free_time_dias = random.randint(7, 30)
    free_time_expiry = calcular_vencimento(eta, free_time_dias)
    
    # Entrada no porto
    port_entry_date = gerar_data_aleatoria(data_inicio, datetime.now())
    
    # Período atual
    dias_por_periodo = random.randint(7, 15)
    current_period_start = port_entry_date
    current_period_expiry = calcular_vencimento(current_period_start, dias_por_periodo)
    
    # Calcular dias armazenados
    storage_days = calcular_dias_armazenados(port_entry_date)
    
    # Referência
    ref = f"REF-{random.randint(1000, 9999)}/{datetime.now().year}"
    
    return {
        "id": f"{id_processo:08d}",
        "status": random.choice(status_opcoes),
        "type": tipo_processo,
        "ref": ref,
        "po": f"PO-{random.randint(10000, 99999)}",
        "origin": random.choice(paises),
        "product": random.choice(produtos),
        "eta": eta,
        "free_time": free_time_dias,
        "free_time_expiry": free_time_expiry,
        "empty_return": calcular_vencimento(eta, random.randint(15, 45)),
        "map": f"MAP-{random.randint(1000, 9999)}",
        "invoice_number": f"INV-{random.randint(10000, 99999)}",
        "port_entry_date": port_entry_date,
        "current_period_start": current_period_start,
        "current_period_expiry": current_period_expiry,
        "storage_days": storage_days,
        "terminal": random.choice(terminais),
        "events": [
            {
                "id": 1,
                "date": gerar_data_aleatoria(data_inicio, datetime.now()),
                "description": f"Processo criado - {ref}",
                "user": "admin"
            },
            {
                "id": 2,
                "date": gerar_data_aleatoria(data_inicio, datetime.now()),
                "description": f"Documentos recebidos - {ref}",
                "user": "admin"
            }
        ],
        "container": f"CONT{random.randint(1000000, 9999999)}",
        "ship": f"NAVIO {random.choice(['STAR', 'MAERSK', 'MSC', 'COSCO', 'HAPAG'])} {random.randint(100, 999)}",
        "agent": f"AGENTE {random.choice(['INTERNACIONAL', 'MARÍTIMO', 'LOGÍSTICO'])} {random.choice(['A', 'B', 'C', 'D', 'E'])}",
        "bl_number": f"BL-{random.randint(100000, 999999)}",
        "original_documents": random.choice([True, False]),
        "archived": False
    }

def gerar_dados_teste(quantidade=100):
    """Gera a quantidade especificada de processos de teste"""
    # Verificar se já existe arquivo de dados
    if os.path.exists("data.json"):
        with open("data.json", "r") as f:
            try:
                dados = json.load(f)
                processos_existentes = dados.get("processes", [])
                print(f"Arquivo data.json existente com {len(processos_existentes)} processos")
            except:
                processos_existentes = []
                print("Erro ao carregar arquivo data.json existente")
    else:
        processos_existentes = []
        print("Arquivo data.json não encontrado")
    
    # Criar novos processos
    novos_processos = []
    for i in range(quantidade):
        novos_processos.append(gerar_processo_aleatorio(20250000 + i))
    
    # Combinar processos existentes com novos
    todos_processos = processos_existentes + novos_processos
    
    # Criar backup do arquivo existente (se houver)
    if os.path.exists("data.json"):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_filename = f"data_backup_{timestamp}.json"
        with open(backup_filename, "w") as f:
            with open("data.json", "r") as original:
                f.write(original.read())
            print(f"Backup criado em {backup_filename}")
    
    # Salvar novos dados
    dados = {"processes": todos_processos}
    with open("data.json", "w") as f:
        json.dump(dados, f, indent=2)
    
    print(f"Total de {len(todos_processos)} processos salvos em data.json")

if __name__ == "__main__":
    gerar_dados_teste(100)
    print("Dados de teste gerados com sucesso!")