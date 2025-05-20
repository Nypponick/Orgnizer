import streamlit as st
import pandas as pd
from datetime import datetime
from data import get_process_by_id, add_process, update_process, add_event
from components.auth import get_users, assign_processes_to_client

def display_add_edit_form(navigate_function):
    """Display form for adding or editing a process"""
    from utils import calculate_free_time_expiry, calculate_period_expiry, calculate_storage_days
    
    # Get storage days per period from config
    storage_days_per_period = st.session_state.data.get("config", {}).get("storage_days_per_period", 30)
    
    if st.session_state.edit_mode:
        process = get_process_by_id(st.session_state.selected_process)
        if process is None:
            st.error("Processo não encontrado!")
            return
        # Determinar título baseado no tipo de processo
        process_type = process.get("type", "importacao")
        if process_type == "exportacao":
            st.header("Editar Processo de Exportação")
        else:
            st.header("Editar Processo de Importação")
    else:
        st.header("Novo Processo")
        # Iniciar com dicionário vazio para não definir padrão
        process = {"type": "importacao"}  # O tipo será definido pelo usuário
    
    # Adicionar seletor de tipo de processo ANTES do formulário em uma coluna mais estreita
    # Isso permite que o usuário mude o tipo e a interface responda
    col_select, _ = st.columns([1, 3])  # Primeira coluna ocupará 1/4 da largura
    with col_select:
        process_type = st.selectbox(
            "Tipo de Processo",
            options=["importacao", "exportacao"],
            format_func=lambda x: "Importação" if x == "importacao" else "Exportação",
            index=0 if process.get("type") != "exportacao" else 1,
            key="process_type_key"
        )
    
    # Create a form with multiple sections
    with st.form("process_form", clear_on_submit=False):
        # Basic Information Section
        st.subheader("Informações Básicas")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            process_id = st.text_input("Código", value=process.get("id", ""), disabled=st.session_state.edit_mode)
            reference = st.text_input("Referência", value=process.get("ref", ""))
            
            # PO para Importação, Pedido para Exportação
            if process_type == "importacao":
                po = st.text_input("PO (Purchase Order)", value=process.get("po", ""))
            else:
                po = st.text_input("Pedido", value=process.get("po", ""))
        
        with col2:
            # Campo invoice removido daqui para evitar duplicação
            
            # Origem para Importação, Destino para Exportação
            if process_type == "importacao":
                origin = st.selectbox("Origem", options=["CHINA", "USA", "GERMANY", "JAPAN", "OTHER"], 
                                    index=0 if not process.get("origin") else ["CHINA", "USA", "GERMANY", "JAPAN", "OTHER"].index(process.get("origin")),
                                    key="origin_selectbox")
            else:
                origin = st.selectbox("Destino", options=["CHINA", "USA", "GERMANY", "JAPAN", "OTHER"], 
                                    index=0 if not process.get("origin") else ["CHINA", "USA", "GERMANY", "JAPAN", "OTHER"].index(process.get("origin")),
                                    key="destination_selectbox")
            
            product = st.text_input("Produto", value=process.get("product", ""))
        
        with col3:
            container_type = st.text_input("Tipo de Container", value=process.get("container_type", "FCL 1 X 40"))
            
            # ETA para Importação, ETD para Exportação
            if process_type == "importacao":
                eta = st.date_input("ETA (Chegada)", value=None if not process.get("eta") else pd.to_datetime(process.get("eta"), dayfirst=True))
            else:
                eta = st.date_input("ETD (Saída)", value=None if not process.get("eta") else pd.to_datetime(process.get("eta"), dayfirst=True))
            
            map_number = st.text_input("Mapa", value=process.get("map", ""))
        
        # Shipping Information Section
        if process_type == "importacao":
            st.subheader("Informações de Embarque")
        else:
            st.subheader("Informações de Exportação")
            
        col1, col2, col3 = st.columns(3)
        
        with col1:
            # Exportador para Importação, Embarcador para Exportação
            if process_type == "importacao":
                exporter = st.text_input("Exportador", value=process.get("exporter", ""))
            else:
                exporter = st.text_input("Embarcador", value=process.get("exporter", ""))
                
            ship = st.text_input("Navio", value=process.get("ship", ""))
            agent = st.text_input("Agente", value=process.get("agent", ""))
        
        with col2:
            bl_number = st.text_input("Número B/L", value=process.get("bl_number", ""))
            container = st.text_input("Container", value=process.get("container", ""))
        
        with col3:
            # Free Time e Devolução são específicos para importação
            if process_type == "importacao":
                free_time = st.text_input("Free Time (dias)", value=process.get("free_time", "7"))
                
                # Calcular vencimento do free time automaticamente baseado no ETA e dias de free time
                free_time_expiry_value = ""
                if eta and free_time:
                    free_time_expiry_value = calculate_free_time_expiry(eta.strftime("%d/%m/%Y"), free_time)
                
                free_time_expiry = st.date_input(
                    "Vencimento do Free Time (calculado automaticamente)", 
                    value=None if not free_time_expiry_value else pd.to_datetime(free_time_expiry_value, dayfirst=True),
                    disabled=True
                )
                
                empty_return = st.date_input(
                    "Devolução de Vazio", 
                    value=None if not process.get("empty_return") else pd.to_datetime(process.get("empty_return"), dayfirst=True)
                )
            else:
                # Campos específicos para exportação na coluna 3
                map_number = st.text_input("Mapa de Exportação", value=process.get("map", ""))
                importer = st.text_input("Importador", value=process.get("importer", ""))
        
        # Storage Information Section
        if process_type == "importacao":
            st.subheader("Informações de Armazenagem")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                port_entry_date = st.date_input(
                    "Entrada no Porto/Recinto", 
                    value=None if not process.get("port_entry_date") else pd.to_datetime(process.get("port_entry_date"), dayfirst=True)
                )
                
                terminal = st.text_input("Terminal", value=process.get("terminal", ""))
                
            with col2:
                current_period_start = st.date_input(
                    "Início do Período Atual", 
                    value=None if not process.get("current_period_start") else pd.to_datetime(process.get("current_period_start"), dayfirst=True)
                )
                
                days_per_period = st.number_input(
                    "Dias por Período", 
                    min_value=1, 
                    max_value=365, 
                    value=storage_days_per_period,
                    help="Número de dias por período de armazenagem"
                )
            
            with col3:
                # Calcular vencimento do período automaticamente
                current_period_expiry_value = ""
                if current_period_start:
                    current_period_expiry_value = calculate_period_expiry(
                        current_period_start.strftime("%d/%m/%Y"), 
                        days_per_period
                    )
                
                current_period_expiry = st.date_input(
                    "Vencimento do Período (calculado automaticamente)", 
                    value=None if not current_period_expiry_value else pd.to_datetime(current_period_expiry_value, dayfirst=True),
                    disabled=True
                )
                
                # Calcular dias armazenados automaticamente
                storage_days_value = process.get("storage_days", "0")
                if port_entry_date:
                    storage_days_value = calculate_storage_days(port_entry_date.strftime("%d/%m/%Y"))
                
                storage_days = st.text_input(
                    "Dias Armazenados", 
                    value=storage_days_value,
                    disabled=True
                )
        else:
            # Para exportação, mostramos informações relacionadas ao terminal de exportação
            st.subheader("Informações do Terminal de Exportação")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                port_entry_date = st.date_input(
                    "Entrada no Terminal", 
                    value=None if not process.get("port_entry_date") else pd.to_datetime(process.get("port_entry_date"), dayfirst=True)
                )
                
                terminal = st.text_input("Terminal de Exportação", value=process.get("terminal", ""))
                
            with col2:
                # Campos específicos para exportação
                if not st.session_state.edit_mode:  # Se for um novo processo
                    # Inicializa data atual para campos não preenchidos
                    due_date = st.date_input(
                        "Data de Registro da DU-E",
                        value=None if not process.get("due_date") else pd.to_datetime(process.get("due_date"), dayfirst=True),
                        key="due_date_export"
                    )
                else:
                    due_date = st.date_input(
                        "Data de Registro da DU-E",
                        value=None if not process.get("due_date") else pd.to_datetime(process.get("due_date"), dayfirst=True),
                        key="due_date_export"
                    )
                
                dispatch_value = st.text_input("Valor do Despacho em USD", value=process.get("dispatch_value", ""), key="dispatch_value_export")
                
            with col3:
                knowledge_number = st.text_input("Número do Conhecimento", value=process.get("knowledge_number", ""), key="knowledge_number_main")
                
                knowledge_date = st.date_input(
                    "Data do Conhecimento", 
                    value=None if not process.get("knowledge_date") else pd.to_datetime(process.get("knowledge_date"), dayfirst=True),
                    key="knowledge_date_main"
                )
                
                endorsement_date = st.date_input(
                    "Data de Averbação", 
                    value=None if not process.get("endorsement_date") else pd.to_datetime(process.get("endorsement_date"), dayfirst=True),
                    key="endorsement_date_main"
                )
        
        # Additional Information Section
        st.subheader("Documentos e Status")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            # Nota Fiscal para Importação, Fatura para Exportação
            if process_type == "importacao":
                invoice_number = st.text_input("Nota Fiscal", value=process.get("invoice_number", ""), key="invoice_number_field")
            else:
                # Usamos o valor de invoice aqui para compatibilidade com dados existentes
                initial_value = process.get("invoice_number", "") or process.get("invoice", "")
                invoice_number = st.text_input("Fatura (Invoice)", value=initial_value, key="invoice_field")
            
            # D.I. para Importação, DU-E para Exportação
            if process_type == "importacao":
                di = st.text_input("D.I.", value=process.get("di", ""))
            else:
                di = st.text_input("DU-E (Declaração Única de Exportação)", value=process.get("di", ""))
        
        with col2:
            original_docs = st.selectbox(
                "Documentos Originais", 
                options=["Sim", "Não", "Em trânsito"],
                index=0 if not process.get("original_docs") else ["Sim", "Não", "Em trânsito"].index(process.get("original_docs"))
            )
            
            # Campos específicos para exportação
            if process_type == "exportacao":
                # Drawback
                drawback = st.text_input("Drawback", value=process.get("drawback", ""), key="drawback_export_main")
                
                # Data de envio dos originais
                originals_sent_date = st.date_input(
                    "Data de Envio dos Originais",
                    value=None if not process.get("originals_sent_date") else pd.to_datetime(process.get("originals_sent_date"), dayfirst=True),
                    key="originals_sent_date_export_main"
                )
                
                # Número do rastreio
                tracking_number = st.text_input("Número do Rastreio", value=process.get("tracking_number", ""), key="tracking_number_export_main")
            
