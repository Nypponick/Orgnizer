"""
Ferramenta para converter uma planilha do Google Sheets para o formato HTML do JGR Broker
"""

import pandas as pd
import streamlit as st
import os
import json
from datetime import datetime
from html_generator import generate_processes_table_html
from tempfile import NamedTemporaryFile
import io

def format_date(date_str):
    """Formata data para o formato brasileiro"""
    if pd.isna(date_str) or date_str == "":
        return ""
    try:
        # Tenta converter formato ISO
        date_obj = pd.to_datetime(date_str)
        return date_obj.strftime("%d/%m/%Y")
    except:
        # Se não conseguir, retorna o valor original
        return date_str

def convert_sheet_to_html():
    """Interface para converter planilha para HTML"""
    st.title("Converter Planilha para HTML")
    
    st.write("""
    Esta ferramenta permite converter dados de uma planilha Excel ou CSV para o formato HTML do JGR Broker.
    """)
    
    # Upload de arquivo
    uploaded_file = st.file_uploader("Faça upload da sua planilha", type=["xlsx", "csv"])
    
    if uploaded_file:
        # Determine file type based on extension
        file_extension = uploaded_file.name.split(".")[-1].lower()
        
        try:
            # Parse the file based on its type
            if file_extension == "csv":
                df = pd.read_csv(uploaded_file)
            else:  # xlsx
                df = pd.read_excel(uploaded_file)
            
            # Preview data
            st.subheader("Pré-visualização dos dados")
            st.dataframe(df.head())
            
            # Check if required columns exist
            required_columns = ["id", "ref", "status", "type"]
            missing_columns = [col for col in required_columns if col not in df.columns]
            
            if missing_columns:
                st.error(f"Colunas obrigatórias ausentes: {', '.join(missing_columns)}")
                st.write("As colunas obrigatórias são: id, ref, status, type")
                return
            
            # Format dates
            date_columns = [
                'eta', 'free_time_expiry', 'empty_return', 'port_entry_date',
                'current_period_start', 'current_period_expiry', 'return_date',
                'created_at', 'last_update', 'deadline'
            ]
            
            for col in date_columns:
                if col in df.columns:
                    df[col] = df[col].apply(lambda x: format_date(x) if not pd.isna(x) else "")
            
            # Convert dataframe to dictionary format expected by HTML generator
            processes = []
            for _, row in df.iterrows():
                process = {}
                for col in df.columns:
                    if col == 'events':
                        # Handle events as special case
                        process[col] = json.loads(row[col]) if not pd.isna(row[col]) else []
                    else:
                        # Convert nan to empty string
                        value = row[col]
                        if pd.isna(value):
                            value = ""
                        if isinstance(value, float):
                            if pd.isna(value):
                                value = ""
                            elif value.is_integer():
                                value = int(value)
                        process[col] = value
                
                # Ensure events field exists
                if 'events' not in process:
                    process['events'] = []
                
                # Ensure type field exists and has default value for backward compatibility
                if 'type' not in process or not process['type']:
                    process['type'] = "importacao"  # Default to importacao if not specified
                
                processes.append(process)
            
            # Options for HTML generation
            st.subheader("Opções de Exportação")
            
            col1, col2 = st.columns(2)
            with col1:
                include_details = st.checkbox("Incluir detalhes", value=True)
            with col2:
                client_name = st.text_input("Nome do cliente (opcional)")
            
            process_type_filter = st.radio(
                "Filtrar por tipo de processo:",
                ["Todos", "Importação", "Exportação"],
                horizontal=True
            )
            
            # Generate HTML button
            if st.button("Gerar HTML"):
                # Filter by type if needed
                filtered_processes = processes
                if process_type_filter == "Importação":
                    filtered_processes = [p for p in processes if p.get('type') != 'exportacao']
                elif process_type_filter == "Exportação":
                    filtered_processes = [p for p in processes if p.get('type') == 'exportacao']
                
                # Convert to dataframe expected by generator
                filtered_df = pd.DataFrame(filtered_processes)
                
                # Generate HTML
                try:
                    filepath, relative_url = generate_processes_table_html(
                        filtered_df=filtered_df,
                        include_details=include_details,
                        client_name=client_name if client_name else None
                    )
                    
                    # Show success message with download link
                    st.success(f"HTML gerado com sucesso!")
                    
                    # Read file for download
                    if filepath and os.path.exists(filepath):
                        with open(filepath, 'r', encoding='utf-8') as f:
                            html_content = f.read()
                        
                        # Create download button
                        st.download_button(
                            label="Baixar HTML",
                            data=html_content,
                            file_name=os.path.basename(filepath),
                            mime="text/html"
                        )
                    else:
                        st.error("Erro: Arquivo HTML não encontrado ou não foi gerado corretamente.")
                    
                    # Show preview
                    if 'html_content' in locals():
                        with st.expander("Pré-visualização do HTML"):
                            st.markdown(f'<iframe srcdoc="{html_content.replace(chr(34), "&quot;")}" width="100%" height="500"></iframe>', unsafe_allow_html=True)
                    
                except Exception as e:
                    st.error(f"Erro ao gerar HTML: {str(e)}")
        
        except Exception as e:
            st.error(f"Erro ao processar o arquivo: {str(e)}")

