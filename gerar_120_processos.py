"""
Script para gerar 120 processos de teste (60 importação e 60 exportação) para o sistema JGR Broker
"""
import os
import random
import json
from datetime import datetime, timedelta
from data import load_data, save_data

def gerar_data_aleatoria(inicio, fim):
    """Gera uma data aleatória entre duas datas"""
    delta = fim - inicio
    dias_aleatorios = random.randrange(delta.days)
    return inicio + timedelta(days=dias_aleatorios)

def calcular_vencimento(data_inicio, dias):
    """Calcular data de vencimento a partir de data de início e dias"""
    if not data_inicio:
        return None
    if isinstance(data_inicio, str):
        try:
            data_inicio = datetime.strptime(data_inicio, "%d/%m/%Y")
        except ValueError:
            return None
    
    data_vencimento = data_inicio + timedelta(days=dias)
    return data_vencimento.strftime("%d/%m/%Y")

def calcular_dias_armazenados(entry_date):
    """Calcular dias de armazenamento"""
    if not entry_date:
        return 0
    
    if isinstance(entry_date, str):
        try:
            data_entrada = datetime.strptime(entry_date, "%d/%m/%Y")
        except ValueError:
            return 0
    else:
        data_entrada = entry_date
        
    hoje = datetime.now()
    return (hoje - data_entrada).days

def gerar_processo_importacao(id_processo):
    """Gera um processo de importação com dados completos"""
    status_options = ["Novo Processo", "Em andamento", "Navio em Santos", "Em despacho", "Entregue ao cliente", "Concluído"]
    origem_options = ["CHINA", "EUA", "EUROPA", "ÁSIA", "AMÉRICA DO SUL"]
    terminal_options = ["SANTOS", "SÃO SEBASTIÃO", "PARANAGUÁ", "RIO DE JANEIRO", "ITAJAÍ"]
    
    # Datas aleatórias
    hoje = datetime.now()
    ha_3_meses = hoje - timedelta(days=90)
    daqui_3_meses = hoje + timedelta(days=90)
    
    port_entry_date = gerar_data_aleatoria(ha_3_meses, hoje).strftime("%d/%m/%Y")
    
    # Free time aleatório de 7 a 21 dias
    free_time = random.randint(7, 21)
    
    # Calcular vencimento do free time
    port_entry_datetime = datetime.strptime(port_entry_date, "%d/%m/%Y")
    free_time_expiry = (port_entry_datetime + timedelta(days=free_time)).strftime("%d/%m/%Y")
    
    # Período atual começa após o vencimento do free time
    period_length = 15  # Dias por período
    periods_passed = random.randint(0, 3)
    
    current_period_start = port_entry_datetime + timedelta(days=free_time + (periods_passed * period_length))
    current_period_start_str = current_period_start.strftime("%d/%m/%Y")
    
    current_period_expiry = (current_period_start + timedelta(days=period_length)).strftime("%d/%m/%Y")
    
    # Dias armazenados
    storage_days = calcular_dias_armazenados(port_entry_datetime)
    
    eta = gerar_data_aleatoria(ha_3_meses, hoje).strftime("%d/%m/%Y")
    if random.random() > 0.7:  # 30% dos casos terá ETA futuro
        eta = gerar_data_aleatoria(hoje, daqui_3_meses).strftime("%d/%m/%Y")
    
    last_update = gerar_data_aleatoria(port_entry_datetime, hoje).strftime("%d/%m/%Y")
    
    return {
        "id": id_processo,
        "tipo": "Importação",
        "status": random.choice(status_options),
        "ref": f"REF{random.randint(10000, 99999)}",
        "po": f"PO{random.randint(100000, 999999)}",
        "origin": random.choice(origem_options),
        "product": f"Produto teste de importação {random.randint(1, 1000)}",
        "eta": eta,
        "free_time": free_time,
        "free_time_expiry": free_time_expiry,
        "terminal": random.choice(terminal_options),
        "port_entry_date": port_entry_date,
        "current_period_start": current_period_start_str,
        "current_period_expiry": current_period_expiry,
        "storage_days": storage_days,
        "map": f"MAP{random.randint(10000, 99999)}",
        "invoice": f"INV{random.randint(100000, 999999)}",
        "empty_return": (port_entry_datetime + timedelta(days=random.randint(10, 30))).strftime("%d/%m/%Y") if random.random() > 0.3 else "",
        "original_docs": "Sim" if random.random() > 0.5 else "Não",
        "exporter": f"Exportador {random.randint(1, 50)}",
        "ship": f"Navio {random.randint(1, 30)}",
        "agent": f"Agente {random.randint(1, 20)}",
        "bl_number": f"BL{random.randint(10000, 99999)}",
        "container": f"CONT{random.randint(10000, 99999)}",
        "arrival_date": (datetime.strptime(eta, "%d/%m/%Y") + timedelta(days=random.randint(1, 5))).strftime("%d/%m/%Y") if eta else "",
        "di": f"DI{random.randint(10000, 99999)}" if random.random() > 0.4 else "",
        "invoice_number": f"NF{random.randint(10000, 99999)}" if random.random() > 0.4 else "",
        "return_date": (port_entry_datetime + timedelta(days=random.randint(20, 45))).strftime("%d/%m/%Y") if random.random() > 0.6 else "",
        "last_update": last_update,
        "observations": f"Observações de teste para processo {id_processo}" if random.random() > 0.7 else "",
        "events": [
            {
                "id": f"evt{i}_{id_processo}",
                "date": (port_entry_datetime + timedelta(days=i*3)).strftime("%d/%m/%Y"),
                "description": f"Evento {i} do processo {id_processo}: {random.choice(['Documento recebido', 'Carga liberada', 'Pagamento efetuado', 'Contato com cliente', 'Acompanhamento'])}",
                "user": f"usuario{random.randint(1, 5)}"
            } for i in range(random.randint(1, 5))
        ],
        "archived": False,
        "client_id": f"cliente_{random.randint(1, 10)}"
    }