# O campo Data de Devolução foi removido, pois é redundante com Devolução de Vazio
        
        with col3:
            # Exportação Marítima ou Rodoviária 
            if process_type == "exportacao":
                export_type = st.selectbox(
                    "Tipo de Exportação", 
                    options=["Marítima", "Rodoviária"],
                    index=0 if not process.get("export_type") else ["Marítima", "Rodoviária"].index(process.get("export_type", "Marítima")),
                    key="export_type_selector"
                )
            
            # Importar a função para obter status por tipo
            from components.settings import get_status_options
            
            # Obter status específicos para o tipo de processo atual
            status_options = get_status_options(process_type)
            
            # Determinar o índice para o valor padrão
            if not process.get("status"):
                status_index = 0
            else:
                # Se o status atual existe na lista, use-o; caso contrário, use o primeiro
                current_status = process.get("status")
                if current_status in status_options:
                    status_index = status_options.index(current_status)
                else:
                    status_index = 0
                    st.warning(f"O status '{current_status}' não está mais disponível para processos de {process_type.capitalize()}. Por favor, selecione um novo status.")
            
            status = st.selectbox(
                "Status", 
                options=status_options,
                index=status_index,
                key=f"status_selectbox_{process_type}"
            )
        
        # Seção específica para Exportação
        if process_type == "exportacao":
            st.subheader("Informações Específicas de Exportação")
            
            # Tipo de exportação (Marítima/Rodoviária)
            export_type = st.selectbox(
                "Tipo de Exportação",
                options=["Marítima", "Rodoviária"],
                index=0 if not process.get("export_type") else ["Marítima", "Rodoviária"].index(process.get("export_type", "Marítima")),
                key="export_type_section"
            )
            
            # Campos específicos para exportação marítima
            if export_type == "Marítima":
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    # DEAD-LINE CARGA
                    cargo_deadline = st.date_input(
                        "Deadline Carga",
                        value=None if not process.get("cargo_deadline") else pd.to_datetime(process.get("cargo_deadline"), dayfirst=True),
                        key="cargo_deadline_export"
                    )
                    
                    # DEAD-LINE DRAFT
                    deadline_draft = st.date_input(
                        "Deadline Draft",
                        value=None if not process.get("deadline_draft") else pd.to_datetime(process.get("deadline_draft"), dayfirst=True),
                        key="deadline_draft_export"
                    )
                    
                    # TERMINAL DE EMBARQUE
                    shipping_terminal = st.text_input("Terminal de Embarque", value=process.get("shipping_terminal", ""), key="shipping_terminal_export")
                
                with col2:
                    # DATA DE EMBARQUE
                    shipping_date = st.date_input(
                        "Data de Embarque",
                        value=None if not process.get("shipping_date") else pd.to_datetime(process.get("shipping_date"), dayfirst=True),
                        key="shipping_date_export"
                    )
                    
                    # PREVISÃO DE CHEGADA
                    arrival_forecast = st.date_input(
                        "Previsão de Chegada",
                        value=None if not process.get("arrival_forecast") else pd.to_datetime(process.get("arrival_forecast"), dayfirst=True),
                        key="arrival_forecast_export"
                    )
                
                with col3:
                    # DESEMBARAÇO REDEX
                    redex_clearance = st.selectbox(
                        "Desembaraço REDEX",
                        options=["Sim", "Não"],
                        index=0 if not process.get("redex_clearance") else ["Sim", "Não"].index(process.get("redex_clearance", "Não"))
                    )
            
            # Campos específicos para exportação rodoviária
            elif export_type == "Rodoviária":
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    # TERMINAL DE CRUZE
                    cross_terminal = st.text_input("Terminal de Cruze", value=process.get("cross_terminal", ""))
                
                with col2:
                    # DATA DE ENTREGA NO CLIENTE
                    client_delivery_date = st.date_input(
                        "Data de Entrega no Cliente",
                        value=None if not process.get("client_delivery_date") else pd.to_datetime(process.get("client_delivery_date"), dayfirst=True)
                    )
                
                with col3:
                    # TRANSPORTADORA
                    carrier = st.text_input("Transportadora", value=process.get("carrier", ""))
        
        # Observations
        observations = st.text_area("Observações", value=process.get("observations", ""), height=100)
        
        # Seção para atribuir cliente (apenas para administradores)
        if 'user_role' in st.session_state and st.session_state.user_role == 'admin':
            st.subheader("Atribuir a Cliente")
            
            # Obter lista de clientes
            users = get_users()
            clients = [user for user in users if user['role'] == 'client']
            
            # Verificar se já existe um cliente atribuído ao processo (quando estiver editando)
            current_client = None
            current_client_id = None
            if st.session_state.edit_mode and process.get("id"):
                from components.auth import get_client_for_process
                current_client = get_client_for_process(process.get("id"))
                if current_client:
                    current_client_id = current_client.get("id")
            
            # Se não houver clientes, exibir mensagem
            if not clients:
                st.info("Não há clientes cadastrados. Adicione clientes na seção de Usuários para poder atribuir processos.")
                assigned_client = current_client_id  # Manter o cliente atual se existir
            else:
                # Lista de clientes para seleção
                client_options = [(user['id'], f"{user['name']} ({user['email']})") for user in clients]
                client_options.insert(0, ("", "Selecione um cliente..."))  # Opção para não selecionar nenhum cliente
                
                client_ids = [id for id, _ in client_options]
                client_labels = [label for _, label in client_options]
                
                # Determinar o índice padrão (cliente atual se estiver editando)
                default_index = 0
                if current_client_id:
                    # Procurar o índice do cliente atual na lista
                    try:
                        default_index = client_ids.index(current_client_id)
                    except ValueError:
                        default_index = 0
                
                # Campo para selecionar cliente
                selected_client_label = st.selectbox(
                    "Cliente", 
                    options=client_labels,
                    index=default_index  # Pré-selecionar o cliente atual
                )
                
                # Determinar o ID do cliente selecionado
                if selected_client_label == "Selecione um cliente...":
                    assigned_client = None
                else:
                    selected_index = client_labels.index(selected_client_label)
                    assigned_client = client_ids[selected_index]
        else:
            # Se não for admin, não pode atribuir cliente
            assigned_client = None
        
        # Submit buttons
        col1, col2 = st.columns(2)
        
        with col1:
            submit_button = st.form_submit_button("Salvar", use_container_width=True)
        
        with col2:
            cancel_button = st.form_submit_button("Cancelar", use_container_width=True)
    
    # Handle form submission
    # Inicializar variáveis de importação e exportação de forma condicional
    # Isso evita erros de variáveis não definidas

    # Variáveis compartilhadas entre tipos de processo
    if not 'days_per_period' in locals(): 
        days_per_period = storage_days_per_period
        
    # Variáveis para processos de importação
    if process_type == "importacao":
        if not 'free_time' in locals(): free_time = None
        if not 'free_time_expiry' in locals(): free_time_expiry = None
        if not 'current_period_start' in locals(): current_period_start = None
        if not 'current_period_expiry' in locals(): current_period_expiry = None
        if not 'storage_days' in locals(): storage_days = ""
        if not 'empty_return' in locals(): empty_return = None
        if not 'port_entry_date' in locals(): port_entry_date = None
        if not 'exporter' in locals(): exporter = ""
        if not 'ship' in locals(): ship = ""
        if not 'agent' in locals(): agent = ""
        if not 'bl_number' in locals(): bl_number = ""
        if not 'di' in locals(): di = ""
        if not 'original_docs' in locals(): original_docs = ""
        if not 'map_number' in locals(): map_number = ""
        if not 'eta' in locals(): eta = None
    
    # Variáveis para processos de exportação
    else:  # process_type == "exportacao"
        if not 'importer' in locals(): importer = ""
        if not 'due_date' in locals(): due_date = None
        if not 'dispatch_value' in locals(): dispatch_value = ""
        if not 'knowledge_number' in locals(): knowledge_number = ""
        if not 'knowledge_date' in locals(): knowledge_date = None
        if not 'endorsement_date' in locals(): endorsement_date = None
        if not 'drawback' in locals(): drawback = ""
        if not 'originals_sent_date' in locals(): originals_sent_date = None
        if not 'tracking_number' in locals(): tracking_number = ""
        if not 'export_type' in locals(): export_type = "Marítima"
        # Variáveis específicas para exportação marítima
        if not 'cargo_deadline' in locals(): cargo_deadline = None
        if not 'deadline_draft' in locals(): deadline_draft = None
        if not 'shipping_terminal' in locals(): shipping_terminal = ""
        if not 'shipping_date' in locals(): shipping_date = None
        if not 'arrival_forecast' in locals(): arrival_forecast = None
        if not 'redex_clearance' in locals(): redex_clearance = ""
        # Variáveis específicas para exportação rodoviária
        if not 'cross_terminal' in locals(): cross_terminal = ""
        if not 'client_delivery_date' in locals(): client_delivery_date = None
        if not 'carrier' in locals(): carrier = ""
    
    if submit_button:
        # Prepare common process data
        process_data = {
            "id": process_id if process_id else None,
            "ref": reference,
            "invoice": invoice_number,  # Unificamos os campos invoice e invoice_number
            "origin": origin,
            "type": process_type,
            "container_type": container_type,
            "status": status,
            "observations": observations,
            "container": container,
            "terminal": terminal,
            "invoice_number": invoice_number,
            "product": product,
            "last_update": datetime.now().strftime("%d/%m/%Y")
        }
        
        # Add import-specific fields if applicable
        if process_type == "importacao":
            process_data.update({
                "eta": eta.strftime("%d/%m/%Y") if eta else "",
                "exporter": exporter,
                "ship": ship,
                "agent": agent,
                "bl_number": bl_number,
                "di": di,
                "free_time": free_time,
                "free_time_expiry": free_time_expiry.strftime("%d/%m/%Y") if free_time_expiry else "",
                "po": po,
                "map": map_number,
                "port_entry_date": port_entry_date.strftime("%d/%m/%Y") if port_entry_date else "",
                "current_period_start": current_period_start.strftime("%d/%m/%Y") if current_period_start else "",
                "current_period_expiry": current_period_expiry.strftime("%d/%m/%Y") if current_period_expiry else "",
                "storage_days": storage_days,
                "original_docs": original_docs,
                "empty_return": empty_return.strftime("%d/%m/%Y") if empty_return else "",
            })
        
        # Adicionar campos específicos para exportação, se aplicável
        elif process_type == "exportacao":
            # Campos básicos de exportação
            if 'importer' in locals():
                process_data["importer"] = importer
            
            # Campos de documentos de exportação
            if 'due_date' in locals() and due_date:
                process_data["due_date"] = due_date.strftime("%d/%m/%Y")
                
            if 'dispatch_value' in locals():
                process_data["dispatch_value"] = dispatch_value
                
            if 'knowledge_number' in locals():
                process_data["knowledge_number"] = knowledge_number
                
            if 'knowledge_date' in locals() and knowledge_date:
                process_data["knowledge_date"] = knowledge_date.strftime("%d/%m/%Y")
                
            if 'endorsement_date' in locals() and endorsement_date:
                process_data["endorsement_date"] = endorsement_date.strftime("%d/%m/%Y")
                
            if 'drawback' in locals():
                process_data["drawback"] = drawback
                
            if 'originals_sent_date' in locals() and originals_sent_date:
                process_data["originals_sent_date"] = originals_sent_date.strftime("%d/%m/%Y")
                
            if 'tracking_number' in locals():
                process_data["tracking_number"] = tracking_number
                
            # Tipo de exportação (Marítima/Rodoviária)
            if 'export_type' in locals():
                process_data["export_type"] = export_type
                
            # Campos específicos para exportação marítima
            if 'export_type' in locals() and export_type == "Marítima":
                if 'cargo_deadline' in locals() and cargo_deadline:
                    process_data["cargo_deadline"] = cargo_deadline.strftime("%d/%m/%Y")
                    
                if 'deadline_draft' in locals() and deadline_draft:
                    process_data["deadline_draft"] = deadline_draft.strftime("%d/%m/%Y")
                    
                if 'shipping_terminal' in locals():
                    process_data["shipping_terminal"] = shipping_terminal
                    
                if 'shipping_date' in locals() and shipping_date:
                    process_data["shipping_date"] = shipping_date.strftime("%d/%m/%Y")
                    
                if 'arrival_forecast' in locals() and arrival_forecast:
                    process_data["arrival_forecast"] = arrival_forecast.strftime("%d/%m/%Y")
                    
                if 'redex_clearance' in locals():
                    process_data["redex_clearance"] = redex_clearance
            
            # Campos específicos para exportação rodoviária
            if 'export_type' in locals() and export_type == "Rodoviária":
                if 'cross_terminal' in locals():
                    process_data["cross_terminal"] = cross_terminal
                    
                if 'client_delivery_date' in locals() and client_delivery_date:
                    process_data["client_delivery_date"] = client_delivery_date.strftime("%d/%m/%Y")
                    
                if 'carrier' in locals():
                    process_data["carrier"] = carrier
        
        # Atualizar a configuração de dias por período
        if "config" not in st.session_state.data:
            st.session_state.data["config"] = {}
        st.session_state.data["config"]["storage_days_per_period"] = days_per_period
        
        # If editing, maintain the existing events
        if st.session_state.edit_mode:
            process_data["events"] = process.get("events", [])
            
            # Add an update event
            process_data["events"].append({
                "date": datetime.now().strftime("%d/%m/%Y"),
                "description": "Processo atualizado",
                "user": "Admin"
            })
            
            # Update the process
            if update_process(process_data):
                # Lidar com a atribuição de cliente no modo de edição
                if 'user_role' in st.session_state and st.session_state.user_role == 'admin':
                    # Se um cliente foi selecionado
                    if assigned_client:
                        # Verificar se o cliente é diferente do atual
                        from components.auth import get_client_for_process
                        current_client = get_client_for_process(process_data["id"])
                        
                        # Se não houver cliente atual ou o cliente selecionado for diferente
                        if not current_client or current_client.get("id") != assigned_client:
                            # Obter cliente
                            users = get_users()
                            client = next((c for c in users if c['id'] == assigned_client), None)
                            
                            if client:
                                # Atualizar a lista de processos do cliente
                                processes = client.get('processes', [])
                                if process_data["id"] not in processes:
                                    processes.append(process_data["id"])
                                    success, _ = assign_processes_to_client(assigned_client, processes)
                                    
                                    if success:
                                        # Adicionar evento ao processo
                                        add_event(process_data["id"], f"Processo atribuído ao cliente {client['name']}")
                                        st.success(f"Processo atualizado com sucesso e atribuído a {client['name']}!")
                                    else:
                                        st.success("Processo atualizado com sucesso, mas não foi possível atribuir ao cliente.")
                                else:
                                    st.success("Processo atualizado com sucesso!")
                            else:
                                st.success("Processo atualizado com sucesso!")
                        else:
                            st.success("Processo atualizado com sucesso!")
                    else:
                        # Se nenhum cliente foi selecionado, remover o processo dos clientes que possam tê-lo
                        from components.auth import load_users, save_users
                        users_data = load_users()
                        
                        # Verificar se algum cliente tem este processo
                        process_removed = False
                        for user in users_data.get('users', []):
                            if user['role'] == 'client' and 'processes' in user and process_data["id"] in user['processes']:
                                user['processes'].remove(process_data["id"])
                                process_removed = True
                        
                        if process_removed:
                            save_users(users_data)
                            add_event(process_data["id"], "Processo removido de cliente")
                            st.success("Processo atualizado com sucesso e desassociado de cliente!")
                        else:
                            st.success("Processo atualizado com sucesso!")
                else:
                    st.success("Processo atualizado com sucesso!")
                
                st.session_state.edit_mode = False
                navigate_function("home")
            else:
                st.error("Erro ao atualizar processo!")
        else:
            # Add a new process
            if add_process(process_data):
                new_process_id = process_data["id"] if process_data.get("id") else None
                
                # Se foi especificado um cliente e se for administrador
                if assigned_client and 'user_role' in st.session_state and st.session_state.user_role == 'admin':
                    # Obter cliente
                    users = get_users()
                    client = next((c for c in users if c['id'] == assigned_client), None)
                    
                    if client:
                        # Atualizar a lista de processos do cliente
                        processes = client.get('processes', [])
                        if new_process_id not in processes:
                            processes.append(new_process_id)
                            success, _ = assign_processes_to_client(assigned_client, processes)
                            
                            if success:
                                # Adicionar evento ao processo
                                add_event(new_process_id, f"Processo atribuído ao cliente {client['name']}")
                                st.success(f"Processo adicionado com sucesso e atribuído a {client['name']}!")
                            else:
                                st.warning(f"Processo adicionado, mas não foi possível atribuir ao cliente.")
                        else:
                            st.success(f"Processo adicionado com sucesso! (Já atribuído a {client['name']})")
                    else:
                        st.success("Processo adicionado com sucesso!")
                else:
                    st.success("Processo adicionado com sucesso!")
                
                navigate_function("home")
            else:
                st.error("Erro ao adicionar processo!")
    
    if cancel_button:
        st.session_state.edit_mode = False
        navigate_function("home")