def create_template_file():
    """Cria um arquivo de modelo Excel para preenchimento"""
    st.subheader("Baixar Modelo de Planilha")
    
    st.write("""
    Use este modelo para preencher seus dados. Após preencher, 
    faça upload do arquivo usando o seletor acima.
    """)
    
    # Dados para o template
    data = {
        # Required fields
        'id': ['PROC-001', 'PROC-002'],
        'ref': ['REF123', 'REF456'],
        'status': ['em_andamento', 'concluido'],
        'type': ['importacao', 'exportacao'],
        
        # Common fields
        'po': ['PO-123', 'PO-456'],
        'product': ['Produto A', 'Produto B'],
        'origin': ['China', 'EUA'],
        'eta': ['2023-01-15', '2023-02-20'],
        'container': ['CONT123', 'CONT456'],
        'invoice': ['INV-001', 'INV-002'],
        'observations': ['Observação 1', 'Observação 2'],
        
        # Import specific
        'free_time': [7, 10],
        'free_time_expiry': ['2023-01-22', ''],
        'empty_return': ['2023-01-25', ''],
        'map': ['MAP123', ''],
        'port_entry_date': ['2023-01-16', ''],
        'current_period_start': ['2023-01-16', ''],
        'current_period_expiry': ['2023-01-26', ''],
        'storage_days': [10, 0],
        'di': ['DI-12345', ''],
        
        # Export specific
        'deadline': ['', '2023-03-01'],
        'importer': ['', 'Empresa XYZ'],
        
        # Control data
        'created_at': ['2023-01-01', '2023-01-05'],
        'last_update': ['2023-01-10', '2023-02-01']
    }
    
    # Adicionar eventos
    data['events'] = [
        '[{"date": "01/01/2023", "description": "Processo criado", "user": "Admin"}]',
        '[{"date": "05/01/2023", "description": "Processo atualizado", "user": "Admin"}]'
    ]
    
    # Criar o DataFrame
    template_df = pd.DataFrame(data)
    
    # Convert to Excel for download
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        template_df.to_excel(writer, index=False, sheet_name='Processos')
        
        # Get workbook and worksheet objects
        workbook = writer.book
        worksheet = writer.sheets['Processos']
        
        # Add format for headers
        header_format = workbook.add_format({
            'bold': True,
            'text_wrap': True,
            'valign': 'top',
            'bg_color': '#D8E4BC',
            'border': 1
        })
        
        # Apply header format
        for col_num, value in enumerate(template_df.columns.values):
            worksheet.write(0, col_num, value, header_format)
            
        # Set column widths
        for i, col in enumerate(template_df.columns):
            width = max(len(col) + 2, template_df[col].astype(str).map(len).max() + 2)
            worksheet.set_column(i, i, width)
    
    # Reset pointer to beginning of stream
    output.seek(0)
    
    # Create download button
    st.download_button(
        label="📥 Baixar Modelo Excel",
        data=output,
        file_name="modelo_jgr_broker.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    
    st.write("""
    ### Orientações para preenchimento:
    
    1. **Campos obrigatórios**: id, ref, status, type
    2. **Tipos de processo**: 'importacao' ou 'exportacao'
    3. **Status disponíveis**: 'em_andamento', 'concluido', 'pendente', 'atrasado', 'cancelado', etc.
    4. **Datas**: Use o formato YYYY-MM-DD (serão convertidas para o formato brasileiro)
    5. **Events**: Campo opcional no formato JSON (mantenha como está se não souber como editar)
    """)

if __name__ == "__main__":
    st.set_page_config(
        page_title="Converter Planilha para HTML - JGR Broker",
        page_icon="📊",
        layout="wide"
    )
    
    tab1, tab2 = st.tabs(["Converter Planilha", "Baixar Modelo"])
    
    with tab1:
        convert_sheet_to_html()
    
    with tab2:
        create_template_file()