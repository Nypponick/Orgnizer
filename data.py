import pandas as pd
import streamlit as st
import os
import json
import uuid
from datetime import datetime
from utils import format_date

# Default data structure based on the screenshots
DEFAULT_DATA = {
    "company_info": {
        "name": "JGR BROKER",
        "logo_path": "assets/images/jgr_logo.png",
        "contact": "contato@jgrbroker.com",
        "phone": "+55 (XX) XXXX-XXXX"
    },
    "config": {
        "storage_days_per_period": 5  # Dias por período de armazenagem (configurável para teste: 5 dias)
    },
    "processes": [
        {
            "id": "20230001",
            "ref": "DKA-1/Sydex Adventure",
            "invoice": "148/23",
            "origin": "CHINA",
            "type": "FCL 1 X 40",
            "eta": "22/04/23",
            "status": "Em andamento",
            "observations": "",
            "last_update": "07/04/23",
            "exporter": "SNF INC",
            "ship": "MSC VIDHI",
            "agent": "MSC",
            "bl_number": "MEDBX123456",
            "arrival_date": "18/01/2023",
            "container": "TTNU1212342",
            "terminal": "ECOPORTO",
            "invoice_number": "7666",
            "di": "20/146885-6",
            "free_time": "7",
            "free_time_expiry": "25/01/2023",  # Vencimento do Free Time
            "return_date": "25/01/2023",
            "po": "PO123456",  # Número da Purchase Order
            "product": "Eletrônicos",  # Produto
            "map": "MAPA123",  # Número do Mapa
            "port_entry_date": "19/01/2023",  # Data de entrada no Porto/Recinto
            "current_period_start": "19/01/2023",  # Início do período atual de armazenagem
            "current_period_expiry": "18/02/2023",  # Vencimento do período
            "storage_days": "6",  # Dias armazenados (calculado)
            "original_docs": "Sim",  # Documentos originais
            "empty_return": "25/01/2023",  # Devolução de vazio
            "events": [
                {"date": "07/04/23", "description": "Processo criado", "user": "Admin"},
                {"date": "10/04/23", "description": "Documentação recebida", "user": "Admin"},
                {"date": "15/04/23", "description": "Navio em trânsito", "user": "Admin"}
            ]
        },
        {
            "id": "20230002",
            "ref": "DKL-1/Sydex Adventure",
            "invoice": "149/23",
            "origin": "CHINA",
            "type": "FCL 1 X 40",
            "eta": "25/04/23",
            "status": "Em andamento",
            "observations": "",
            "last_update": "08/04/23",
            "exporter": "SNF INC",
            "ship": "MSC VIDHI",
            "agent": "MSC",
            "bl_number": "MEDBX654321",
            "arrival_date": "20/01/2023",
            "container": "TTNU3434343",
            "terminal": "ECOPORTO",
            "invoice_number": "7667",
            "di": "20/146886-7",
            "free_time": "7",
            "free_time_expiry": "27/01/2023",  # Vencimento do Free Time
            "return_date": "27/01/2023",
            "po": "PO654321",  # Número da Purchase Order
            "product": "Máquinas",  # Produto
            "map": "MAPA456",  # Número do Mapa
            "port_entry_date": "21/01/2023",  # Data de entrada no Porto/Recinto
            "current_period_start": "21/01/2023",  # Início do período atual de armazenagem
            "current_period_expiry": "20/02/2023",  # Vencimento do período
            "storage_days": "8",  # Dias armazenados (calculado)
            "original_docs": "Não",  # Documentos originais
            "empty_return": "27/01/2023",  # Devolução de vazio
            "events": [
                {"date": "08/04/23", "description": "Processo criado", "user": "Admin"},
                {"date": "12/04/23", "description": "Documentação recebida", "user": "Admin"},
                {"date": "17/04/23", "description": "Navio em trânsito", "user": "Admin"}
            ]
        }
    ]
}

