import streamlit as st
import pandas as pd
import os
from data import get_processes_df, unarchive_process
from utils import export_to_excel, export_to_csv, get_status_color
from html_generator import generate_processes_table_html, get_download_link

def display_archived_processes(navigate_function, filter_ids=None):
    """Display the archived processes table
    
    Args:
        navigate_function: Function to navigate between pages
        filter_ids: Optional list of process IDs to filter by (for client view)
    """
    st.header("Processos Arquivados")
    
    # Get processes data with archived=True
    df = get_processes_df(include_archived=True)
    
    if df.empty:
        st.info("Não há processos arquivados.")
        return
    
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
    col1, col2, col3 = st.columns([3, 2, 2])
    
    with col1:
        search_term = st.text_input("Buscar processo arquivado", key="archived_search")
    
    with col2:
        processo_type_filter = st.selectbox(
            "Tipo de Processo",
            options=["Todos", "Importação", "Exportação"],
            index=0,
            key="archived_type_filter"
        )
    
    with col3:
        status_filter = st.selectbox(
            "Filtrar por status",
            options=["Todos"] + status_options,
            index=0,
            key="archived_status_filter"
        )
    
    # Export buttons
    export_option = None
    if st.session_state.user_role == 'admin':
        export_option = st.selectbox(
            "Exportar para",
            options=["Escolha um formato...", "Excel", "CSV", "HTML (interativo)"],
            index=0,
            key="archived_export_option"
        )
    
    # Filtrar por tipo de processo
    if processo_type_filter != "Todos" and not df.empty and 'type' in df.columns:
        filter_value = "importacao" if processo_type_filter == "Importação" else "exportacao"
        df = df[df['type'] == filter_value]
    
    # Filtrar por status
    if status_filter != "Todos" and not df.empty and 'status' in df.columns:
        df = df[df['status'] == status_filter]
    
    # Filtrar por termo de busca
    if search_term and not df.empty:
        search_result = pd.DataFrame()
        for col in df.columns:
            # Converte todos os valores da coluna para string para busca
            matches = df[df[col].astype(str).str.contains(search_term, case=False, na=False)]
            search_result = pd.concat([search_result, matches])
        
        # Remove duplicatas que podem ter sido geradas pelo método de busca
        df = search_result.drop_duplicates()
    
    # Filtrar por IDs específicos (para view de cliente)
    if filter_ids and not df.empty:
        df = df[df['id'].isin(filter_ids)]
    
    # Se não houver processos após os filtros, mostrar mensagem
    if df.empty:
        st.info("Não foram encontrados processos arquivados com os filtros aplicados.")
        return
    
    # Display the table
    st.subheader(f"Total de processos arquivados: {len(df)}")
    
    # Adicionar coluna com botões de ação
    if st.session_state.user_role == 'admin':
        # Criar a tabela com os dados
        st.write("Clique em um processo para restaurá-lo:")
    
    # Mostrar a tabela com processos
    def color_status(val):
        color = get_status_color(val)
        return f'background-color: {color}; border-radius: 50px; padding: 0.3rem 0.9rem; text-align: center; font-weight: 500; color: white; width: 90%; margin: auto; box-shadow: 0 1px 3px rgba(0,0,0,0.12), 0 1px 2px rgba(0,0,0,0.24);'
    
    # Apply the style only to the status column
    if 'status' in df.columns:
        styled_df = df.style.applymap(
            color_status, 
            subset=['status']
        )
    else:
        styled_df = df.style
    
    # Remover a coluna de ID para exibição
    display_df = df.drop(columns=['id']) if 'id' in df.columns else df
    
    # Criar tabela interativa com DataEditor
    edited_df = st.data_editor(
        display_df,
        hide_index=True,
        use_container_width=True,
        disabled=True,
        key="archived_table"
    )
    
    # Selecionar um processo
    selected_indices = st.multiselect("Selecione processos para restaurar:", df.index, format_func=lambda i: f"{df.iloc[i]['ref']} - {df.iloc[i]['po']}")
    
    if selected_indices and st.session_state.user_role == 'admin':
        btn_col1, btn_col2 = st.columns(2)
        
        with btn_col1:
            if st.button("Restaurar Processos Selecionados", use_container_width=True):
                for idx in selected_indices:
                    process_id = df.iloc[idx]['id']
                    success = unarchive_process(process_id)
                    if success:
                        st.success(f"Processo {df.iloc[idx]['ref']} restaurado com sucesso!")
                    else:
                        st.error(f"Erro ao restaurar processo {df.iloc[idx]['ref']}!")
                
                # Recarregar após executar as ações
                st.rerun()
    
    # Handle exports - similar ao componente home.py
    if st.session_state.user_role == 'admin' and export_option != "Escolha um formato...":
        if export_option == "Excel":
            excel_data = export_to_excel(df)
            st.download_button(
                label="Baixar Excel",
                data=excel_data,
                file_name="processos_arquivados.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                key="download_excel_archived"
            )
        elif export_option == "CSV":
            csv_data = export_to_csv(df)
            st.download_button(
                label="Baixar CSV",
                data=csv_data,
                file_name="processos_arquivados.csv",
                mime="text/csv",
                key="download_csv_archived"
            )
        elif export_option == "HTML (interativo)":
            # Gerar HTML interativo
            include_details = st.checkbox("Incluir detalhes completos", value=True, key="include_details_archived")
            if st.button("Gerar HTML", key="generate_html_archived"):
                filepath, rel_path = generate_processes_table_html(
                    filtered_df=df, 
                    include_details=include_details,
                    archived=True,
                    client_filter=None,
                    client_name=None
                )
                
                # Mostrar link de download
                st.success("HTML gerado com sucesso!")
                
                # Exibir link usando markdown com HTML
                download_html = get_download_link(filepath, os.path.basename(filepath) if filepath else "arquivo.html")
                st.markdown(download_html, unsafe_allow_html=True)
    
    # Rodapé informativo
    st.caption("Os processos arquivados não aparecem na lista principal de processos ativos.")