def gerar_processo_exportacao(id_processo):
    """Gera um processo de exportação com dados completos"""
    status_options = ["Novo Processo", "Em andamento", "Documentos recebidos", "Em despacho", "Carga embarcada", "Concluído"]
    destino_options = ["CHINA", "EUA", "EUROPA", "ÁSIA", "AMÉRICA DO SUL"]
    terminal_options = ["SANTOS", "SÃO SEBASTIÃO", "PARANAGUÁ", "RIO DE JANEIRO", "ITAJAÍ"]
    shipping_terminals = ["Terminal 1", "Terminal 2", "Terminal 3", "Terminal 4", "Terminal 5"]
    crossing_terminals = ["Terminal Terrestre 1", "Terminal Terrestre 2", "Terminal Terrestre 3"]
    
    # Datas aleatórias
    hoje = datetime.now()
    ha_3_meses = hoje - timedelta(days=90)
    daqui_3_meses = hoje + timedelta(days=90)
    
    port_entry_date = gerar_data_aleatoria(ha_3_meses, hoje).strftime("%d/%m/%Y")
    
    etd = gerar_data_aleatoria(hoje, daqui_3_meses).strftime("%d/%m/%Y")
    if random.random() > 0.7:  # 30% dos casos terá ETD passado
        etd = gerar_data_aleatoria(ha_3_meses, hoje).strftime("%d/%m/%Y")
    
    # Prazos aleatórios
    cargo_deadline = (datetime.strptime(etd, "%d/%m/%Y") - timedelta(days=random.randint(5, 15))).strftime("%d/%m/%Y")
    draft_deadline = (datetime.strptime(cargo_deadline, "%d/%m/%Y") - timedelta(days=random.randint(2, 5))).strftime("%d/%m/%Y")
    shipping_date = (datetime.strptime(etd, "%d/%m/%Y") + timedelta(days=random.randint(1, 3))).strftime("%d/%m/%Y")
    arrival_forecast = (datetime.strptime(shipping_date, "%d/%m/%Y") + timedelta(days=random.randint(15, 45))).strftime("%d/%m/%Y")
    
    # 50% será marítimo, 50% rodoviário
    is_maritime = random.random() > 0.5
    
    # Determinar o tipo de transporte
    transport_type = "maritimo" if is_maritime else "rodoviario"
    
    # Datas de entrega/liberação baseadas no tipo de transporte
    if is_maritime:
        redex_clearance = (datetime.strptime(cargo_deadline, "%d/%m/%Y") - timedelta(days=random.randint(1, 3))).strftime("%d/%m/%Y")
        docs_shipping_date = (datetime.strptime(shipping_date, "%d/%m/%Y") + timedelta(days=random.randint(5, 10))).strftime("%d/%m/%Y")
        tracking_number = f"TRK{random.randint(100000, 999999)}" if random.random() > 0.4 else ""
        client_delivery_date = ""
        carrier = ""
        terminal = random.choice(shipping_terminals)
    else:
        redex_clearance = ""
        docs_shipping_date = ""
        tracking_number = ""
        client_delivery_date = (datetime.strptime(etd, "%d/%m/%Y") + timedelta(days=random.randint(5, 15))).strftime("%d/%m/%Y")
        carrier = f"Transportadora {random.randint(1, 10)}"
        terminal = random.choice(crossing_terminals)
    
    last_update = gerar_data_aleatoria(datetime.strptime(port_entry_date, "%d/%m/%Y"), hoje).strftime("%d/%m/%Y")
    
    return {
        "id": id_processo,
        "tipo": "Exportação",
        "status": random.choice(status_options),
        "ref": f"REF{random.randint(10000, 99999)}",
        "origin": random.choice(destino_options),
        "product": f"Produto teste de exportação {random.randint(1, 1000)}",
        "etd": etd,
        "terminal": terminal,
        "port_entry_date": port_entry_date,
        "invoice": f"INV{random.randint(100000, 999999)}",
        "original_docs": "Sim" if random.random() > 0.5 else "Não",
        "map": f"MAP{random.randint(10000, 99999)}",
        "cargo_deadline": cargo_deadline if is_maritime else "",
        "draft_deadline": draft_deadline if is_maritime else "",
        "shipping_terminal": terminal if is_maritime else "",
        "shipping_date": shipping_date,
        "arrival_forecast": arrival_forecast,
        "redex_clearance": redex_clearance,
        "original_docs_shipping_date": docs_shipping_date,
        "tracking_number": tracking_number,
        "crossing_terminal": terminal if not is_maritime else "",
        "client_delivery_date": client_delivery_date,
        "carrier": carrier,
        "importer": f"Importador {random.randint(1, 50)}",
        "invoice_number": f"NF{random.randint(10000, 99999)}",
        "due": f"DUE{random.randint(10000, 99999)}",
        "due_registration_date": (datetime.strptime(port_entry_date, "%d/%m/%Y") + timedelta(days=random.randint(1, 10))).strftime("%d/%m/%Y"),
        "dispatch_value": f"USD {random.randint(5000, 100000)}.00",
        "bl_number": f"BL{random.randint(10000, 99999)}",
        "bl_date": (datetime.strptime(shipping_date, "%d/%m/%Y") - timedelta(days=random.randint(1, 3))).strftime("%d/%m/%Y") if shipping_date else "",
        "endorsement_date": (datetime.strptime(port_entry_date, "%d/%m/%Y") + timedelta(days=random.randint(5, 15))).strftime("%d/%m/%Y"),
        "drawback": f"DB{random.randint(10000, 99999)}" if random.random() > 0.7 else "",
        "last_update": last_update,
        "observations": f"Observações de teste para processo de exportação {id_processo}" if random.random() > 0.7 else "",
        "events": [
            {
                "id": f"evt{i}_{id_processo}",
                "date": (datetime.strptime(port_entry_date, "%d/%m/%Y") + timedelta(days=i*3)).strftime("%d/%m/%Y"),
                "description": f"Evento {i} do processo {id_processo}: {random.choice(['Documento enviado', 'Carga despachada', 'Pagamento recebido', 'Contato com importador', 'Acompanhamento'])}",
                "user": f"usuario{random.randint(1, 5)}"
            } for i in range(random.randint(1, 5))
        ],
        "transport_type": transport_type,
        "archived": False,
        "client_id": f"cliente_{random.randint(1, 10)}"
    }