def load_data():
    """Load data from file or return default data"""
    try:
        if os.path.exists("data.json"):
            with open("data.json", "r") as f:
                data = json.load(f)
        else:
            data = DEFAULT_DATA
            
        # Garantir que todos os processos tenham campos necessários
        periods_updated = []  # Lista para acompanhar quais processos tiveram períodos atualizados
        
        for process in data["processes"]:
            # Garantir que todos os eventos tenham IDs únicos
            if "events" in process:
                # Realizar a verificação em dois passos para evitar erros de iteração
                events_to_update = []
                for i, event in enumerate(process["events"]):
                    if "id" not in event or event["id"] is None or event["id"] == "":
                        events_to_update.append(i)
                
                # Adicionar IDs aos eventos que não têm
                for i in events_to_update:
                    process["events"][i]["id"] = str(uuid.uuid4())
                    print(f"ID gerado para evento {i} do processo {process['id']}: {process['events'][i]['id']}")
            
            # Garantir que exista o campo 'type' (para compatibilidade)
            if "type" not in process:
                process["type"] = "importacao"  # Valor padrão
            
            # Garantir que exista o campo 'archived' (para funcionalidade de arquivamento)
            if "archived" not in process:
                process["archived"] = False
            
            # Para registros antigos, converter 'type' do tipo de carga para tipo de processo
            if process.get("type") in ["FCL 1 X 40", "FCL 1 X 20", "LCL"]:
                # Guardar o tipo de container/carga em outro campo
                process["container_type"] = process["type"]
                # Definir o tipo de processo como importação (valor padrão)
                process["type"] = "importacao"
            
            # Verificar se o período atual expirou e precisa ser atualizado
            try:
                from utils import check_period_expiry
                
                needs_update, new_start, new_expiry = check_period_expiry(process)
                if needs_update and new_start and new_expiry:
                    # Atualizar as datas no processo
                    process["current_period_start"] = new_start
                    process["current_period_expiry"] = new_expiry
                    
                    # Adicionar evento registrando a atualização
                    now = datetime.now().strftime("%d/%m/%Y")
                    event_id = str(uuid.uuid4())
                    
                    if "events" not in process:
                        process["events"] = []
                    
                    event_description = f"Período atualizado automaticamente: início {new_start}, vencimento {new_expiry}"
                    process["events"].append({
                        "id": event_id,
                        "date": now,
                        "description": event_description,
                        "user": "Sistema"
                    })
                    
                    process["last_update"] = now
                    periods_updated.append(process["id"])
            except Exception as e:
                print(f"Erro ao verificar/atualizar período do processo {process.get('id', 'unknown')}: {e}")
        
        # Se houve atualizações, salvar os dados
        if periods_updated:
            print(f"Períodos atualizados para os processos: {', '.join(periods_updated)}")
            save_data(data)
        
        return data
    except Exception as e:
        st.error(f"Erro ao carregar dados: {e}")
        return DEFAULT_DATA

def save_data(data):
    """Save data to file"""
    try:
        with open("data.json", "w") as f:
            json.dump(data, f, indent=4)
        return True
    except Exception as e:
        st.error(f"Erro ao salvar dados: {e}")
        return False

def get_process_by_id(process_id):
    """Get a process by ID"""
    for process in st.session_state.data["processes"]:
        if process["id"] == process_id:
            return process
    return None

def update_process(process_data):
    """Update an existing process"""
    for i, process in enumerate(st.session_state.data["processes"]):
        if process["id"] == process_data["id"]:
            # Verificar se o período atual expirou antes de salvar as alterações
            try:
                from utils import check_period_expiry
                
                needs_update, new_start, new_expiry = check_period_expiry(process_data)
                if needs_update and new_start and new_expiry:
                    # Atualizar as datas no processo
                    process_data["current_period_start"] = new_start
                    process_data["current_period_expiry"] = new_expiry
                    
                    # Adicionar evento registrando a atualização
                    now = datetime.now().strftime("%d/%m/%Y")
                    event_id = str(uuid.uuid4())
                    
                    if "events" not in process_data:
                        process_data["events"] = []
                    
                    event_description = f"Período atualizado automaticamente: início {new_start}, vencimento {new_expiry}"
                    process_data["events"].append({
                        "id": event_id,
                        "date": now,
                        "description": event_description,
                        "user": "Sistema"
                    })
                    
                    process_data["last_update"] = now
                    print(f"Período atualizado para o processo {process_data['id']}")
            except Exception as e:
                print(f"Erro ao verificar/atualizar período do processo {process_data.get('id', 'unknown')}: {e}")
            
            # Atualizar o processo com os dados atualizados
            st.session_state.data["processes"][i] = process_data
            save_data(st.session_state.data)
            return True
    return False

