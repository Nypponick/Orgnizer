import streamlit as st
import pandas as pd
import os
from data import get_processes_df, get_process_by_id, delete_process, archive_process
from utils import export_to_excel, export_to_csv, get_status_color
from html_generator import generate_processes_table_html, get_download_link
from html_export_pagination import export_html_with_pagination

def display_home(navigate_function, filter_ids=None):
    """Display the home page with the processes table
    
    Args:
        navigate_function: Function to navigate between pages
        filter_ids: Optional list of process IDs to filter by (for client view)
    """
    st.header("Processos")
    
    # Get processes data first before we set up any UI
    df = get_processes_df()
    
    # Prepare status options based on existing data
    status_options = ["Em andamento", "Concluído", "Atrasado", "Pendente", "Cancelado", 
                      "Novo Processo", "Chegada do navio alterada", "Desembaraçado", 
                      "Documento entregue", "BL enviado"]
    
    # Se temos dados carregados, adicionar outros status que possam existir
    if not df.empty and 'status' in df.columns:
        # Extrair status únicos dos dados e adicionar à lista de opções
        for status in df['status'].unique():
            if status and status not in status_options:
                status_options.append(status)
                
    # Ordenar alfabeticamente para facilitar a localização
    status_options.sort()
    
    # Search and filter section
    if st.session_state.user_role == 'admin':
        col1, col2, col3, col4, col5 = st.columns([3, 2, 2, 2, 3])
    else:
        col1, col2, col3, col4 = st.columns([3, 2, 2, 2])
    
    with col1:
        search_term = st.text_input("Buscar processo", value=st.session_state.filter_value)
        st.session_state.filter_value = search_term
    
    with col2:
        processo_type_filter = st.selectbox(
            "Tipo de Processo",
            options=["Todos", "Importação", "Exportação"],
            index=0
        )
    
    with col3:
        # Mostrar o seletor de status com todas as opções
        status_filter = st.multiselect("Filtrar por status", status_options)
    
    with col4:
        date_range = st.date_input("Período", value=[], help="Selecione um intervalo de datas")
    
    # Adicionar filtro por cliente apenas para administradores
    client_filter = None
    if st.session_state.user_role == 'admin':
        with col5:  # Mudamos para a quinta coluna
            from components.auth import get_users
            users = get_users()
            clients = [user for user in users if user['role'] == 'client']
            
            # Opções para o dropdown de clientes
            client_options = ["Todos os clientes"]
            client_options.extend([f"{user['name']} ({user['email']})" for user in clients])
            
            # Dropdown para selecionar cliente
            selected_client = st.selectbox("Filtrar por cliente", client_options)
            
            # Se selecionou um cliente específico
            if selected_client != "Todos os clientes":
                # Encontrar o cliente correspondente
                selected_client_info = next((user for user in clients 
                                           if f"{user['name']} ({user['email']})" == selected_client), None)
                if selected_client_info:
                    client_filter = selected_client_info.get('processes', [])
    
    if df.empty:
        st.info("Nenhum processo encontrado. Adicione um novo processo clicando em 'Novo Processo'.")
        return
    
    # Apply filters
    filtered_df = df.copy()
    
    # Filtrar por IDs específicos (quando em modo cliente ou quando filtro por cliente é aplicado)
    if filter_ids is not None and len(filter_ids) > 0:
        # Filtro padrão para cliente
        filtered_df = filtered_df[filtered_df['id'].isin(filter_ids)]
    elif client_filter is not None and len(client_filter) > 0:
        # Filtro escolhido pelo administrador
        filtered_df = filtered_df[filtered_df['id'].isin(client_filter)]
    
    # Garantir que a coluna 'type' exista
    if 'type' not in filtered_df.columns:
        filtered_df['type'] = ''  # Adiciona coluna type se não existir

    # Adicionar coluna para exibição formatada do tipo de processo
    filtered_df['processo_tipo'] = filtered_df['type'].apply(
        lambda x: "Exportação" if x == "exportacao" else "Importação"
    )

    # Filtrar por tipo de processo
    if processo_type_filter != "Todos":
        if processo_type_filter == "Importação":
            # Filtrar processos de importação (type == "importacao" ou não definido/null)
            mask = (filtered_df['type'] == 'importacao') | (filtered_df['type'].isna()) | (filtered_df['type'] == '')
            filtered_df = filtered_df[mask]
        else:  # Exportação
            filtered_df = filtered_df[filtered_df['type'] == 'exportacao']
    
    if search_term:
        filter_condition = False
        for col in filtered_df.columns:
            filter_condition |= filtered_df[col].astype(str).str.contains(search_term, case=False, na=False)
        filtered_df = filtered_df[filter_condition]
    
    if status_filter:
        filtered_df = filtered_df[filtered_df['status'].isin(status_filter)]
        
    # Display export options
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.download_button(
            label="📥 Exportar para Excel",
            data=export_to_excel(filtered_df),
            file_name="processos_importacao_exportacao.xlsx",
            mime="application/vnd.ms-excel"
        )
    
    with col2:
        st.download_button(
            label="📄 Exportar para CSV",
            data=export_to_csv(filtered_df),
            file_name="processos_importacao_exportacao.csv",
            mime="text/csv"
        )
        
    with col3:
        # Botão para gerar HTML interativo
        if st.button("📊 Exportar HTML Interativo", use_container_width=True):
            # Definir informações do cliente selecionado para o HTML
            client_name = None
            export_process_ids = None
            client_logo = None
            
            # Caso 1: Cliente logado vendo seus processos
            if st.session_state.user_role == 'client':
                from components.auth import get_users
                all_users = get_users()
                current_user = next((user for user in all_users if user.get('id') == st.session_state.user_id), None)
                if current_user:
                    client_name = current_user.get('name', '')
                    export_process_ids = filter_ids
                    client_logo = current_user.get('logo_path')
                
            # Caso 2: Admin selecionou um cliente específico
            elif st.session_state.user_role == 'admin' and 'selected_client' in locals() and selected_client != "Todos os clientes":
                selected_client_info = next((user for user in clients 
                                         if f"{user['name']} ({user['email']})" == selected_client), None)
                if selected_client_info:
                    client_name = selected_client_info.get('name', '')
                    export_process_ids = selected_client_info.get('processes', [])
                    client_logo = selected_client_info.get('logo_path')
            
            with st.spinner("Gerando página HTML interativa com paginação..."):
                # Gerar HTML com a tabela interativa e paginação, mantendo o visual original
                filepath, filename = export_html_with_pagination(
                    filtered_df, 
                    process_ids=export_process_ids,
                    title="Relatório de Processos de Importação/Exportação",
                    include_details=True,
                    client_name=client_name,
                    client_logo=client_logo
                )
                
                if filepath:
                    href, name = get_download_link(filepath, filename)
                    if client_name:
                        st.success(f"Página HTML interativa para o cliente {client_name} gerada com sucesso!")
                    else:
                        st.success("Página HTML interativa gerada com sucesso!")
                    
                    st.markdown(
                        f'<a href="{href}" download="{name}" target="_blank">📥 Baixar página HTML interativa</a>',
                        unsafe_allow_html=True
                    )
    
    # Add styling to the status column
    def color_status(val):
        color = get_status_color(val)
        return f'background-color: {color}; color: white; border-radius: 50px; padding: 0.3rem 0.9rem; text-align: center; font-weight: 500; width: 90%; margin: auto; box-shadow: 0 1px 3px rgba(0,0,0,0.12), 0 1px 2px rgba(0,0,0,0.24);'
    
    # Display dataframe with styling (using .map instead of .applymap which is deprecated)
    # Configuração de colunas para renomear os campos
    column_configs = {
        "id": "Código",
        "status": "Status", 
        "processo_tipo": "Tipo de Processo",
        "po": "PO",
        "ref": "Referência",
        "origin": "Origem",
        "product": "Produto",
        "eta": "ETA",
        "free_time": "Free Time",
        "free_time_expiry": "Vencimento Free Time",
        "empty_return": "Devolução de Vazio",
        "map": "Mapa",
        "invoice_number": "Nota Fiscal",
        "port_entry_date": "Entrada no Porto/Recinto",
        "current_period_start": "Início do período atual",
        "current_period_expiry": "Vencimento do período",
        "storage_days": "Dias armazenados",
        "original_docs": "Documentos originais",
        # Campos específicos para exportação
        "cargo_deadline": "Deadline Carga",
        "deadline_draft": "Deadline Draft",
        "export_type": "Tipo de Exportação"
    }
    
    # Aplicar estilos às células usando Pandas Styler
    styled_df = filtered_df.style
    
    # Estilo para as células de status
    styled_df = styled_df.map(
        lambda x: color_status(x) if x else '',
        subset=['status']
    )
    
    # Estilo global para o alinhamento central de todas as células
    styled_df = styled_df.set_properties(**{
        'text-align': 'center',
        'font-size': '14px',
        'padding': '5px'
    })
    
    # Exibir o dataframe estilizado
    st.dataframe(
        styled_df,
        use_container_width=True,
        height=400,
        column_config=column_configs
    )
    
    # Action buttons for each row
    st.subheader("Ações")
    
    if not filtered_df.empty:
        col1, col2 = st.columns([1, 2])
        
        with col1:
            # Criar listas para as opções do dropdown e os IDs dos processos
            process_options = []
            process_ids = []
            
            for _, row in filtered_df.iterrows():
                process_id = row["id"]
                reference = row.get("ref", "")
                
                # Definir o texto de exibição:
                # 1. Mostrar a referência se existir
                # 2. Caso contrário, mostrar um texto especial indicando que não há referência
                if reference and reference.strip():
                    display_text = reference
                else:
                    display_text = f"Processo sem referência ({process_id})"
                
                process_options.append(display_text)
                process_ids.append(process_id)
            
            if process_options:
                # Criar dropdown com as opções de processo formatadas
                selected_index = st.selectbox("Selecione um processo", 
                                            range(len(process_options)), 
                                            format_func=lambda i: process_options[i])
                
                # Obter o process_id selecionado
                process_id = process_ids[selected_index]
            else:
                # Fallback case if the filtered list is empty
                st.info("Não há processos disponíveis para seleção.")
                process_id = None
        
        with col2:
            if st.button("👁️ Visualizar Detalhes", use_container_width=True):
                navigate_function("view_details", process_id)
        
        # Botões apenas para administradores
        if 'user_role' in st.session_state and st.session_state.user_role == 'admin':
            col1, col2, col3 = st.columns(3)
            
            with col1:
                if st.button("✏️ Editar Processo", use_container_width=True):
                    st.session_state.edit_mode = True
                    navigate_function("add_edit", process_id)
            
            with col2:
                # Delete process option (with confirmation)
                delete_button = st.button("🗑️ Excluir Processo", use_container_width=True, key="delete_process_button")
                
            with col3:
                # Archive process option
                archive_button = st.button("📦 Arquivar Processo", use_container_width=True, key="archive_process_button")
                if archive_button and process_id:
                    if archive_process(process_id):
                        st.success(f"Processo arquivado com sucesso!")
                        st.rerun()
                    else:
                        st.error("Erro ao arquivar o processo.")
        else:
            st.info("Como cliente, você pode apenas visualizar os detalhes dos processos.")
    else:
        st.info("Nenhum processo encontrado para exibir.")
    
    # Armazenar estado de confirmação na sessão
    if "confirm_delete" not in st.session_state:
        st.session_state.confirm_delete = False
    
    # Para evitar erro quando delete_button não existe (cliente)
    if 'delete_button' in locals() and delete_button:
        st.session_state.confirm_delete = True
    
    # Somente mostrar confirmação de exclusão para admin e quando temos um processo selecionado
    if 'user_role' in st.session_state and st.session_state.user_role == 'admin' and st.session_state.confirm_delete and 'process_id' in locals():
        st.warning("Tem certeza que deseja excluir este processo? Esta ação não pode ser desfeita.")
        col1, col2 = st.columns(2)
        
        with col1:
            confirm_button = st.button("✓ Confirmar Exclusão", use_container_width=True, key="confirm_delete_button")
            if confirm_button:
                if delete_process(process_id):
                    st.success("Processo excluído com sucesso!")
                    st.session_state.confirm_delete = False
                    st.rerun()
                else:
                    st.error("Erro ao excluir processo.")
        
        with col2:
            cancel_button = st.button("✗ Cancelar", use_container_width=True, key="cancel_delete_button")
            if cancel_button:
                st.session_state.confirm_delete = False
                st.rerun()
