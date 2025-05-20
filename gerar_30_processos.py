"""
Script para gerar 30 processos de teste (15 importação e 15 exportação) para o sistema JGR Broker
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

def gerar_processo_importacao(id_processo):
    """Gera um processo de importação com dados completos"""
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
        "type": "importacao",
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
                "description": f"Processo importação criado - {ref}",
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
        "days_per_period": dias_por_periodo,
        "archived": False
    }

def gerar_processo_exportacao(id_processo):
    """Gera um processo de exportação com dados completos"""
    # Status possíveis
    status_opcoes = [
        "Em andamento", 
        "Pendente", 
        "Liberado", 
        "Embarque agendado", 
        "Aguardando documentos",
        "Em desembaraço",
        "Documentos enviados",
        "Aguardando embarque",
        "Embarcado",
        "Novo Processo",
        "Concluído"
    ]
    
    # Origem/destino
    paises = ["CHINA", "EUA", "ALEMANHA", "JAPÃO", "COREIA DO SUL", "ÍNDIA", "VIETNÃ", "TAILÂNDIA", "ITÁLIA", "ESPANHA"]
    
    # Produtos
    produtos = [
        "CAFÉ", "CARNE BOVINA", "SOJA", "MINÉRIO DE FERRO", "AÇÚCAR",
        "AUTOMÓVEIS", "CALÇADOS", "EQUIPAMENTOS AGRÍCOLAS", "CELULOSE", "ALGODÃO",
        "AERONAVES", "QUÍMICOS INDUSTRIAIS", "MILHO"
    ]
    
    # Terminais
    terminais_maritimos = ["SANTOS BRASIL", "DPW SANTOS", "BTP", "EMBRAPORT", "TCP", "PORTONAVE", "ITAPOÁ"]
    terminais_rodoviarios = ["EADI SANTO ANDRÉ", "CLIA CAMPINAS", "PORTO SECO BARUERI", "TERMINAL ROCHA", "CLIA GUARULHOS"]
    
    # Datas
    data_inicio = datetime.now() - timedelta(days=180)
    data_fim = datetime.now() + timedelta(days=90)
    
    # Gerar datas aleatórias
    etd = gerar_data_aleatoria(data_inicio, data_fim)
    due_date = gerar_data_aleatoria(data_inicio, datetime.now())
    knowledge_date = gerar_data_aleatoria(data_inicio, datetime.now())
    endorsement_date = gerar_data_aleatoria(data_inicio, datetime.now())
    shipping_date = gerar_data_aleatoria(datetime.now(), data_fim)
    
    # Deadlines
    cargo_deadline = calcular_vencimento(shipping_date, -random.randint(3, 7))
    draft_deadline = calcular_vencimento(shipping_date, -random.randint(7, 14))
    
    # Referência
    ref = f"EXP-{random.randint(1000, 9999)}/{datetime.now().year}"
    
    # Tipo de exportação (marítima/rodoviária)
    export_type = random.choice(["maritima", "rodoviaria"])
    
    process = {
        "id": f"{id_processo:08d}",
        "status": random.choice(status_opcoes),
        "type": "exportacao",
        "ref": ref,
        "product": random.choice(produtos),
        "export_type": export_type,
        "importer": f"IMPORTADOR {random.choice(['A', 'B', 'C', 'D', 'E'])} - {random.choice(paises)}",
        "due_number": f"DUE-{random.randint(10000000, 99999999)}",
        "due_date": due_date,
        "dispatch_value": random.randint(10000, 100000) / 100.0,
        "knowledge_number": f"CE-{random.randint(10000, 99999)}",
        "knowledge_date": knowledge_date,
        "endorsement_date": endorsement_date,
        "invoice_number": f"EXP-INV-{random.randint(10000, 99999)}",
        "drawback": random.choice([True, False]),
        "originals_sent_date": gerar_data_aleatoria(datetime.now() - timedelta(days=30), datetime.now()),
        "tracking_number": f"TRACK-{random.randint(100000, 999999)}",
        "events": [
            {
                "id": 1,
                "date": gerar_data_aleatoria(data_inicio, datetime.now()),
                "description": f"Processo exportação criado - {ref}",
                "user": "admin"
            },
            {
                "id": 2,
                "date": gerar_data_aleatoria(data_inicio, datetime.now()),
                "description": f"Documentos recebidos - {ref}",
                "user": "admin"
            }
        ],
        "archived": False
    }
    
    # Campos específicos para exportação marítima
    if export_type == "maritima":
        process.update({
            "cargo_deadline": cargo_deadline,
            "deadline_draft": draft_deadline,
            "shipping_terminal": random.choice(terminais_maritimos),
            "shipping_date": shipping_date,
            "arrival_forecast": calcular_vencimento(shipping_date, random.randint(15, 45)),
            "redex_clearance": gerar_data_aleatoria(data_inicio, datetime.now()),
            "bl_number": f"BL-EXP-{random.randint(100000, 999999)}",
            "container": f"CONT{random.randint(1000000, 9999999)}",
            "ship": f"NAVIO {random.choice(['STAR', 'MAERSK', 'MSC', 'COSCO', 'HAPAG'])} {random.randint(100, 999)}",
        })
    # Campos específicos para exportação rodoviária
    else:
        process.update({
            "cross_terminal": random.choice(terminais_rodoviarios),
            "client_delivery_date": calcular_vencimento(etd, random.randint(5, 15)),
            "carrier": f"TRANSP. {random.choice(['RÁPIDA', 'INTERNACIONAL', 'EXPRESSA', 'GLOBAL'])} {random.choice(['A', 'B', 'C', 'D'])}",
        })
    
    return process

def gerar_30_processos():
    """Gera 30 processos de teste (15 importação e 15 exportação)"""
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
    
    # Criar backup do arquivo existente (se houver)
    if os.path.exists("data.json"):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_filename = f"data_backup_{timestamp}.json"
        with open(backup_filename, "w") as f:
            with open("data.json", "r") as original:
                f.write(original.read())
            print(f"Backup criado em {backup_filename}")
    
    # Gerar processos
    processos = []
    
    # Gerar 15 processos de importação
    for i in range(15):
        processos.append(gerar_processo_importacao(20250500 + i))
    
    # Gerar 15 processos de exportação
    for i in range(15):
        processos.append(gerar_processo_exportacao(20250600 + i))
    
    # Combinar processos existentes com novos
    todos_processos = processos_existentes + processos
    
    # Salvar dados
    dados = {"processes": todos_processos}
    with open("data.json", "w") as f:
        json.dump(dados, f, indent=2)
    
    print(f"Total de {len(todos_processos)} processos (incluindo {len(processos)} novos processos gerados)")
    print(f"- {len([p for p in processos if p['type'] == 'importacao'])} processos de importação")
    print(f"- {len([p for p in processos if p['type'] == 'exportacao'])} processos de exportação")

if __name__ == "__main__":
    gerar_30_processos()
    print("30 processos de teste gerados com sucesso!")