def add_process(process_data):
    """Add a new process"""
    # Generate a new ID if not provided
    if not process_data.get("id"):
        process_data["id"] = generate_process_id()
    
    # Add timestamp for creation
    now = datetime.now().strftime("%d/%m/%Y")
    process_data["last_update"] = now
    
    # Initialize empty events list if not provided
    if "events" not in process_data:
        process_data["events"] = []
    
    # Add creation event
    process_data["events"].append({
        "id": str(uuid.uuid4()),
        "date": now,
        "description": "Processo criado",
        "user": "Admin"
    })
    
    # Configurar período inicial baseado na data de entrada no porto/recinto
    port_entry_date = process_data.get("port_entry_date", "")
    if port_entry_date and not process_data.get("current_period_start"):
        # Usar a data de entrada como início do período atual
        process_data["current_period_start"] = port_entry_date
        
        # Calcular o vencimento baseado nos dias configurados
        try:
            from utils import calculate_period_expiry
            
            # Obter os dias por período da configuração global
            days_per_period = 30  # valor padrão
            if "data" in st.session_state and "config" in st.session_state.data:
                days_per_period = st.session_state.data["config"].get("storage_days_per_period", 30)
            
            # Calcular e definir a data de vencimento
            period_expiry = calculate_period_expiry(port_entry_date, days_per_period)
            if period_expiry:
                process_data["current_period_expiry"] = period_expiry
                
                # Adicionar evento de configuração do período
                process_data["events"].append({
                    "id": str(uuid.uuid4()),
                    "date": now,
                    "description": f"Período inicial configurado: início {port_entry_date}, vencimento {period_expiry}",
                    "user": "Sistema"
                })
        except Exception as e:
            print(f"Erro ao configurar período inicial: {e}")
    
    st.session_state.data["processes"].append(process_data)
    save_data(st.session_state.data)
    return True

def delete_process(process_id):
    """Delete a process by ID"""
    for i, process in enumerate(st.session_state.data["processes"]):
        if process["id"] == process_id:
            del st.session_state.data["processes"][i]
            save_data(st.session_state.data)
            return True
    return False

def add_event(process_id, description, user=None):
    """Add an event to a process"""
    if user is None and 'username' in st.session_state:
        user = st.session_state.username
    else:
        user = "Admin"
        
    for process in st.session_state.data["processes"]:
        if process["id"] == process_id:
            # Gerar um ID único para o evento
            event_id = str(uuid.uuid4())
            new_event = {
                "id": event_id,
                "date": datetime.now().strftime("%d/%m/%Y"),
                "description": description,
                "user": user
            }
            print(f"Adicionando evento com ID {event_id} ao processo {process_id}")
            
            # Inicializar a lista de eventos se não existir
            if "events" not in process:
                process["events"] = []
                
            process["events"].append(new_event)
            process["last_update"] = datetime.now().strftime("%d/%m/%Y")
            save_data(st.session_state.data)
            return True
    return False

def edit_event(process_id, event_id, new_description):
    """Edit an existing event"""
    print(f"Tentando editar evento: process_id={process_id}, event_id={event_id}, nova descrição={new_description}")
    for process in st.session_state.data["processes"]:
        if process["id"] == process_id:
            # Debug: listar todos os eventos neste processo para diagnóstico
            print(f"Processo {process_id} encontrado, procurando evento {event_id}")
            for i, event in enumerate(process.get("events", [])):
                print(f"  Evento {i}: id={event.get('id')}, description={event.get('description')}")
                
                # Verificar se o ID do evento corresponde
                current_id = event.get("id")
                if current_id == event_id:
                    print(f"  Evento {event_id} encontrado! Atualizando descrição...")
                    event["description"] = new_description
                    process["last_update"] = datetime.now().strftime("%d/%m/%Y")
                    save_data(st.session_state.data)
                    return True
                
                # Verificação alternativa para índices como chaves
                if current_id is None and event_id.startswith("event_"):
                    try:
                        # Se event_id é algo como "event_3", extrair o índice
                        idx = int(event_id.split("_")[1])
                        if idx == i:
                            print(f"  Correspondência por índice {idx}! Atualizando descrição...")
                            event["description"] = new_description
                            # Adicionar um ID ao evento para referência futura
                            event["id"] = str(uuid.uuid4())
                            process["last_update"] = datetime.now().strftime("%d/%m/%Y")
                            save_data(st.session_state.data)
                            return True
                    except (ValueError, IndexError):
                        pass
    
    print(f"Evento não encontrado para edição")
    return False

