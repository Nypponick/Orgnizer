import streamlit as st
import pandas as pd
from data import get_process_by_id
from utils import format_date, get_status_color
from components.event_log import display_event_log
from html_generator import generate_process_html, get_download_link

def display_client_view(process_id):
    """Display a client-facing view of a process"""
    process = get_process_by_id(process_id)
    
    if process is None:
        st.error("Processo não encontrado!")
        return
    
    # Title with process ID and status
    col1, col2, col3 = st.columns([3, 1, 1])
    
    with col1:
        process_type = "Exportação" if process.get('type', '') == "exportacao" else "Importação"
        st.header(f"Processo de {process_type} - {process['id']}")
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
    
    with col3:
        # Gerar HTML do processo e oferecer download
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
    
    # Main information in tabs
    tab1, tab2 = st.tabs(["Informações Gerais", "Eventos"])
    
    # Tab 1: General Information
    with tab1:
        # Display process details in a structured way
        st.subheader("Detalhes do Processo")
        
        # First row: Basic info
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("**Código:**")
            st.markdown(process.get('id', ''))
            
            st.markdown("**Referência:**")
            st.markdown(process.get('ref', ''))
            
            st.markdown("**PO:**")
            st.markdown(process.get('po', ''))
        
        with col2:
            st.markdown("**Invoice:**")
            st.markdown(process.get('invoice', ''))
            
            st.markdown("**Origem:**")
            st.markdown(process.get('origin', ''))
            
            st.markdown("**Produto:**")
            st.markdown(process.get('product', ''))
        
        with col3:
            st.markdown("**Tipo:**")
            st.markdown(process.get('type', ''))
            
            st.markdown("**ETA:**")
            st.markdown(format_date(process.get('eta', '')))
            
            st.markdown("**Status:**")
            st.markdown(process.get('status', ''))
        
        st.divider()
        
        # Second row: Shipping info
        st.subheader("Informações de Embarque")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("**Exportador:**")
            st.markdown(process.get('exporter', ''))
            
            st.markdown("**Navio:**")
            st.markdown(process.get('ship', ''))
            
            st.markdown("**Agente:**")
            st.markdown(process.get('agent', ''))
        
        with col2:
            st.markdown("**Número B/L:**")
            st.markdown(process.get('bl_number', ''))
            
            st.markdown("**Container:**")
            st.markdown(process.get('container', ''))
            
            st.markdown("**Previsão de Chegada:**")
            st.markdown(format_date(process.get('arrival_date', '')))
        
        with col3:
            st.markdown("**Free Time:**")
            st.markdown(f"{process.get('free_time', '')} dias")
            
            st.markdown("**Vencimento Free Time:**")
            st.markdown(format_date(process.get('free_time_expiry', '')))
            
            st.markdown("**Devolução de Vazio:**")
            st.markdown(format_date(process.get('empty_return', '')))
        
        st.divider()
        
        # Third row: Storage info
        st.subheader("Informações de Armazenagem")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("**Terminal:**")
            st.markdown(process.get('terminal', ''))
            
            st.markdown("**Entrada no Porto/Recinto:**")
            st.markdown(format_date(process.get('port_entry_date', '')))
        
        with col2:
            st.markdown("**Início do Período Atual:**")
            st.markdown(format_date(process.get('current_period_start', '')))
            
            st.markdown("**Vencimento do Período:**")
            st.markdown(format_date(process.get('current_period_expiry', '')))
        
        with col3:
            st.markdown("**Dias Armazenados:**")
            st.markdown(process.get('storage_days', '0'))
            
            st.markdown("**Mapa:**")
            st.markdown(process.get('map', ''))
        
        st.divider()
        
        # Fourth row: Documents info
        st.subheader("Documentos e Informações Adicionais")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("**Nota Fiscal:**")
            st.markdown(process.get('invoice_number', ''))
            
            st.markdown("**D.I.:**")
            st.markdown(process.get('di', ''))
        
        with col2:
            st.markdown("**Documentos Originais:**")
            st.markdown(process.get('original_docs', ''))
            
            st.markdown("**Data de Devolução:**")
            st.markdown(format_date(process.get('return_date', '')))
        
        with col3:
            st.markdown("**Última Atualização:**")
            st.markdown(format_date(process.get('last_update', '')))
        
        st.divider()
        
        # Observations
        st.subheader("Observações")
        st.text_area("Observações", value=process.get('observations', ''), disabled=True, height=100, label_visibility="collapsed")
    
    # Tab 2: Events log (read-only)
    with tab2:
        display_event_log(process)