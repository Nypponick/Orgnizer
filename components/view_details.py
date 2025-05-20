import streamlit as st
import pandas as pd
from datetime import datetime

from data import get_process_by_id, add_event
from components.event_log import display_event_log
from utils import format_date, get_status_color
from components.auth import get_users, assign_processes_to_client, get_client_for_process
from html_generator import generate_process_html, get_download_link

def display_detail_view(navigate_function):
    """Display detailed view of a process"""
    process_id = st.session_state.selected_process
    process = get_process_by_id(process_id)
    
    if process is None:
        st.error("Processo não encontrado!")
        if st.button("← Voltar para a lista de processos"):
            navigate_function("home")
        return
    
    # Botão X para fechar o detalhamento (posicionado no canto superior direito)
    close_btn_col1, close_btn_col2 = st.columns([0.95, 0.05])
    with close_btn_col2:
        if st.button("❌", help="Fechar detalhamento"):
            navigate_function("home")
            return
    
    # Title with process ID and status
    col1, col2 = st.columns([3, 1])
    
    with col1:
        # Determinar o tipo de processo (importação ou exportação)
        processo_tipo = process.get('type', 'importacao')
        tipo_texto = "Exportação" if processo_tipo == "exportacao" else "Importação"
        st.header(f"Processo de {tipo_texto} - {process['id']}")
        st.caption(f"Referência: {process.get('ref', '')}")
    
    with col2:
        status = process.get('status', 'Em andamento')
        status_color = get_status_color(status)
        st.markdown(f"""
        <div style="background-color: {status_color}; color: white; padding: 10px; 
        border-radius: 5px; text-align: center; font-weight: bold;">
            {status}
        </div>
        """, unsafe_allow_html=True)
    
    # Main information in tabs
    if st.session_state.user_role == 'admin':
        tab1, tab2, tab3, tab4 = st.tabs(["Informações Gerais", "Eventos", "Documentos", "Atribuição"])
    else:
        tab1, tab2, tab3 = st.tabs(["Informações Gerais", "Eventos", "Documentos"])
    
    # Tab 1: General Information
    with tab1:
        # Display process details in a structured way
        st.markdown("""
        <div class="info-panel">
            <h3 class="info-panel-title">Detalhes do Processo</h3>
        """, unsafe_allow_html=True)
        
        # First row: Basic info
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown('<div class="field-label">Código:</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="data-value">{process.get("id", "")}</div>', unsafe_allow_html=True)
            
            st.markdown('<div class="field-label">Referência:</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="data-value">{process.get("ref", "")}</div>', unsafe_allow_html=True)
            
            st.markdown('<div class="field-label">PO:</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="data-value">{process.get("po", "")}</div>', unsafe_allow_html=True)
        
        with col2:
            st.markdown('<div class="field-label">Invoice:</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="data-value">{process.get("invoice", "")}</div>', unsafe_allow_html=True)
            
            st.markdown('<div class="field-label">Origem:</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="data-value">{process.get("origin", "")}</div>', unsafe_allow_html=True)
            
            st.markdown('<div class="field-label">Produto:</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="data-value">{process.get("product", "")}</div>', unsafe_allow_html=True)
        
        with col3:
            st.markdown('<div class="field-label">Tipo de Processo:</div>', unsafe_allow_html=True)
            tipo_processo = "Importação" if process.get("type", "importacao") == "importacao" else "Exportação"
            st.markdown(f'<div class="data-value">{tipo_processo}</div>', unsafe_allow_html=True)
            
            st.markdown('<div class="field-label">Tipo de Container:</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="data-value">{process.get("container_type", "")}</div>', unsafe_allow_html=True)
            
            # ETA para importação, ETD para exportação
            if process.get("type", "importacao") == "importacao":
                st.markdown('<div class="field-label">ETA:</div>', unsafe_allow_html=True)
            else:
                st.markdown('<div class="field-label">ETD:</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="data-value">{format_date(process.get("eta", ""))}</div>', unsafe_allow_html=True)
            
            st.markdown('<div class="field-label">Status:</div>', unsafe_allow_html=True)
            status_color = get_status_color(process.get('status', ''))
            st.markdown(f'<div class="status-indicator" style="background-color: {status_color};">{process.get("status", "")}</div>', unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Second row: Shipping info
        if process.get("type", "importacao") == "importacao":
            st.markdown("""
            <div class="info-panel">
                <h3 class="info-panel-title">Informações de Embarque</h3>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="info-panel">
                <h3 class="info-panel-title">Informações de Exportação</h3>
            """, unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if process.get("type", "importacao") == "importacao":
                st.markdown('<div class="field-label">Exportador:</div>', unsafe_allow_html=True)
            else:
                st.markdown('<div class="field-label">Embarcador:</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="data-value">{process.get("exporter", "")}</div>', unsafe_allow_html=True)
            
            st.markdown('<div class="field-label">Navio:</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="data-value">{process.get("ship", "")}</div>', unsafe_allow_html=True)
            
            st.markdown('<div class="field-label">Agente:</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="data-value">{process.get("agent", "")}</div>', unsafe_allow_html=True)
        
        with col2:
            st.markdown('<div class="field-label">Número B/L:</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="data-value">{process.get("bl_number", "")}</div>', unsafe_allow_html=True)
            
            st.markdown('<div class="field-label">Container:</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="data-value">{process.get("container", "")}</div>', unsafe_allow_html=True)
            
            if process.get("type", "importacao") == "importacao":
                st.markdown('<div class="field-label">Previsão de Chegada:</div>', unsafe_allow_html=True)
            else:
                st.markdown('<div class="field-label">Deadline:</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="data-value">{format_date(process.get("arrival_date", ""))}</div>', unsafe_allow_html=True)
        
        with col3:
            st.markdown('<div class="field-label">Free Time:</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="data-value">{process.get("free_time", "")} dias</div>', unsafe_allow_html=True)
            
            st.markdown('<div class="field-label">Vencimento Free Time:</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="data-value">{format_date(process.get("free_time_expiry", ""))}</div>', unsafe_allow_html=True)
            
            st.markdown('<div class="field-label">Devolução de Vazio:</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="data-value">{format_date(process.get("empty_return", ""))}</div>', unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Third row: Storage info
        if process.get("type", "importacao") == "importacao":
            st.markdown("""
            <div class="info-panel">
                <h3 class="info-panel-title">Informações de Armazenagem</h3>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="info-panel">
                <h3 class="info-panel-title">Informações de Terminal</h3>
            """, unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown('<div class="field-label">Terminal:</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="data-value">{process.get("terminal", "")}</div>', unsafe_allow_html=True)
            
            if process.get("type", "importacao") == "importacao":
                st.markdown('<div class="field-label">Entrada no Porto/Recinto:</div>', unsafe_allow_html=True)
            else:
                st.markdown('<div class="field-label">Data de Entrega:</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="data-value">{format_date(process.get("port_entry_date", ""))}</div>', unsafe_allow_html=True)
        
        with col2:
            st.markdown('<div class="field-label">Início do Período Atual:</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="data-value">{format_date(process.get("current_period_start", ""))}</div>', unsafe_allow_html=True)
            
            st.markdown('<div class="field-label">Vencimento do Período:</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="data-value">{format_date(process.get("current_period_expiry", ""))}</div>', unsafe_allow_html=True)
        
        with col3:
            st.markdown('<div class="field-label">Dias Armazenados:</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="data-value">{process.get("storage_days", "0")}</div>', unsafe_allow_html=True)
            
            st.markdown('<div class="field-label">Mapa:</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="data-value">{process.get("map", "")}</div>', unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Fourth row: Documents info
        st.markdown("""
        <div class="info-panel">
            <h3 class="info-panel-title">Documentos e Informações Adicionais</h3>
        """, unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown('<div class="field-label">Nota Fiscal:</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="data-value">{process.get("invoice_number", "")}</div>', unsafe_allow_html=True)
            
            if process.get("type", "importacao") == "importacao":
                st.markdown('<div class="field-label">D.I.:</div>', unsafe_allow_html=True)
            else:
                st.markdown('<div class="field-label">DU-E:</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="data-value">{process.get("di", "")}</div>', unsafe_allow_html=True)
        
        with col2:
            st.markdown('<div class="field-label">Documentos Originais:</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="data-value">{process.get("original_docs", "")}</div>', unsafe_allow_html=True)
            
            st.markdown('<div class="field-label">Data de Devolução:</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="data-value">{format_date(process.get("return_date", ""))}</div>', unsafe_allow_html=True)
        
        with col3:
            if process.get("type", "importacao") == "exportacao":
                st.markdown('<div class="field-label">Importador:</div>', unsafe_allow_html=True)
                st.markdown(f'<div class="data-value">{process.get("importer", "")}</div>', unsafe_allow_html=True)
            
            st.markdown('<div class="field-label">Última Atualização:</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="data-value">{format_date(process.get("last_update", ""))}</div>', unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Observations
        st.markdown("""
        <div class="info-panel">
            <h3 class="info-panel-title">Observações</h3>
        """, unsafe_allow_html=True)
        
        observations = process.get('observations', '')
        st.markdown(f'<div class="data-value" style="min-height: 100px;">{observations}</div>', unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Seção específica para Exportação
        if process.get("type", "importacao") == "exportacao":
            st.markdown("""
            <div class="info-panel">
                <h3 class="info-panel-title">Informações Específicas de Exportação</h3>
            """, unsafe_allow_html=True)
            
            # Informação do tipo de exportação (Marítima/Rodoviária)
            export_type = process.get("export_type", "Marítima")
            st.markdown(f'<div class="info-type" style="margin-bottom: 15px; font-weight: bold;">Tipo de Exportação: <span style="color: #2c3e50;">{export_type}</span></div>', unsafe_allow_html=True)
            
            col1, col2, col3 = st.columns(3)
            
            # Campos básicos de documentação de exportação
            with col1:
                st.markdown('<div class="field-label">Data de Registro da DU-E:</div>', unsafe_allow_html=True)
                st.markdown(f'<div class="data-value">{format_date(process.get("due_date", ""))}</div>', unsafe_allow_html=True)
                
                st.markdown('<div class="field-label">Valor do Despacho:</div>', unsafe_allow_html=True)
                st.markdown(f'<div class="data-value">{process.get("dispatch_value", "")}</div>', unsafe_allow_html=True)
            
            with col2:
                st.markdown('<div class="field-label">Número do Conhecimento:</div>', unsafe_allow_html=True)
                st.markdown(f'<div class="data-value">{process.get("knowledge_number", "")}</div>', unsafe_allow_html=True)
                
                st.markdown('<div class="field-label">Data do Conhecimento:</div>', unsafe_allow_html=True)
                st.markdown(f'<div class="data-value">{format_date(process.get("knowledge_date", ""))}</div>', unsafe_allow_html=True)
            
            with col3:
                st.markdown('<div class="field-label">Data de Averbação:</div>', unsafe_allow_html=True)
                st.markdown(f'<div class="data-value">{format_date(process.get("endorsement_date", ""))}</div>', unsafe_allow_html=True)
                
                st.markdown('<div class="field-label">Drawback:</div>', unsafe_allow_html=True)
                st.markdown(f'<div class="data-value">{process.get("drawback", "")}</div>', unsafe_allow_html=True)
            
            # Subseção específica para Exportação Marítima
            if export_type == "Marítima":
                st.markdown('<div style="margin-top: 20px; margin-bottom: 10px; font-weight: bold; border-bottom: 1px solid #eee; padding-bottom: 5px;">Detalhes de Exportação Marítima</div>', unsafe_allow_html=True)
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.markdown('<div class="field-label">Deadline Carga:</div>', unsafe_allow_html=True)
                    st.markdown(f'<div class="data-value">{format_date(process.get("cargo_deadline", ""))}</div>', unsafe_allow_html=True)
                    
                    st.markdown('<div class="field-label">Deadline Draft:</div>', unsafe_allow_html=True)
                    st.markdown(f'<div class="data-value">{format_date(process.get("deadline_draft", ""))}</div>', unsafe_allow_html=True)
                
                with col2:
                    st.markdown('<div class="field-label">Terminal de Embarque:</div>', unsafe_allow_html=True)
                    st.markdown(f'<div class="data-value">{process.get("shipping_terminal", "")}</div>', unsafe_allow_html=True)
                    
                    st.markdown('<div class="field-label">Data de Embarque:</div>', unsafe_allow_html=True)
                    st.markdown(f'<div class="data-value">{format_date(process.get("shipping_date", ""))}</div>', unsafe_allow_html=True)
                
                with col3:
                    st.markdown('<div class="field-label">Previsão de Chegada:</div>', unsafe_allow_html=True)
                    st.markdown(f'<div class="data-value">{format_date(process.get("arrival_forecast", ""))}</div>', unsafe_allow_html=True)
                    
                    st.markdown('<div class="field-label">Desembaraço REDEX:</div>', unsafe_allow_html=True)
                    st.markdown(f'<div class="data-value">{process.get("redex_clearance", "Não")}</div>', unsafe_allow_html=True)
            
            # Subseção específica para Exportação Rodoviária
            elif export_type == "Rodoviária":
                st.markdown('<div style="margin-top: 20px; margin-bottom: 10px; font-weight: bold; border-bottom: 1px solid #eee; padding-bottom: 5px;">Detalhes de Exportação Rodoviária</div>', unsafe_allow_html=True)
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.markdown('<div class="field-label">Terminal de Cruze:</div>', unsafe_allow_html=True)
                    st.markdown(f'<div class="data-value">{process.get("cross_terminal", "")}</div>', unsafe_allow_html=True)
                
                with col2:
                    st.markdown('<div class="field-label">Data de Entrega no Cliente:</div>', unsafe_allow_html=True)
                    st.markdown(f'<div class="data-value">{format_date(process.get("client_delivery_date", ""))}</div>', unsafe_allow_html=True)
                
                with col3:
                    st.markdown('<div class="field-label">Transportadora:</div>', unsafe_allow_html=True)
                    st.markdown(f'<div class="data-value">{process.get("carrier", "")}</div>', unsafe_allow_html=True)
            
            # Final da subseção específica para informações de rastreamento de todos os tipos de exportação
            st.markdown('<div style="margin-top: 20px; margin-bottom: 10px; font-weight: bold; border-bottom: 1px solid #eee; padding-bottom: 5px;">Informações de Rastreio</div>', unsafe_allow_html=True)
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown('<div class="field-label">Data de Envio dos Originais:</div>', unsafe_allow_html=True)
                st.markdown(f'<div class="data-value">{format_date(process.get("originals_sent_date", ""))}</div>', unsafe_allow_html=True)
            
            with col2:
                st.markdown('<div class="field-label">Número do Rastreio:</div>', unsafe_allow_html=True)
                st.markdown(f'<div class="data-value">{process.get("tracking_number", "")}</div>', unsafe_allow_html=True)
            
            st.markdown('</div>', unsafe_allow_html=True)
    
    # Tab 2: Events log
    with tab2:
        display_event_log(process)
        
        # Add new event
        st.subheader("Adicionar Novo Evento")
        with st.form("add_event_form"):
            event_description = st.text_area("Descrição do Evento", height=100)
            
            col1, col2 = st.columns(2)
            
            with col1:
                submit = st.form_submit_button("Adicionar Evento", use_container_width=True)
            
            with col2:
                cancel = st.form_submit_button("Cancelar", use_container_width=True)
        
        if submit and event_description:
            # A função add_event foi modificada para incluir geração de ID único
            if add_event(process_id, event_description):
                st.success("Evento adicionado com sucesso!")
                st.rerun()
            else:
                st.error("Erro ao adicionar evento!")
    
    # Tab 3: Documents
    with tab3:
        st.info("Funcionalidade de documentos será implementada em uma versão futura.")
    
    # Tab 4: Atribuição de cliente (apenas para admin)
    if st.session_state.user_role == 'admin' and 'tab4' in locals():
        with tab4:
            st.subheader("Atribuir processo a um cliente")
            
            # Obter o cliente atual do processo (se houver)
            current_client = get_client_for_process(process_id)
            
            # Obter lista de clientes
            users = get_users()
            clients = [user for user in users if user['role'] == 'client']
            
            if not clients:
                st.warning("Não há clientes cadastrados. Adicione clientes na seção de Usuários para poder atribuir processos.")
            else:
                # Exibir cliente atual
                st.subheader("Cliente atual")
                if current_client:
                    st.success(f"Este processo está atribuído a: **{current_client['name']}** ({current_client['email']})")
                else:
                    st.info("Este processo não está atribuído a nenhum cliente")
                
                # Formulário para atribuir a outro cliente
                st.subheader("Atribuir a outro cliente")
                
                with st.form("assign_client_form"):
                    # Lista de clientes
                    client_options = [(user['id'], f"{user['name']} ({user['email']})") for user in clients]
                    client_ids = [id for id, _ in client_options]
                    client_labels = [label for _, label in client_options]
                    
                    # Selecionar cliente
                    selected_index = 0
                    if current_client:
                        try:
                            selected_index = client_ids.index(current_client['id'])
                        except ValueError:
                            selected_index = 0
                    
                    selected_client = st.selectbox("Selecione um cliente", client_labels, index=selected_index)
                    selected_client_id = client_ids[client_labels.index(selected_client)]
                    
                    # Botões
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        assign_btn = st.form_submit_button("Atribuir Processo", use_container_width=True)
                    
                    with col2:
                        remove_btn = st.form_submit_button("Remover Atribuição", use_container_width=True)
                
                # Processar atribuição
                if assign_btn:
                    # Obter processos atuais do cliente
                    client = next((c for c in clients if c['id'] == selected_client_id), None)
                    processes = client.get('processes', [])
                    
                    # Adicionar processo se ainda não estiver associado
                    if process_id not in processes:
                        processes.append(process_id)
                        success, message = assign_processes_to_client(selected_client_id, processes)
                        if success:
                            st.success(f"Processo atribuído com sucesso a {client['name']}!")
                            # Adicionar evento ao processo
                            add_event(process_id, f"Processo atribuído ao cliente {client['name']}")
                            st.rerun()
                        else:
                            st.error(f"Erro ao atribuir processo: {message}")
                    else:
                        st.info(f"Este processo já está associado ao cliente {client['name']}")
                
                # Remover atribuição
                if remove_btn and current_client:
                    processes = current_client.get('processes', [])
                    if process_id in processes:
                        processes.remove(process_id)
                        success, message = assign_processes_to_client(current_client['id'], processes)
                        if success:
                            st.success(f"Processo removido com sucesso de {current_client['name']}!")
                            # Adicionar evento ao processo
                            add_event(process_id, f"Processo removido do cliente {current_client['name']}")
                            st.rerun()
                        else:
                            st.error(f"Erro ao remover processo: {message}")
                    else:
                        st.info("Este processo não está associado ao cliente selecionado")
    
    # Action buttons
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("← Voltar para a lista", use_container_width=True):
            navigate_function("home")
    
    with col2:
        if st.button("✏️ Editar Processo", use_container_width=True):
            st.session_state.edit_mode = True
            navigate_function("add_edit", process_id)
    
    with col3:
        # Botão para exportar HTML
        if st.button("📄 Exportar HTML", use_container_width=True):
            with st.spinner("Gerando arquivo HTML..."):
                filepath, filename = generate_process_html(process_id, include_details=True)
                if filepath:
                    href, name = get_download_link(filepath, filename)
                    st.success("Arquivo HTML gerado com sucesso!")
                    st.markdown(
                        f'<a href="{href}" download="{name}" target="_blank">📥 Baixar arquivo HTML</a>',
                        unsafe_allow_html=True
                    )