def gerar_120_processos():
    """Gera 120 processos de teste (60 importação e 60 exportação)"""
    # Carregar dados existentes
    data = load_data()
    
    # Salvar backup
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_filename = f"data_backup_{timestamp}.json"
    
    with open(backup_filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    
    print(f"Backup dos dados originais salvo em: {backup_filename}")
    
    # Limpar processos existentes
    # Por padrão, manteremos os processos existentes e apenas adicionaremos novos
    # data['processes'] = []
    
    # ID base para novos processos
    base_id = 1000
    if data['processes']:
        # Buscar maior ID existente
        ids = [int(p.get('id', 0)) for p in data['processes'] if p.get('id', "").isdigit()]
        if ids:
            base_id = max(ids) + 1
    
    # Gerar processos
    print("Gerando 60 processos de importação...")
    for i in range(60):
        processo_id = str(base_id + i)
        processo = gerar_processo_importacao(processo_id)
        data['processes'].append(processo)
    
    print("Gerando 60 processos de exportação...")
    for i in range(60):
        processo_id = str(base_id + 60 + i)
        processo = gerar_processo_exportacao(processo_id)
        data['processes'].append(processo)
    
    # Salvar dados
    save_data(data)
    
    print(f"Foram gerados 120 processos de teste (60 importação e 60 exportação)")
    print(f"Total de processos no sistema: {len(data['processes'])}")

if __name__ == "__main__":
    gerar_120_processos()