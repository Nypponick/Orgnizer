"""
Módulo para exportação de HTML com paginação
"""
import streamlit as st
from new_html_generator import generate_html_report

def generate_html_with_pagination(filtered_df=None, process_ids=None, title="Relatório de Processos", include_details=True, client_filter=None, client_name=None, archived=False):
    """
    Gera um arquivo HTML contendo uma tabela de processos com paginação.
    
    Args:
        filtered_df: DataFrame com os processos filtrados (opcional)
        process_ids: Lista de IDs de processos para incluir (opcional)
        title: Título do relatório
        include_details: Se True, inclui a seção de detalhes
        client_filter: ID do cliente para filtrar processos (opcional)
        client_name: Nome do cliente para personalizar o relatório (opcional)
        archived: Se True, indica que estamos gerando relatório para processos arquivados
        
    Returns:
        tuple: (caminho do arquivo gerado, URL relativo)
    """
    try:
        # Usar o novo gerador com paginação
        filepath, filename = generate_html_report(
            filtered_df=filtered_df, 
            process_ids=process_ids,
            title=title,
            include_details=include_details,
            client_filter=client_filter,
            client_name=client_name,
            archived=archived
        )
        return filepath, filename
    except Exception as e:
        st.error(f"Erro ao gerar HTML: {str(e)}")
        return None, None

# Para manter compatibilidade com o código existente
def get_download_link(filepath, filename):
    """
    Cria um link para download do arquivo HTML gerado.
    
    Args:
        filepath: Caminho completo do arquivo
        filename: Nome do arquivo para exibição
        
    Returns:
        tuple: (URL, nome do arquivo)
    """
    return f"/{filename}", filename