def delete_event(process_id, event_id):
    """Delete an event from a process"""
    print(f"Tentando excluir evento: process_id={process_id}, event_id={event_id}")
    for process in st.session_state.data["processes"]:
        if process["id"] == process_id:
            # Debug: listar todos os eventos neste processo para diagnóstico
            print(f"Processo {process_id} encontrado, procurando evento {event_id}")
            for i, event in enumerate(process.get("events", [])):
                print(f"  Evento {i}: id={event.get('id')}, description={event.get('description')}")
                
                # Verificar se o ID do evento corresponde
                current_id = event.get("id")
                if current_id == event_id:
                    print(f"  Evento {event_id} encontrado! Excluindo...")
                    del process["events"][i]
                    process["last_update"] = datetime.now().strftime("%d/%m/%Y")
                    save_data(st.session_state.data)
                    return True
                
                # Verificação alternativa para índices como chaves
                if current_id is None and event_id.startswith("event_"):
                    try:
                        # Se event_id é algo como "event_3", extrair o índice
                        idx = int(event_id.split("_")[1])
                        if idx == i:
                            print(f"  Correspondência por índice {idx}! Excluindo...")
                            del process["events"][i]
                            process["last_update"] = datetime.now().strftime("%d/%m/%Y")
                            save_data(st.session_state.data)
                            return True
                    except (ValueError, IndexError):
                        pass
    
    print(f"Evento não encontrado para exclusão")
    return False

def generate_process_id():
    """Generate a new process ID"""
    year = datetime.now().year
    existing_ids = [p["id"] for p in st.session_state.data["processes"] if p["id"].startswith(str(year))]
    if not existing_ids:
        return f"{year}0001"
    
    max_id = max(existing_ids)
    next_num = int(max_id[4:]) + 1
    return f"{year}{next_num:04d}"

def archive_process(process_id):
    """Arquivar um processo pelo ID"""
    for i, process in enumerate(st.session_state.data["processes"]):
        if process["id"] == process_id:
            st.session_state.data["processes"][i]["archived"] = True
            
            # Adicionar evento de arquivamento
            now = datetime.now().strftime("%d/%m/%Y")
            event_id = str(uuid.uuid4())
            
            if "events" not in st.session_state.data["processes"][i]:
                st.session_state.data["processes"][i]["events"] = []
                
            st.session_state.data["processes"][i]["events"].append({
                "id": event_id,
                "date": now,
                "description": "Processo arquivado",
                "user": st.session_state.get('username', 'Admin')
            })
            
            st.session_state.data["processes"][i]["last_update"] = now
            save_data(st.session_state.data)
            return True
    return False

def unarchive_process(process_id):
    """Desarquivar um processo pelo ID"""
    for i, process in enumerate(st.session_state.data["processes"]):
        if process["id"] == process_id:
            st.session_state.data["processes"][i]["archived"] = False
            
            # Adicionar evento de desarquivamento
            now = datetime.now().strftime("%d/%m/%Y")
            event_id = str(uuid.uuid4())
            
            if "events" not in st.session_state.data["processes"][i]:
                st.session_state.data["processes"][i]["events"] = []
                
            st.session_state.data["processes"][i]["events"].append({
                "id": event_id,
                "date": now,
                "description": "Processo reativado",
                "user": st.session_state.get('username', 'Admin')
            })
            
            st.session_state.data["processes"][i]["last_update"] = now
            save_data(st.session_state.data)
            return True
    return False

def get_processes_df(include_archived=False):
    """Convert processes to a DataFrame for display
    
    Args:
        include_archived: Se True, inclui processos arquivados. Se False (padrão), exclui arquivados.
    """
    if not st.session_state.data["processes"]:
        return pd.DataFrame()
    
    # Filtrar processos de acordo com o status de arquivamento
    filtered_processes = []
    for process in st.session_state.data["processes"]:
        is_archived = process.get("archived", False)
        if (include_archived and is_archived) or (not include_archived and not is_archived):
            filtered_processes.append(process)
    
    if not filtered_processes:
        return pd.DataFrame()
        
    df = pd.DataFrame(filtered_processes)
    
    # Verificar e atualizar os períodos, e atualizar os dias armazenados para todos os processos
    updated_processes = []
    for i, process in enumerate(st.session_state.data["processes"]):
        # 1. Verificar e atualizar o período atual se necessário
        if "current_period_expiry" in process and process["current_period_expiry"]:
            from utils import check_period_expiry
            
            needs_update, new_start, new_expiry = check_period_expiry(process)
            if needs_update and new_start and new_expiry:
                # Verificar se a última data de vencimento já passou
                try:
                    # Atualizar as datas no processo
                    st.session_state.data["processes"][i]["current_period_start"] = new_start
                    st.session_state.data["processes"][i]["current_period_expiry"] = new_expiry
                    
                    # Adicionar evento registrando a atualização
                    now = datetime.now().strftime("%d/%m/%Y")
                    event_id = str(uuid.uuid4())
                    event_description = f"Período atualizado automaticamente: início {new_start}, vencimento {new_expiry}"
                    
                    if "events" not in st.session_state.data["processes"][i]:
                        st.session_state.data["processes"][i]["events"] = []
                    
                    st.session_state.data["processes"][i]["events"].append({
                        "id": event_id,
                        "date": now,
                        "description": event_description,
                        "user": "Sistema"
                    })
                    
                    updated_processes.append(process["id"])
                except Exception as e:
                    print(f"Erro ao atualizar período: {e}")
        
        # 2. Atualizar os dias armazenados
        if "port_entry_date" in process and process["port_entry_date"]:
            try:
                entry_date = pd.to_datetime(process["port_entry_date"], dayfirst=True)
                today = pd.to_datetime(datetime.now().date())
                days_stored = (today - entry_date).days
                # Salvar como número inteiro para permitir ordenação correta
                st.session_state.data["processes"][i]["storage_days"] = max(0, days_stored)
            except Exception as e:
                # Caso ocorra um erro, garantir que storage_days seja um número
                if "storage_days" in st.session_state.data["processes"][i]:
                    try:
                        # Converter string para inteiro se existente
                        days_str = st.session_state.data["processes"][i]["storage_days"]
                        st.session_state.data["processes"][i]["storage_days"] = int(days_str)
                    except (ValueError, TypeError):
                        # Se não conseguir converter, definir como 0
                        st.session_state.data["processes"][i]["storage_days"] = 0
    
    # Informar quais processos foram atualizados
    if updated_processes:
        print(f"Períodos atualizados para os processos: {', '.join(updated_processes)}")
    
    # Salvar os dados para persistir os dias armazenados atualizados
    save_data(st.session_state.data)
    
    # Atualizar o DataFrame
    df = pd.DataFrame(filtered_processes)
    
    # Garantir que storage_days seja numérico para todos os processos
    if 'storage_days' in df.columns:
        df['storage_days'] = pd.to_numeric(df['storage_days'], errors='coerce').fillna(0).astype(int)
    
    # Select columns for main table view (removido "id" conforme solicitado)
    display_columns = [
        "status", "type", "po", "ref", "origin", "product", "eta", 
        "free_time", "free_time_expiry", "empty_return", "map", 
        "invoice_number", "port_entry_date", "current_period_start", 
        "current_period_expiry", "storage_days", "original_docs",
        # Campos específicos para exportação
        "cargo_deadline", "deadline_draft", "export_type"
    ]
    
    # Manter o id para uso interno, embora não seja exibido na tabela
    internal_id_column = "id"
    
    # Garantir que todas as colunas existam
    for col in display_columns:
        if col not in df.columns:
            df[col] = ""
    
    # Criar uma cópia do dataframe com as colunas de exibição e ID
    # Isso garante que o ID está disponível para operações internas
    # mas não aparece na tabela visível para o usuário
    full_df = df.copy()
    
    # Formatação das colunas de data para o padrão brasileiro (DD/MM/YYYY)
    date_columns = [
        "eta", "free_time_expiry", "empty_return", "port_entry_date", 
        "current_period_start", "current_period_expiry", "return_date",
        # Campos de datas específicos para exportação
        "cargo_deadline", "deadline_draft", "due_date", "knowledge_date", 
        "endorsement_date", "shipping_date", "arrival_forecast", 
        "client_delivery_date", "originals_sent_date"
    ]
    
    # Aplicar formatação apenas às colunas de data que existem no dataframe
    for col in date_columns:
        if col in full_df.columns:
            full_df[col] = full_df[col].apply(lambda x: format_date(x) if x else "")
    
    # Reorganizar colunas para que ID seja a primeira (para uso interno)
    columns_with_id = ["id"] + display_columns
    
    # Garantir que não há duplicatas
    columns_with_id = list(dict.fromkeys(columns_with_id))
    
    return full_df[columns_with_id]
