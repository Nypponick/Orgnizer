"""
Gerador de HTML para exportar processos
"""
import os
import base64
from datetime import datetime
from data import get_process_by_id, get_processes_df
from utils import format_date, get_status_color
from custom_html_styles import get_html_styles
from html_export_styles import get_basic_styles
from inline_mobile_styles import get_mobile_styles


def get_base64_encoded_image(image_path):
    """
    Converte uma imagem para formato base64 para inserção em HTML.
    
    Args:
        image_path: Caminho para o arquivo de imagem
        
    Returns:
        str: String codificada em base64 da imagem
    """
    if not image_path or not os.path.exists(image_path):
        return ""
    
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode('utf-8')

HTML_EXPORTS_DIR = "html_exports"


def generate_process_html(process_id, include_details=True):
    """
    Gera um arquivo HTML contendo as informações do processo especificado.
    
    Args:
        process_id: ID do processo
        include_details: Se True, inclui a seção de detalhes
        
    Returns:
        tuple: (caminho do arquivo gerado, URL relativo)
    """
    process = get_process_by_id(process_id)
    if not process:
        return None, None
    
    # Criar diretório de exportação se não existir
    if not os.path.exists(HTML_EXPORTS_DIR):
        os.makedirs(HTML_EXPORTS_DIR)
        
    # Nome do arquivo
    filename = f"processo_{process_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
    filepath = os.path.join(HTML_EXPORTS_DIR, filename)
    
    # Status
    status = process.get('status', 'Em andamento')
    status_color = get_status_color(status)
    # Garante que status não é None para usar upper()
    if status is None:
        status = ""
    
    # Criar HTML
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Processo de Importação - {process_id}</title>
        <style>
            body {{
                font-family: Arial, sans-serif;
                margin: 0;
                padding: 20px;
                color: #333;
            }}
            .container {{
                max-width: 1200px;
                margin: 0 auto;
                padding: 20px;
                background: #fff;
                box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
                border-radius: 5px;
            }}
            .header {{
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin-bottom: 20px;
                border-radius: 4px;
                overflow: hidden; /* Para garantir que as bordas arredondadas funcionem */
                box-shadow: 0 1px 3px rgba(0,0,0,0.08); /* Sombra muito sutil na tabela inteira */
                border-bottom: 1px solid #eee;
                padding-bottom: 10px;
            }}
            .status-badge {{
                background-color: {status_color};
                color: white;
                padding: 6px 15px;
                border-radius: 50px;
                font-weight: bold;
                display: inline-block;
                box-shadow: 0 1px 3px rgba(0,0,0,0.12), 0 1px 2px rgba(0,0,0,0.24);
                text-align: center;
                width: 110px;
                font-size: 0.9em;
                letter-spacing: 0.5px;
                text-transform: uppercase;
            }}
            /* Estilo para os contadores de status */
            .status-counts-container {{
                display: flex;
                flex-wrap: wrap;
                gap: 10px;
                margin-bottom: 15px;
            }}
            .status-count-item {{
                padding: 6px 15px;
                border-radius: 20px;
                font-size: 0.9em;
                display: flex;
                align-items: center;
                justify-content: space-between;
                cursor: pointer;
                color: white;
                width: 120px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                transition: all 0.2s ease;
                margin: 2px;
            }}
            
            .status-count-item:hover {{
                transform: translateY(-2px);
                box-shadow: 0 4px 8px rgba(0,0,0,0.15);
            }}
            .status-count-badge {{
                background: rgba(255,255,255,0.3);
                padding: 2px 8px;
                border-radius: 12px;
                text-align: center;
                margin-left: 8px;
                display: inline-block;
                color: white;
                font-weight: bold;
                font-size: 0.85em;
            }}
            .section {{
                margin-bottom: 30px;
                padding: 15px;
                background: #f9f9f9;
                border-radius: 5px;
                border-left: 4px solid #2c3e50;
            }}
            .section-title {{
                margin-top: 0;
                color: #2c3e50;
                font-size: 1.2em;
            }}
            .grid {{
                display: grid;
                grid-template-columns: repeat(3, 1fr);
                gap: 15px;
            }}
            .grid-item {{
                margin-bottom: 10px;
            }}
            .label {{
                font-weight: bold;
                font-size: 0.9em;
                color: #555;
                margin-bottom: 5px;
            }}
            .value {{
                background: #f5f5f5;
                padding: 8px;
                border-radius: 4px;
                font-size: 0.95em;
            }}
            .logo {{
                width: 150px;
            }}
            .footer {{
                text-align: center;
                margin-top: 30px;
                font-size: 0.8em;
                color: #777;
                border-top: 1px solid #eee;
                padding-top: 10px;
            }}
            table {{
                width: 100%;
                border-collapse: collapse;
                margin-bottom: 20px;
                border-radius: 4px;
                overflow: hidden; /* Para garantir que as bordas arredondadas funcionem */
                box-shadow: 0 1px 3px rgba(0,0,0,0.08); /* Sombra muito sutil na tabela inteira */
            }}
            table th, table td {{
                padding: 8px 10px;
                text-align: left;
                border-bottom: 1px solid #eee;
            }}
            table th {{
                background: #f5f5f5;
                font-weight: bold;
            }}
            @media print {{
                body {{
                    padding: 0;
                    font-size: 12pt;
                }}
                .container {{
                    box-shadow: none;
                    max-width: 100%;
                }}
                .section {{
                    page-break-inside: avoid;
                }}
                .no-print {{
                    display: none;
                }}
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <!-- Logo removido dos relatórios individuais conforme solicitado -->
            <div class="header">
                <div>
                    <h1>Processo de {"Exportação" if process.get('type', '') == "exportacao" else "Importação"} - {process_id}</h1>
                    <p>Referência: {process.get('ref', '')}</p>
                </div>
                <div>
                    <div class="status-badge">{status.upper() if status else ''}</div>
                </div>
            </div>
    """
    
    # Seção de Informações Gerais
    html += f"""
            <div class="section">
                <h2 class="section-title">Informações Gerais</h2>
                <div class="grid">
                    <div class="grid-item">
                        <div class="label">Código</div>
                        <div class="value">{process.get('id', '')}</div>
                    </div>
                    <div class="grid-item">
                        <div class="label">Referência</div>
                        <div class="value">{process.get('ref', '')}</div>
                    </div>
                    <div class="grid-item">
                        <div class="label">PO</div>
                        <div class="value">{process.get('po', '')}</div>
                    </div>
                    <div class="grid-item">
                        <div class="label">Invoice</div>
                        <div class="value">{process.get('invoice', '')}</div>
                    </div>
                    <div class="grid-item">
                        <div class="label">Origem</div>
                        <div class="value">{process.get('origin', '')}</div>
                    </div>
                    <div class="grid-item">
                        <div class="label">Produto</div>
                        <div class="value">{process.get('product', '')}</div>
                    </div>
                    <div class="grid-item">
                        <div class="label">Tipo de Processo</div>
                        <div class="value">{"Exportação" if process.get('type', '') == "exportacao" else "Importação"}</div>
                    </div>
                    <div class="grid-item">
                        <div class="label">ETA</div>
                        <div class="value">{format_date(process.get('eta', ''))}</div>
                    </div>
                    <div class="grid-item">
                        <div class="label">Status</div>
                        <div class="value">{process.get('status', '')}</div>
                    </div>
                </div>
            </div>
    """
    
    # Seção de Embarque
    html += f"""
            <div class="section">
                <h2 class="section-title">{"Informações de Exportação" if process.get('type', '') == "exportacao" else "Informações de Embarque"}</h2>
                <div class="grid">
                    <div class="grid-item">
                        <div class="label">{"Embarcador" if process.get('type', '') == "exportacao" else "Exportador"}</div>
                        <div class="value">{process.get('exporter', '')}</div>
                    </div>
                    <div class="grid-item">
                        <div class="label">Navio</div>
                        <div class="value">{process.get('ship', '')}</div>
                    </div>
                    <div class="grid-item">
                        <div class="label">Agente</div>
                        <div class="value">{process.get('agent', '')}</div>
                    </div>
                    <div class="grid-item">
                        <div class="label">Número B/L</div>
                        <div class="value">{process.get('bl_number', '')}</div>
                    </div>
                    <div class="grid-item">
                        <div class="label">Container</div>
                        <div class="value">{process.get('container', '')}</div>
                    </div>
                    <div class="grid-item">
                        <div class="label">Previsão de Chegada</div>
                        <div class="value">{format_date(process.get('arrival_date', ''))}</div>
                    </div>
                    <div class="grid-item">
                        <div class="label">Free Time</div>
                        <div class="value">{process.get('free_time', '')} dias</div>
                    </div>
                    <div class="grid-item">
                        <div class="label">Vencimento Free Time</div>
                        <div class="value">{format_date(process.get('free_time_expiry', ''))}</div>
                    </div>
                    <div class="grid-item">
                        <div class="label">Devolução de Vazio</div>
                        <div class="value">{format_date(process.get('empty_return', ''))}</div>
                    </div>
                </div>
            </div>
    """
    
    # Seção de Armazenagem
    html += f"""
            <div class="section">
                <h2 class="section-title">{"Informações do Terminal de Exportação" if process.get('type', '') == "exportacao" else "Informações de Armazenagem"}</h2>
                <div class="grid">
                    <div class="grid-item">
                        <div class="label">{"Terminal de Exportação" if process.get('type', '') == "exportacao" else "Terminal"}</div>
                        <div class="value">{process.get('terminal', '')}</div>
                    </div>
                    <div class="grid-item">
                        <div class="label">{"Entrada no Terminal" if process.get('type', '') == "exportacao" else "Entrada no Porto/Recinto"}</div>
                        <div class="value">{format_date(process.get('port_entry_date', ''))}</div>
                    </div>
                    <div class="grid-item">
                        <div class="label">Início do Período Atual</div>
                        <div class="value">{format_date(process.get('current_period_start', ''))}</div>
                    </div>
                    <div class="grid-item">
                        <div class="label">Vencimento do Período</div>
                        <div class="value">{format_date(process.get('current_period_expiry', ''))}</div>
                    </div>
                    <div class="grid-item">
                        <div class="label">Dias Armazenados</div>
                        <div class="value">{process.get('storage_days', '0')}</div>
                    </div>
                    <div class="grid-item">
                        <div class="label">Mapa</div>
                        <div class="value">{process.get('map', '')}</div>
                    </div>
                </div>
            </div>
    """
    
    # Seção de Documentos
    html += f"""
            <div class="section">
                <h2 class="section-title">Documentos e Informações Adicionais</h2>
                <div class="grid">
                    <div class="grid-item">
                        <div class="label">Nota Fiscal</div>
                        <div class="value">{process.get('invoice_number', '')}</div>
                    </div>
                    <div class="grid-item">
                        <div class="label">{"DU-E" if process.get('type', '') == "exportacao" else "D.I."}</div>
                        <div class="value">{process.get('di', '')}</div>
                    </div>
                    <div class="grid-item">
                        <div class="label">Documentos Originais</div>
                        <div class="value">{process.get('original_docs', '')}</div>
                    </div>
                    <div class="grid-item">
                        <div class="label">Data de Devolução</div>
                        <div class="value">{format_date(process.get('return_date', ''))}</div>
                    </div>
                    <div class="grid-item">
                        <div class="label">Última Atualização</div>
                        <div class="value">{format_date(process.get('last_update', ''))}</div>
                    </div>
                    {f'''
                    <div class="grid-item">
                        <div class="label">Importador</div>
                        <div class="value">{process.get('importer', '')}</div>
                    </div>
                    <div class="grid-item">
                        <div class="label">Deadline</div>
                        <div class="value">{format_date(process.get('deadline', ''))}</div>
                    </div>
                    ''' if process.get('type', '') == "exportacao" else ''}
                </div>
            </div>
    """
    
    if include_details:
        # Seção de Observações
        html += f"""
                <div class="section">
                    <h2 class="section-title">Observações</h2>
                    <div class="value" style="min-height: 60px;">
                        {process.get('observations', '')}
                    </div>
                </div>
        """
        
        # Seção de Eventos
        if 'events' in process and process['events']:
            html += """
                <div class="section">
                    <h2 class="section-title">Histórico de Eventos</h2>
                    <table>
                        <thead>
                            <tr>
                                <th>Data</th>
                                <th>Descrição</th>
                                <th>Usuário</th>
                            </tr>
                        </thead>
                        <tbody>
            """
            
            for event in process['events']:
                # Filtrar eventos de atribuição
                if not "atribuído" in event.get('description', '').lower():
                    html += f"""
                            <tr>
                                <td>{event.get('date', '')}</td>
                                <td>{event.get('description', '')}</td>
                                <td>{event.get('user', '')}</td>
                            </tr>
                    """
            
            html += """
                        </tbody>
                    </table>
                </div>
            """
    
    # Rodapé
    current_date = datetime.now().strftime("%d/%m/%Y")
    html += f"""
            <div class="footer">
                <p>Documento gerado em {current_date} | JGR Broker</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    # Salvar arquivo
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(html)
    
    return filepath, filename


def get_jgr_logo_base64():
    """
    Retorna o logo da JGR Broker em formato base64.
    Se o logo não existir, retorna uma string vazia.
    
    Returns:
        str: String codificada em base64 do logo
    """
    import base64
    logo_path = "assets/images/jgr_logo.png"
    if not os.path.exists(logo_path):
        return ""
        
    with open(logo_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode('utf-8')


def generate_processes_table_html(filtered_df=None, process_ids=None, include_details=True, client_filter=None, client_name=None, client_logo=None, archived=False):
    """
    Gera um arquivo HTML contendo uma tabela de processos com funcionalidade de expansão de detalhes.
    
    Args:
        filtered_df: DataFrame com os processos filtrados (opcional)
        process_ids: Lista de IDs de processos para incluir (opcional)
        include_details: Se True, inclui a seção de detalhes
        client_filter: ID do cliente para filtrar processos (opcional)
        client_name: Nome do cliente para personalizar o relatório (opcional)
        client_logo: Caminho para o logo do cliente (opcional)
        archived: Se True, indica que estamos gerando relatório para processos arquivados
        
    Returns:
        tuple: (caminho do arquivo gerado, URL relativo)
    """
    # Obter dados
    if filtered_df is None:
        filtered_df = get_processes_df()
    
    # Filtrar por IDs específicos (para visualização de cliente)
    if process_ids is not None:
        filtered_df = filtered_df[filtered_df['id'].isin(process_ids)]
    
    # Filtrar por cliente (novo)
    if client_filter:
        from components.auth import get_users
        users = get_users()
        
        # Encontrar o cliente pelo ID
        client = next((u for u in users if u['id'] == client_filter), None)
        
        if client and 'processes' in client and client['processes']:
            # Filtrar processos pelo cliente selecionado
            filtered_df = filtered_df[filtered_df['id'].isin(client['processes'])]
    
    # Verificar se há dados
    if filtered_df.empty:
        return None, None
    
    # Criar diretório de exportação se não existir
    if not os.path.exists(HTML_EXPORTS_DIR):
        os.makedirs(HTML_EXPORTS_DIR)
    
    # Nome do arquivo
    client_suffix = ""
    if client_name:
        client_suffix = f"_cliente_{client_name.replace(' ', '_')}"
    elif client_filter:
        client_suffix = f"_cliente_{client_filter}"
        
    # Adicionar indicação de processos arquivados no nome do arquivo
    archived_suffix = "_arquivados" if archived else ""
    filename = f"processos{client_suffix}{archived_suffix}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
    filepath = os.path.join(HTML_EXPORTS_DIR, filename)
    
    # Título personalizado com nome do cliente e indicador de arquivamento, se aplicável
    archived_title = "Arquivados" if archived else ""
    title = f"Processos de Importação e Exportação {archived_title} - JGR Broker"
    if client_name:
        title = f"Processos de Importação e Exportação {archived_title} - Cliente: {client_name} - JGR Broker"
    
    # Obter o logo da JGR em base64
    jgr_logo_base64 = get_jgr_logo_base64()
    
    # Criar HTML com estilos e scripts
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0">
        <title>{title}</title>
        <style>
            {get_mobile_styles()}
            body {{
                font-family: 'Segoe UI', Arial, sans-serif;
                margin: 0;
                padding: 20px;
                color: #333;
            }}
            .logo-container {{
                text-align: center;
                margin-bottom: 20px;
            }}
            .jgr-logo {{
                max-width: 300px;
                height: auto;
            }}
            .container {{
                max-width: 100%;
                margin: 0 auto;
                padding: 20px;
                background: #fff;
                box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
                border-radius: 5px;
            }}
            .header {{
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin-bottom: 20px;
                border-radius: 4px;
                overflow: hidden; /* Para garantir que as bordas arredondadas funcionem */
                box-shadow: 0 1px 3px rgba(0,0,0,0.08); /* Sombra muito sutil na tabela inteira */
                border-bottom: 1px solid #eee;
                padding-bottom: 10px;
            }}
            .filter-container {{
                margin: 20px 0;
                padding: 15px;
                background: #f9f9f9;
                border-radius: 5px;
                display: flex;
                flex-wrap: wrap;
                align-items: center;
                gap: 15px;
            }}
            
            .status-counts-wrapper {{
                margin: 20px 0;
            }}
            
            .status-counts-wrapper h3 {{
                font-size: 16px;
                margin-bottom: 10px;
                color: #555;
            }}
            
            .status-counts {{
                display: flex;
                flex-wrap: wrap;
                gap: 10px;
                padding: 15px;
                background: #f9f9f9;
                border-radius: 5px;
                border: 1px solid #e0e0e0;
            }}
            
            .status-count-item {{
                display: inline-flex;
                align-items: center;
                justify-content: space-between;
                padding: 8px 15px;
                border-radius: 50px;
                color: white;
                font-size: 0.85rem;
                font-weight: bold;
                cursor: pointer;
                min-width: 130px;
                box-shadow: 0 1px 3px rgba(0,0,0,0.12), 0 1px 2px rgba(0,0,0,0.24);
                transition: all 0.2s ease;
            }}
            
            .status-count-item:hover {{
                transform: translateY(-2px);
                box-shadow: 0 3px 6px rgba(0,0,0,0.16), 0 3px 6px rgba(0,0,0,0.23);
            }}
            
            .status-count-badge {{
                background-color: rgba(255,255,255,0.3);
                padding: 2px 8px;
                border-radius: 12px;
                margin-left: 8px;
                font-weight: bold;
            }}
            .filter-input {{
                padding: 8px 12px;
                border: 1px solid #ddd;
                border-radius: 4px;
                margin-right: 10px;
                width: 300px;
            }}
            .filter-label {{
                margin-right: 10px;
                font-weight: bold;
            }}
            .status-badge {{
                color: white;
                padding: 4px 12px;
                border-radius: 50px;
                font-weight: bold;
                display: inline-block;
                box-shadow: 0 1px 3px rgba(0,0,0,0.12), 0 1px 2px rgba(0,0,0,0.24);
                font-size: 0.75em;
                letter-spacing: 0.3px;
                min-width: 40px;
                max-width: 100%;
                text-align: center;
                white-space: nowrap;
                overflow: hidden;
                text-overflow: ellipsis;
                line-height: 1.5;
            }}
            table {{
                width: 100%;
                border-collapse: collapse;
                margin-bottom: 20px;
                border-radius: 4px;
                overflow: hidden; /* Para garantir que as bordas arredondadas funcionem */
                box-shadow: 0 1px 3px rgba(0,0,0,0.08); /* Sombra muito sutil na tabela inteira */
            }}
            table th, table td {{
                padding: 8px 10px;
                text-align: left;
                border-bottom: 1px solid #eee;
            }}
            table th {{
                background: #f5f5f5;
                font-weight: 700; /* Aumentado para super bold */
                cursor: pointer;
                position: relative;
                padding-right: 20px; /* Espaço para o ícone de ordenação */
                border: 1px solid #ddd; /* Borda sutil para o cabeçalho */
                box-shadow: 0 1px 2px rgba(0,0,0,0.05); /* Sombra leve para efeito de elevação */
                font-size: 13px; /* Tamanho ligeiramente maior */
                text-transform: uppercase; /* Letras maiúsculas para destaque */
                letter-spacing: 0.5px; /* Espaçamento entre letras */
                color: #000000; /* Cor preta para máximo contraste */
            }}
            
            /* Larguras específicas para as colunas */
            table th:nth-child(1), table td:nth-child(1) {{
                width: 80px; /* Coluna ID */
            }}
            table th:nth-child(2), table td:nth-child(2) {{
                min-width: 120px; /* Coluna de status */
                text-align: center;
            }}
            table th:nth-child(3), table td:nth-child(3) {{
                width: 90px; /* Coluna Tipo */
            }}
            table th:nth-child(8), table td:nth-child(8),
            table th:nth-child(10), table td:nth-child(10),
            table th:nth-child(14), table td:nth-child(14),
            table th:nth-child(15), table td:nth-child(15),
            table th:nth-child(16), table td:nth-child(16) {{
                width: 90px; /* Colunas de datas */
            }}
            /* Alinhar centralmente a coluna Free Time/Deadline */
            table th:nth-child(9), table td:nth-child(9) {{
                text-align: center;
            }}
            
            table th:nth-child(17), table td:nth-child(17) {{
                width: 40px; /* Coluna Dias Armazenados */
                text-align: center;
            }}
            
            /* Estilos para paginação */
            .pagination {{
                display: flex;
                justify-content: center;
                margin: 20px 0;
                user-select: none;
            }}
            
            .pagination-button {{
                border: 1px solid #ccc;
                background: #f5f5f5;
                padding: 5px 10px;
                margin: 0 5px;
                cursor: pointer;
                border-radius: 3px;
                font-size: 14px;
                color: #333;
                min-width: 30px;
                text-align: center;
            }}
            
            .pagination-button:hover {{
                background: #e5e5e5;
            }}
            
            .pagination-button.active {{
                background: #2c3e50;
                color: white;
                border-color: #2c3e50;
                font-weight: bold;
            }}
            
            .pagination-info {{
                margin: 0 10px;
                font-size: 14px;
                color: #666;
                align-self: center;
            }}
            
            table th:hover {{
                background: #eaeaea;
            }}
            
            table th.sort-asc::after {{
                content: "↑";
                position: absolute;
                right: 8px;
                opacity: 1;
                color: #2c3e50;
            }}
            
            table th.sort-desc::after {{
                content: "↓";
                position: absolute;
                right: 8px;
                opacity: 1;
                color: #2c3e50;
            }}
            .process-row {{
                cursor: pointer;
            }}
            .process-row:hover {{
                background-color: #f5f5f5;
            }}
            .details-row {{
                display: none;
            }}
            .details-container {{
                padding: 15px;
                background: #f9f9f9;
                border-radius: 5px;
                margin: 10px 0;
                position: relative;
            }}
            
            /* Estilo para botão de fechar detalhes */
            .close-button {{
                position: absolute;
                top: 10px;
                right: 10px;
                width: 25px;
                height: 25px;
                background-color: #f0f0f0;
                border-radius: 50%;
                color: #444;
                font-size: 12px;
                display: flex;
                align-items: center;
                justify-content: center;
                cursor: pointer;
                box-shadow: 0 1px 3px rgba(0,0,0,0.2);
                z-index: 10;
                transition: all 0.2s ease;
            }}
            
            .close-button:hover {{
                background-color: #e0e0e0;
                color: #000;
                transform: scale(1.1);
            }}
            .tab-container {{
                overflow: hidden;
                border: 1px solid #ccc;
                background-color: #f1f1f1;
                border-radius: 5px 5px 0 0;
            }}
            .tab {{
                background-color: inherit;
                float: left;
                border: none;
                outline: none;
                cursor: pointer;
                padding: 10px 16px;
                transition: 0.3s;
                font-size: 14px;
            }}
            .tab:hover {{
                background-color: #ddd;
            }}
            .tab.active {{
                background-color: #2c3e50;
                color: white;
            }}
            .tabcontent {{
                display: none;
                padding: 15px;
                border: 1px solid #ccc;
                border-top: none;
                border-radius: 0 0 5px 5px;
            }}
            .details-grid {{
                display: grid;
                grid-template-columns: repeat(3, 1fr);
                gap: 15px;
            }}
            .details-item {{
                margin-bottom: 10px;
            }}
            .details-label {{
                font-weight: bold;
                font-size: 0.95em;
                color: #333;
                margin-bottom: 5px;
            }}
            .details-value {{
                background: #f5f5f5;
                padding: 10px;
                border-radius: 4px;
                font-size: 1em;
                border: 1px solid #ddd;
                box-shadow: inset 0 1px 3px rgba(0,0,0,0.05);
            }}
            .footer {{
                text-align: center;
                margin-top: 30px;
                font-size: 0.8em;
                color: #777;
                border-top: 1px solid #eee;
                padding-top: 10px;
            }}
            @media print {{
                body {{
                    padding: 0;
                    font-size: 11pt;
                }}
                .container {{
                    box-shadow: none;
                    max-width: 100%;
                    padding: 0;
                }}
                .filter-container, .no-print {{
                    display: none !important;
                }}
                .details-row {{
                    display: table-row;
                }}
                .details-container {{
                    page-break-inside: avoid;
                }}
                .tabcontent {{
                    display: block !important;
                }}
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="logo-container">
                <img src="data:image/png;base64,{jgr_logo_base64}" alt="JGR Broker Logo" class="jgr-logo">
            </div>
            <div class="header">
                <div style="display: flex; justify-content: space-between; align-items: center; width: 100%;">
                    <div>
                        {f'<h1>Processos de Importação e Exportação - Cliente: {client_name} - JGR Broker</h1>' if client_name else '<h1>Processos de Importação e Exportação - JGR Broker</h1>'}
                    </div>
                    {f'<div style="flex-shrink: 0; margin-left: 20px;"><img src="data:image/png;base64,{get_base64_encoded_image(client_logo)}" style="max-height: 80px; max-width: 180px;"></div>' if client_logo and os.path.exists(client_logo) else ''}
                </div>
                <div style="display: flex; justify-content: space-between; color: #777; font-size: 0.9em; width: 100%;">
                    <span style="margin-right: 20px;">Relatório gerado em: {datetime.now().strftime('%d/%m/%Y')}</span>
                    <span>Total de processos: {len(filtered_df)}</span>
                </div>
            </div>
            
            <div class="filter-container no-print">
                <span class="filter-label">Buscar:</span>
                <input type="text" id="filterInput" class="filter-input" placeholder="Digite para filtrar (ID, Referência, PO, etc.)">
                
                <span class="filter-label" style="margin-left: 20px;">Tipo de Processo:</span>
                <select id="processTypeFilter" class="filter-input">
                    <option value="todos">Todos</option>
                    <option value="importacao">Importação</option>
                    <option value="exportacao">Exportação</option>
                </select>
                
                <span class="filter-label" style="margin-left: 20px;">Status:</span>
                <select id="statusFilter" class="filter-input">
                    <option value="todos">Todos</option>
                    <!-- Opções de status serão adicionadas via JavaScript -->
                </select>
            </div>
            
            <div class="status-counts-wrapper">
                <h3>Status dos Processos</h3>
                <div id="statusCounts" class="status-counts">
                    <!-- Contadores de status serão adicionados aqui via JavaScript -->
                </div>
            </div>
            
            <table id="processesTable">
                <thead>
                    <tr>
                        <th>ID</th>
                        <th>Status</th>
                        <th>Tipo</th>
                        <th>Referência</th>
                        <th>PO</th>
                        <th>Origem/Destino</th>
                        <th>Produto</th>
                        <th>ETA/ETD</th>
                        <th>Free Time/Deadline</th>
                        <th>Venc. Free Time</th>
                        <th>Devolução</th>
                        <th>Mapa</th>
                        <th>Nota Fiscal</th>
                        <th>Entrada Porto/Terminal</th>
                        <th>Início do Período</th>
                        <th>Vencimento do Período</th>
                        <th>Dias Armazenados</th>
                    </tr>
                </thead>
                <tbody>
    """
    
    # Adicionar cada processo como uma linha da tabela
    process_details_html = ""
    
    # Registrar todos os status para debug
    status_counts = {}
    for _, row in filtered_df.iterrows():
        row_status = row.get('status', '')
        if row_status in status_counts:
            status_counts[row_status] += 1
        else:
            status_counts[row_status] = 1
    
    print(f"Status encontrados no DataFrame: {status_counts}")
    
    for _, row in filtered_df.iterrows():
        process_id = row['id']
        status = row.get('status', '')
        status_color = get_status_color(status)
        # Garante que status não é None para usar upper()
        if status is None:
            status = ""
        
        # Linha principal com dados básicos
        process_type = row.get('type', '')
        process_type_display = "Importação" if process_type == "importacao" else "Exportação" if process_type == "exportacao" else ""
        
        # Labels adaptados de acordo com o tipo de processo
        origin_label = "Destino" if process_type == "exportacao" else "Origem"
        eta_label = "ETD" if process_type == "exportacao" else "ETA"
        freetime_label = "Deadline" if process_type == "exportacao" else "Free Time"
        entry_label = "Entrada no Terminal" if process_type == "exportacao" else "Entrada no Porto"
        
        html += f"""
                    <tr class="process-row" data-id="{process_id}" data-type="{process_type}" data-status="{status}" onclick="toggleDetails('{process_id}')">
                        <td>{process_id}</td>
                        <td style="text-align: center;"><div class="status-badge" style="background-color: {status_color}">{status.upper() if status else ''}</div></td>
                        <td>{process_type_display}</td>
                        <td>{row.get('ref', '')}</td>
                        <td>{row.get('po', '')}</td>
                        <td>{row.get('origin', '')}</td>
                        <td>{row.get('product', '')}</td>
                        <td>{format_date(row.get('eta', ''))}</td>
                        <td>{row.get('free_time', '')}</td>
                        <td>{format_date(row.get('free_time_expiry', ''))}</td>
                        <td>{format_date(row.get('empty_return', ''))}</td>
                        <td>{row.get('map', '')}</td>
                        <td>{row.get('invoice_number', '')}</td>
                        <td>{format_date(row.get('port_entry_date', ''))}</td>
                        <td>{format_date(row.get('current_period_start', ''))}</td>
                        <td>{format_date(row.get('current_period_expiry', ''))}</td>
                        <td>{row.get('storage_days', '0')}</td>
                    </tr>
        """
        
        # Obter detalhes completos do processo
        process = get_process_by_id(process_id)
        if not process:
            continue
            
        # Adicionar linha de detalhes expandível
        process_details_html += f"""
                    <tr class="details-row" id="details-{process_id}">
                        <td colspan="10">
                            <div class="details-container">
                                <div class="close-button" onclick="toggleDetails('{process_id}', true)">✖</div>
                                <div class="tab-container no-print">
                                    <button class="tab active" onclick="openTab(event, '{process_id}-info')">Informações Gerais</button>
                                    <button class="tab" onclick="openTab(event, '{process_id}-transport')">{"Exportação" if process.get('type', '') == "exportacao" else "Transporte"}</button>
                                    <button class="tab" onclick="openTab(event, '{process_id}-dates')">Datas</button>
                                    <button class="tab" onclick="openTab(event, '{process_id}-storage')">{"Terminal de Exportação" if process.get('type', '') == "exportacao" else "Armazenagem"}</button>
                                    <button class="tab" onclick="openTab(event, '{process_id}-docs')">Documentos</button>
                                    <button class="tab" onclick="openTab(event, '{process_id}-events')">Eventos</button>
                                </div>
                                
                                <div id="{process_id}-info" class="tabcontent" style="display: block;">
                                    <h3>Informações Gerais - {"Exportação" if process.get('type', '') == "exportacao" else "Importação"}</h3>
                                    <div class="details-grid">
                                        <div class="details-item">
                                            <div class="details-label">Código</div>
                                            <div class="details-value">{process.get('id', '')}</div>
                                        </div>
                                        <div class="details-item">
                                            <div class="details-label">Referência</div>
                                            <div class="details-value">{process.get('ref', '')}</div>
                                        </div>
                                        <div class="details-item">
                                            <div class="details-label">PO</div>
                                            <div class="details-value">{process.get('po', '')}</div>
                                        </div>
                                        <div class="details-item">
                                            <div class="details-label">Invoice</div>
                                            <div class="details-value">{process.get('invoice', '')}</div>
                                        </div>
                                        <div class="details-item">
                                            <div class="details-label">Origem</div>
                                            <div class="details-value">{process.get('origin', '')}</div>
                                        </div>
                                        <div class="details-item">
                                            <div class="details-label">Produto</div>
                                            <div class="details-value">{process.get('product', '')}</div>
                                        </div>
                                        <div class="details-item">
                                            <div class="details-label">Tipo de Processo</div>
                                            <div class="details-value">{"Exportação" if process.get('type', '') == "exportacao" else "Importação"}</div>
                                        </div>
                                        <div class="details-item">
                                            <div class="details-label">Tipo de Carga</div>
                                            <div class="details-value">{process.get('container_type', '')}</div>
                                        </div>
                                        <div class="details-item">
                                            <div class="details-label">ETA</div>
                                            <div class="details-value">{format_date(process.get('eta', ''))}</div>
                                        </div>
                                        <div class="details-item">
                                            <div class="details-label">Status</div>
                                            <div class="details-value">{process.get('status', '')}</div>
                                        </div>
                                    </div>
                                </div>
                                
                                <div id="{process_id}-transport" class="tabcontent">
                                    <h3>Transporte</h3>
                                    <div class="details-grid">
                                        <div class="details-item">
                                            <div class="details-label">Exportador</div>
                                            <div class="details-value">{process.get('exporter', '')}</div>
                                        </div>
                                        <div class="details-item">
                                            <div class="details-label">Navio</div>
                                            <div class="details-value">{process.get('ship', '')}</div>
                                        </div>
                                        <div class="details-item">
                                            <div class="details-label">Agente</div>
                                            <div class="details-value">{process.get('agent', '')}</div>
                                        </div>
                                        <div class="details-item">
                                            <div class="details-label">Número B/L</div>
                                            <div class="details-value">{process.get('bl_number', '')}</div>
                                        </div>
                                        <div class="details-item">
                                            <div class="details-label">Container</div>
                                            <div class="details-value">{process.get('container', '')}</div>
                                        </div>
                                    </div>
                                </div>
                                
                                <div id="{process_id}-dates" class="tabcontent">
                                    <h3>Datas</h3>
                                    <div class="details-grid">
                                        <div class="details-item">
                                            <div class="details-label">{"ETD" if process.get('type') == 'exportacao' else "ETA"}</div>
                                            <div class="details-value">{format_date(process.get('eta', ''))}</div>
                                        </div>
                                        <div class="details-item">
                                            <div class="details-label">{"Previsão de Saída" if process.get('type') == 'exportacao' else "Previsão de Chegada"}</div>
                                            <div class="details-value">{format_date(process.get('arrival_date', ''))}</div>
                                        </div>
                                        <div class="details-item">
                                            <div class="details-label">{"Deadline" if process.get('type') == 'exportacao' else "Free Time"}</div>
                                            <div class="details-value">{process.get('free_time', '')} dias</div>
                                        </div>
                                        <div class="details-item">
                                            <div class="details-label">{"Vencimento Deadline" if process.get('type') == 'exportacao' else "Vencimento Free Time"}</div>
                                            <div class="details-value">{format_date(process.get('free_time_expiry', ''))}</div>
                                        </div>
                                        <div class="details-item">
                                            <div class="details-label">Devolução de Vazio</div>
                                            <div class="details-value">{format_date(process.get('empty_return', ''))}</div>
                                        </div>
                                    </div>
                                </div>
                                
                                <div id="{process_id}-storage" class="tabcontent">
                                    <h3>{"Terminal de Exportação" if process.get('type') == 'exportacao' else "Armazenagem"}</h3>
                                    <div class="details-grid">
                                        <div class="details-item">
                                            <div class="details-label">{"Terminal de Exportação" if process.get('type') == 'exportacao' else "Terminal"}</div>
                                            <div class="details-value">{process.get('terminal', '')}</div>
                                        </div>
                                        <div class="details-item">
                                            <div class="details-label">{"Entrada no Terminal" if process.get('type') == 'exportacao' else "Entrada no Porto/Recinto"}</div>
                                            <div class="details-value">{format_date(process.get('port_entry_date', ''))}</div>
                                        </div>
                                        <div class="details-item">
                                            <div class="details-label">Início do Período Atual</div>
                                            <div class="details-value">{format_date(process.get('current_period_start', ''))}</div>
                                        </div>
                                        <div class="details-item">
                                            <div class="details-label">Vencimento do Período</div>
                                            <div class="details-value">{format_date(process.get('current_period_expiry', ''))}</div>
                                        </div>
                                        <div class="details-item">
                                            <div class="details-label">Dias Armazenados</div>
                                            <div class="details-value">{process.get('storage_days', '0')}</div>
                                        </div>
                                        <div class="details-item">
                                            <div class="details-label">Mapa</div>
                                            <div class="details-value">{process.get('map', '')}</div>
                                        </div>
                                    </div>
                                </div>
                                
                                <div id="{process_id}-docs" class="tabcontent">
                                    <h3>Documentos</h3>
                                    <div class="details-grid">
                                        <div class="details-item">
                                            <div class="details-label">Nota Fiscal</div>
                                            <div class="details-value">{process.get('invoice_number', '')}</div>
                                        </div>
                                        <div class="details-item">
                                            <div class="details-label">{"DU-E" if process.get('type') == 'exportacao' else "D.I."}</div>
                                            <div class="details-value">{process.get('di', '')}</div>
                                        </div>
                                        <div class="details-item">
                                            <div class="details-label">Documentos Originais</div>
                                            <div class="details-value">{process.get('original_docs', '')}</div>
                                        </div>
                                        <div class="details-item">
                                            <div class="details-label">Data de Devolução</div>
                                            <div class="details-value">{format_date(process.get('return_date', ''))}</div>
                                        </div>
                                    </div>
                                </div>
        """
        
        if include_details and 'events' in process and process['events']:
            process_details_html += f"""
                                <div id="{process_id}-events" class="tabcontent">
                                    <h3>Histórico de Eventos</h3>
                                    <table>
                                        <thead>
                                            <tr>
                                                <th>Data</th>
                                                <th>Descrição</th>
                                                <th>Usuário</th>
                                            </tr>
                                        </thead>
                                        <tbody>
            """
            
            for event in process['events']:
                # Filtrar eventos de atribuição
                if not "atribuído" in event.get('description', '').lower():
                    process_details_html += f"""
                                            <tr>
                                                <td>{event.get('date', '')}</td>
                                                <td>{event.get('description', '')}</td>
                                                <td>{event.get('user', '')}</td>
                                            </tr>
                    """
            
            process_details_html += """
                                        </tbody>
                                    </table>
                                </div>
            """
        else:
            process_details_html += f"""
                                <div id="{process_id}-events" class="tabcontent">
                                    <h3>Histórico de Eventos</h3>
                                    <p>Sem eventos registrados para este processo.</p>
                                </div>
            """
            
        process_details_html += """
                            </div>
                        </td>
                    </tr>
        """
    
    # Adicionar detalhes de processos ao HTML
    html += process_details_html
    
    # Adicionar scripts e rodapé
    html += """
                </tbody>
            </table>
            
            <!-- Container para paginação -->
            <div id="pagination-container"></div>
            
            <div class="footer">
                <p>© 2025 JGR BROKER - Todos os direitos reservados</p>
            </div>
        </div>
        
        <script>
            // Configuração de paginação
            const ITEMS_PER_PAGE = 10;
            let currentPage = 1;
            let filteredRows = [];
            
            document.addEventListener('DOMContentLoaded', function() {
                console.log("DOM carregado - iniciando setup");
                
                // Primeiro, verificamos se todos os elementos necessários estão presentes
                const filterInput = document.getElementById('filterInput');
                const processTypeFilter = document.getElementById('processTypeFilter');
                const statusFilter = document.getElementById('statusFilter');
                const table = document.getElementById('processesTable');
                const statusContainer = document.getElementById('statusCounts');
                const paginationContainer = document.getElementById('pagination-container');
                
                if (!filterInput || !processTypeFilter || !statusFilter || !table || !statusContainer || !paginationContainer) {
                    console.error("Elementos críticos não encontrados:", {
                        filterInput, processTypeFilter, statusFilter, table, statusContainer, paginationContainer
                    });
                }
                
                // Adicionar event listeners para os filtros
                if (filterInput) filterInput.addEventListener('keyup', filterTable);
                if (processTypeFilter) processTypeFilter.addEventListener('change', filterTable);
                if (statusFilter) statusFilter.addEventListener('change', filterTable);
                
                // Inicializar os filtros de status e contadores com atraso para garantir
                // que a tabela esteja totalmente renderizada
                setTimeout(function() {
                    console.log("Iniciando filtros de status após atraso...");
                    initStatusFilters();
                    filterTable(); // Aplicar filtros iniciais
                }, 200);
                
                // Inicializar responsividade
                adjustTableForMobile();
                window.addEventListener('resize', adjustTableForMobile);
            });
            
            // Inicializar os filtros de status e contadores
            function initStatusFilters() {
                console.log("Iniciando filtros de status");
                const table = document.getElementById('processesTable');
                if (!table) {
                    console.error("Tabela de processos não encontrada");
                    return;
                }
                
                const rows = Array.from(table.querySelectorAll('tbody tr.process-row'));
                console.log("Linhas encontradas:", rows.length);
                
                const statusSelect = document.getElementById('statusFilter');
                const statusContainer = document.getElementById('statusCounts');
                
                if (!statusSelect || !statusContainer) {
                    console.error("Elementos de filtro não encontrados", {statusSelect, statusContainer});
                    return;
                }
                
                // Debug: Verificar os atributos data-status das linhas
                rows.forEach(row => {
                    const rowStatus = row.getAttribute('data-status');
                    const rowId = row.getAttribute('data-id');
                    console.log(`Row ${rowId}: data-status="${rowStatus}"`);
                });
                
                // Limpar opções existentes no select, mantendo apenas a opção 'todos'
                while (statusSelect.options.length > 1) {
                    statusSelect.remove(1);
                }
                
                // Objeto para armazenar status e suas cores e contagens
                const statusData = {};
                
                // Coletar todos os status existentes na tabela
                rows.forEach(row => {
                    if (!row) return;
                    
                    // Usar o atributo data-status para obter o status
                    const status = row.getAttribute('data-status');
                    if (!status) {
                        console.log("Status não encontrado para a linha:", row);
                        return;
                    }
                    
                    // Ainda obtemos a cor do badge para manter a consistência visual
                    const statusCell = row.cells[1]; // Coluna de status
                    if (!statusCell) return;
                    
                    const statusBadge = statusCell.querySelector('.status-badge');
                    if (!statusBadge) return;
                    
                    // Obter a cor real do elemento
                    const computedStyle = window.getComputedStyle(statusBadge);
                    const color = statusBadge.style.backgroundColor || computedStyle.backgroundColor;
                    
                    if (!statusData[status]) {
                        statusData[status] = {
                            count: 1,
                            color: color
                        };
                        
                        // Adicionar ao dropdown
                        const option = document.createElement('option');
                        option.value = status;
                        option.textContent = status;
                        statusSelect.appendChild(option);
                    } else {
                        statusData[status].count++;
                    }
                });
                
                console.log("Status encontrados:", Object.keys(statusData).length);
                console.log("Dados de status:", statusData);
                

                
                // Criar os contadores visuais
                statusContainer.innerHTML = '';
                
                // Debug - para ver todos os status encontrados
                console.log("Status encontrados para criar contadores:", Object.keys(statusData));
                
                for (const status in statusData) {
                    if (!status || status === "") continue; // Ignorar status vazios
                    
                    const data = statusData[status];
                    const count = data.count;
                    const color = data.color || '#999';
                    
                    console.log(`Criando contador para ${status}: ${count} (cor: ${color})`);
                    
                    const item = document.createElement('div');
                    item.className = 'status-count-item';
                    
                    // IMPORTANTE: Garantir que o atributo data-status seja definido corretamente
                    item.setAttribute('data-status', status); // Atribuir o status para referência futura
                    
                    item.style.backgroundColor = color;
                    item.innerHTML = `${status} <span class="status-count-badge">${count}</span>`;
                    
                    // Verificar se o atributo foi definido corretamente
                    console.log(`Atributo data-status definido: ${item.getAttribute('data-status')}`);
                    
                    // Adicionar evento de clique para filtrar
                    item.addEventListener('click', function() {
                        console.log(`Clicou em status: ${status}`);
                        statusSelect.value = status;
                        filterTable();
                    });
                    
                    statusContainer.appendChild(item);
                }
                
                // Verificar se os contadores foram criados
                const createdItems = statusContainer.querySelectorAll('.status-count-item');
                console.log(`Foram criados ${createdItems.length} contadores de status`);
                
                // Filtrar inicialmente
                filterTable();
            }
            
            // Função de filtragem da tabela
            function filterTable() {
                console.log("Aplicando filtros à tabela");
                const filterValue = document.getElementById('filterInput').value.toLowerCase();
                const typeFilter = document.getElementById('processTypeFilter').value;
                const statusFilter = document.getElementById('statusFilter').value;
                
                const table = document.getElementById('processesTable');
                if (!table) {
                    console.error("Tabela não encontrada na filtragem");
                    return;
                }
                
                // Obter todas as linhas de processos utilizando o seletor de classe
                const rows = Array.from(table.querySelectorAll('tbody tr.process-row'));
                console.log(`Filtrando ${rows.length} linhas`);
                
                // Objeto para contar status visíveis
                const visibleStatusCounts = {};
                
                // Inicializar contadores com zero para cada status
                // Buscamos pelos elementos diretamente do DOM
                const statusItems = document.querySelectorAll('.status-count-item');
                statusItems.forEach(item => {
                    if (!item || !item.textContent) return;
                    
                    // Pegamos apenas o texto do status, sem o contador
                    const statusParts = item.textContent.split(' ');
                    if (statusParts.length > 0) {
                        const status = statusParts[0].trim();
                        visibleStatusCounts[status] = 0;
                        console.log(`Inicializando contador para ${status}: 0`);
                    }
                });
                
                // Reset filtered rows for pagination
                filteredRows = [];
                
                // Aplicar filtros a cada linha
                for (let i = 0; i < rows.length; i++) {
                    const row = rows[i];
                    if (!row || !row.cells) continue;
                    
                    const cells = row.cells;
                    const processId = row.getAttribute('data-id');
                    const processType = row.getAttribute('data-type') || '';
                    
                    // Verificar filtro de texto
                    let matchesText = false;
                    for (let j = 0; j < cells.length; j++) {
                        if (!cells[j]) continue;
                        
                        const cellText = cells[j].textContent.toLowerCase();
                        if (cellText.includes(filterValue)) {
                            matchesText = true;
                            break;
                        }
                    }
                    
                    // Verificar filtro de tipo de processo
                    let matchesType = true;
                    if (typeFilter !== 'todos') {
                        // Comparar tipos normalizados para evitar problemas com maiúsculas/minúsculas
                        const normalizedType = processType.toLowerCase();
                        const normalizedFilter = typeFilter.toLowerCase();
                        
                        // Melhorar lógica de correspondência para considerar valores vazios ou nulos
                        matchesType = (normalizedType === normalizedFilter) || 
                                     (normalizedFilter === 'importacao' && (normalizedType === '' || normalizedType === 'importacao'));
                        
                        console.log(`Row ${processId}: processType=${processType}, typeFilter=${typeFilter}, matchesType=${matchesType}`);
                    }
                    
                    // Verificar filtro de status
                    let matchesStatus = true;
                    if (statusFilter !== 'todos') {
                        const rowStatus = row.getAttribute('data-status');
                        matchesStatus = (rowStatus === statusFilter);
                        console.log(`Row ${row.getAttribute('data-id')}: status=${rowStatus}, filter=${statusFilter}, matches=${matchesStatus}`);
                    }
                    
                    // Check if row passes all filters
                    const isVisible = matchesText && matchesType && matchesStatus;
                    
                    // Instead of directly showing/hiding rows, collect them for pagination
                    if (isVisible) {
                        filteredRows.push(row);
                        
                        // Hide all rows initially (pagination will show them)
                        row.style.display = 'none';
                        
                        // Atualizar contadores de status visíveis
                        // Método 3 (mais confiável): Usar o atributo data-status
                        const status = row.getAttribute('data-status');
                        
                        // Se encontramos um status, incrementamos o contador
                        if (status && status.length > 0) {
                            console.log(`Incrementando contador para status: ${status}`);
                            visibleStatusCounts[status] = (visibleStatusCounts[status] || 0) + 1;
                        }
                    }
                }
                
                // Atualizar os contadores visuais
                console.log("Status visíveis:", visibleStatusCounts);
                
                // Atualizar os contadores no DOM
                statusItems.forEach(item => {
                    if (!item) return;
                    
                    // Obter o status a partir do atributo data-status
                    const statusText = item.getAttribute('data-status');
                    if (!statusText) {
                        console.error("Item sem atributo data-status:", item);
                        return;
                    }
                    
                    console.log(`Atualizando badge para: ${statusText}`);
                    
                    // Encontrar o elemento de contador
                    const badge = item.querySelector('.status-count-badge');
                    if (badge) {
                        // CORREÇÃO: Precisamos contar novamente os processos com este status
                        // quando filtros de texto ou tipo são aplicados
                        if (statusFilter !== 'todos' && statusFilter !== statusText) {
                            // Se um filtro de status específico está aplicado e não é este status,
                            // mostramos 0 (pois todos os outros status estão filtrados)
                            badge.textContent = '0';
                            item.style.opacity = '0.6';
                        } else {
                            // Contamos diretamente do DOM para maior precisão
                            let count = 0;
                            
                            if (filterValue === '' && typeFilter === 'todos') {
                                // Se não há outros filtros, usamos o valor pré-calculado
                                count = visibleStatusCounts[statusText] || 0;
                            } else {
                                // Se há outros filtros, contamos os processos visíveis com este status
                                rows.forEach(row => {
                                    if (row.style.display !== 'none' && 
                                        row.getAttribute('data-status') === statusText) {
                                        count++;
                                    }
                                });
                            }
                            
                            badge.textContent = count.toString();
                            console.log(`  - Nova contagem para ${statusText}: ${count}`);
                            
                            // Destacar visualmente status com zero processos
                            if (count === 0) {
                                item.style.opacity = '0.6';
                            } else {
                                item.style.opacity = '1';
                            }
                        }
                    } else {
                        console.error(`  - Badge não encontrado para ${statusText}`);
                    }
                    
                    // Destacar o status selecionado
                    if (statusText === statusFilter) {
                        item.style.border = '2px solid #333';
                        item.style.transform = 'translateY(-2px)';
                        item.style.boxShadow = '0 4px 6px rgba(0, 0, 0, 0.15)';
                    } else {
                        item.style.border = 'none';
                        item.style.transform = 'none';
                        item.style.boxShadow = '0 1px 3px rgba(0, 0, 0, 0.1)';
                    }
                });
            }
            
            // Expandir/colapsar detalhes
            function toggleDetails(processId, isClose = false) {
                const row = document.querySelector(`tr[data-id="${processId}"]`);
                const detailsRow = document.getElementById('details-' + processId);
                
                if (!detailsRow) {
                    console.error('Details row not found for process:', processId);
                    return;
                }
                
                // Verificar estado atual
                const isVisible = detailsRow.style.display === 'table-row';
                
                // Se estamos fechando (botão X) ou alternando um item já aberto, fechar
                if (isClose || isVisible) {
                    detailsRow.style.display = 'none';
                    if (row) row.classList.remove('active');
                    return;
                }
                
                // Primeiro, fechar todos os detalhes abertos
                const allDetailRows = document.querySelectorAll('tr[id^="details-"]');
                const allProcessRows = document.querySelectorAll('tr.process-row');
                
                // Fechar todos os outros detalhes
                allDetailRows.forEach(row => {
                    row.style.display = 'none';
                });
                
                // Remover classe 'active' de todas as linhas de processo
                allProcessRows.forEach(prow => {
                    prow.classList.remove('active');
                });
                
                // Fechar detalhes se estiver aberto (toggle)
                if (isVisible) {
                    detailsRow.style.display = 'none';
                    if (row) row.classList.remove('active');
                } else {
                    // Abrir detalhes do processo atual
                    detailsRow.style.display = 'table-row';
                    if (row) row.classList.add('active');
                    
                    // Ativar a primeira aba por padrão
                    const firstTab = detailsRow.querySelector('.tab');
                    const firstContent = detailsRow.querySelector('.tabcontent');
                    
                    if (firstTab && firstContent) {
                        // Desativar todas as abas e conteúdos
                        const allTabs = detailsRow.querySelectorAll('.tab');
                        const allContents = detailsRow.querySelectorAll('.tabcontent');
                        
                        allTabs.forEach(tab => tab.classList.remove('active'));
                        allContents.forEach(content => content.style.display = 'none');
                        
                        // Ativar a primeira aba
                        firstTab.classList.add('active');
                        firstContent.style.display = 'block';
                    }
                }
            }
            
            // Trocar abas
            function openTab(evt, tabId) {
                // Obter o ID do processo (primeira parte do ID da aba)
                const processId = tabId.split('-')[0];
                
                // Esconder todas as abas de conteúdo deste processo
                const tabcontent = document.getElementsByClassName('tabcontent');
                for (let i = 0; i < tabcontent.length; i++) {
                    if (tabcontent[i].id.startsWith(processId)) {
                        tabcontent[i].style.display = 'none';
                    }
                }
                
                // Remover classe "active" de todas as abas deste processo
                const tablinks = evt.currentTarget.parentNode.getElementsByClassName('tab');
                for (let i = 0; i < tablinks.length; i++) {
                    tablinks[i].className = tablinks[i].className.replace(' active', '');
                }
                
                // Mostrar a aba selecionada
                const selectedTab = document.getElementById(tabId);
                if (selectedTab) {
                    selectedTab.style.display = 'block';
                    evt.currentTarget.className += ' active';
                } else {
                    console.error('Tab content not found:', tabId);
                }
            }
            
            // Ordenação da tabela
            document.querySelectorAll('#processesTable th').forEach((header, index) => {
                header.addEventListener('click', () => {
                    const table = document.getElementById('processesTable');
                    const rows = Array.from(table.querySelectorAll('tr.process-row'));
                    const detailsRows = {};
                    
                    // Salvar as linhas de detalhes
                    rows.forEach(row => {
                        const processId = row.getAttribute('data-id');
                        const detailsRow = document.getElementById('details-' + processId);
                        if (detailsRow) {
                            detailsRows[processId] = detailsRow;
                        }
                    });
                    
                    // Ordenar as linhas
                    const sortedRows = rows.sort((a, b) => {
                        const aValue = a.cells[index].textContent.trim();
                        const bValue = b.cells[index].textContent.trim();
                        return aValue.localeCompare(bValue, 'pt-BR');
                    });
                    
                    // Remover todas as linhas
                    rows.forEach(row => {
                        const processId = row.getAttribute('data-id');
                        const detailsRow = document.getElementById('details-' + processId);
                        if (detailsRow) {
                            detailsRow.remove();
                        }
                        row.remove();
                    });
                    
                    // Re-adicionar linhas ordenadas
                    const tbody = table.querySelector('tbody');
                    sortedRows.forEach(row => {
                        tbody.appendChild(row);
                        const processId = row.getAttribute('data-id');
                        if (detailsRows[processId]) {
                            tbody.appendChild(detailsRows[processId]);
                        }
                    });
                });
            });
            
            // Inicializar ordenação da tabela
            initTableSorting();
            
            // Função para inicializar ordenação da tabela
            function initTableSorting() {
                const table = document.getElementById('processesTable');
                const headers = table.querySelectorAll('th');
                
                // Definir colunas especiais para ordenação de datas e números
                const dateColumns = [7, 9, 11, 14, 15, 16]; // ETA, Vencimento Free Time, etc.
                const numberColumns = [8, 17]; // Free Time, Dias Armazenados
                
                headers.forEach((header, index) => {
                    header.addEventListener('click', () => {
                        sortTable(table, index, dateColumns.includes(index), numberColumns.includes(index));
                    });
                });
            }
            
            // Função para ordenar tabela
            function sortTable(table, column, isDate, isNumber) {
                const tbody = table.querySelector('tbody');
                const rows = Array.from(tbody.querySelectorAll('tr.process-row'));
                
                // Detectar se já está ordenada nesta coluna
                const currentSort = tbody.getAttribute('data-sort-column');
                const currentDir = tbody.getAttribute('data-sort-dir');
                
                // Definir direção da ordenação
                let direction = 'asc';
                if (currentSort == column) {
                    direction = currentDir === 'asc' ? 'desc' : 'asc';
                }
                
                // Marcar cabeçalho como ordenado
                const headers = table.querySelectorAll('th');
                headers.forEach(th => {
                    th.classList.remove('sort-asc', 'sort-desc');
                });
                headers[column].classList.add(direction === 'asc' ? 'sort-asc' : 'sort-desc');
                
                // Ordenar linhas
                rows.sort((a, b) => {
                    // Obter valores das células
                    let aValue = a.cells[column].textContent.trim();
                    let bValue = b.cells[column].textContent.trim();
                    
                    // Tratar células vazias
                    if (aValue === '') return 1;
                    if (bValue === '') return -1;
                    
                    // Conversão para comparação
                    if (isDate) {
                        // Converter data formato DD/MM/YYYY para YYYY-MM-DD para comparação
                        aValue = aValue.split('/').reverse().join('-');
                        bValue = bValue.split('/').reverse().join('-');
                    } else if (isNumber) {
                        // Converter para número
                        aValue = parseFloat(aValue) || 0;
                        bValue = parseFloat(bValue) || 0;
                    }
                    
                    // Comparação
                    if (aValue < bValue) return direction === 'asc' ? -1 : 1;
                    if (aValue > bValue) return direction === 'asc' ? 1 : -1;
                    return 0;
                });
                
                // Reordenar as linhas na tabela
                rows.forEach(row => {
                    const processId = row.getAttribute('data-id');
                    const detailsRow = document.getElementById('details-' + processId);
                    
                    // Remover a linha e sua linha de detalhes
                    tbody.removeChild(row);
                    if (detailsRow) tbody.removeChild(detailsRow);
                    
                    // Adicionar de volta na nova ordem
                    tbody.appendChild(row);
                    if (detailsRow) tbody.appendChild(detailsRow);
                });
                
                // Salvar estado de ordenação
                tbody.setAttribute('data-sort-column', column);
                tbody.setAttribute('data-sort-dir', direction);
                
                // Atualizar paginação após ordenação
                window.filterTable();
            }
            
            // Configuração de paginação
            const ITEMS_PER_PAGE = 10;
            let currentPage = 1;
            let filteredRows = [];
            
            // Função para mostrar a página atual
            function showPage(page) {
                // Esconder todas as linhas filtradas
                filteredRows.forEach(row => {
                    row.style.display = 'none';
                    
                    // Também esconder as linhas de detalhes
                    const rowId = row.getAttribute('data-id');
                    if (rowId) {
                        const detailsRow = document.getElementById(`details-${rowId}`);
                        if (detailsRow) {
                            detailsRow.style.display = 'none';
                        }
                    }
                });
                
                // Calcular os índices das linhas a serem exibidas
                const startIdx = (page - 1) * ITEMS_PER_PAGE;
                const endIdx = Math.min(startIdx + ITEMS_PER_PAGE, filteredRows.length);
                
                // Exibir somente as linhas da página atual
                for (let i = startIdx; i < endIdx; i++) {
                    filteredRows[i].style.display = '';
                }
                
                // Atualizar a interface de paginação
                updateActivePage(page);
            }
            
            // Função para atualizar a interface de paginação
            function updatePagination() {
                const totalPages = Math.ceil(filteredRows.length / ITEMS_PER_PAGE);
                const paginationContainer = document.getElementById('pagination-container');
                paginationContainer.innerHTML = '';
                
                if (totalPages <= 1) {
                    return; // Não mostrar paginação se houver apenas uma página
                }
                
                // Criar o componente de paginação
                const pagination = document.createElement('div');
                pagination.className = 'pagination';
                
                // Botão Anterior
                const prevButton = document.createElement('div');
                prevButton.className = 'pagination-button';
                prevButton.innerText = '«';
                prevButton.addEventListener('click', () => {
                    if (currentPage > 1) {
                        currentPage--;
                        showPage(currentPage);
                    }
                });
                pagination.appendChild(prevButton);
                
                // Botões de página
                const maxVisiblePages = 5; // Número máximo de botões de página visíveis
                let startPage = Math.max(1, currentPage - Math.floor(maxVisiblePages / 2));
                let endPage = Math.min(totalPages, startPage + maxVisiblePages - 1);
                
                // Ajustar se estamos próximos ao final
                if (endPage - startPage < maxVisiblePages - 1) {
                    startPage = Math.max(1, endPage - maxVisiblePages + 1);
                }
                
                // Primeira página (se não estiver visível)
                if (startPage > 1) {
                    const firstPageBtn = document.createElement('div');
                    firstPageBtn.className = 'pagination-button';
                    firstPageBtn.innerText = '1';
                    firstPageBtn.addEventListener('click', () => {
                        currentPage = 1;
                        showPage(currentPage);
                    });
                    pagination.appendChild(firstPageBtn);
                    
                    // Adicionar elipses se necessário
                    if (startPage > 2) {
                        const ellipsis = document.createElement('div');
                        ellipsis.className = 'pagination-info';
                        ellipsis.innerText = '...';
                        pagination.appendChild(ellipsis);
                    }
                }
                
                // Botões de página regulares
                for (let i = startPage; i <= endPage; i++) {
                    const pageButton = document.createElement('div');
                    pageButton.className = 'pagination-button';
                    if (i === currentPage) {
                        pageButton.classList.add('active');
                    }
                    pageButton.innerText = i;
                    pageButton.addEventListener('click', () => {
                        currentPage = i;
                        showPage(currentPage);
                    });
                    pagination.appendChild(pageButton);
                }
                
                // Última página (se não estiver visível)
                if (endPage < totalPages) {
                    // Adicionar elipses se necessário
                    if (endPage < totalPages - 1) {
                        const ellipsis = document.createElement('div');
                        ellipsis.className = 'pagination-info';
                        ellipsis.innerText = '...';
                        pagination.appendChild(ellipsis);
                    }
                    
                    const lastPageBtn = document.createElement('div');
                    lastPageBtn.className = 'pagination-button';
                    lastPageBtn.innerText = totalPages;
                    lastPageBtn.addEventListener('click', () => {
                        currentPage = totalPages;
                        showPage(currentPage);
                    });
                    pagination.appendChild(lastPageBtn);
                }
                
                // Botão Próximo
                const nextButton = document.createElement('div');
                nextButton.className = 'pagination-button';
                nextButton.innerText = '»';
                nextButton.addEventListener('click', () => {
                    if (currentPage < totalPages) {
                        currentPage++;
                        showPage(currentPage);
                    }
                });
                pagination.appendChild(nextButton);
                
                // Adicionar informação da página atual
                const pageInfo = document.createElement('div');
                pageInfo.className = 'pagination-info';
                pageInfo.id = 'page-info';
                pageInfo.innerText = `Página ${currentPage} de ${totalPages}`;
                pagination.appendChild(pageInfo);
                
                paginationContainer.appendChild(pagination);
            }
            
            // Função para atualizar o botão de página ativa
            function updateActivePage(page) {
                // Atualizar classe ativa nos botões
                document.querySelectorAll('.pagination-button').forEach(btn => {
                    btn.classList.remove('active');
                    if (btn.innerText === page.toString()) {
                        btn.classList.add('active');
                    }
                });
                
                // Atualizar informação da página
                const pageInfo = document.getElementById('page-info');
                if (pageInfo) {
                    const totalPages = Math.ceil(filteredRows.length / ITEMS_PER_PAGE);
                    pageInfo.innerText = `Página ${page} de ${totalPages}`;
                }
            }
            
            // Modificar a função filterTable original
            document.addEventListener('DOMContentLoaded', function() {
                // Guardar referência à função original
                const originalFilterTable = window.filterTable;
                
                // Sobrescrever a função filterTable
                window.filterTable = function() {
                    // Obter os filtros atuais
                    const filterValue = document.getElementById('filterInput')?.value?.toLowerCase() || '';
                    const typeFilter = document.getElementById('processTypeFilter')?.value || 'todos';
                    const statusFilter = document.getElementById('statusFilter')?.value || 'todos';
                    
                    const table = document.getElementById('processesTable');
                    if (!table) {
                        console.error("Tabela não encontrada");
                        return;
                    }
                    
                    // Obter todas as linhas de processos
                    const rows = Array.from(table.querySelectorAll('tbody tr.process-row'));
                    
                    // Redefinir as linhas filtradas para paginação
                    filteredRows = [];
                    
                    // Aplicar filtros e coletar linhas visíveis
                    rows.forEach(row => {
                        // Esconder todas as linhas inicialmente
                        row.style.display = 'none';
                        
                        const cells = row.cells;
                        const processType = row.getAttribute('data-type') || '';
                        const rowStatus = row.getAttribute('data-status') || '';
                        
                        // Verificar filtro de texto
                        let matchesText = !filterValue;
                        if (filterValue) {
                            for (let j = 0; j < cells.length; j++) {
                                if (!cells[j]) continue;
                                
                                const cellText = cells[j].textContent.toLowerCase();
                                if (cellText.includes(filterValue)) {
                                    matchesText = true;
                                    break;
                                }
                            }
                        }
                        
                        // Verificar filtro de tipo de processo
                        let matchesType = true;
                        if (typeFilter !== 'todos') {
                            matchesType = (processType === typeFilter) || 
                                        (typeFilter === 'importacao' && processType === '');
                        }
                        
                        // Verificar filtro de status
                        let matchesStatus = true;
                        if (statusFilter !== 'todos') {
                            matchesStatus = (rowStatus === statusFilter);
                        }
                        
                        // Adicionar à lista de linhas filtradas se passar por todos os filtros
                        if (matchesText && matchesType && matchesStatus) {
                            filteredRows.push(row);
                        }
                    });
                    
                    // Atualizar a contagem total
                    const processCounter = document.getElementById('process-counter');
                    if (processCounter) {
                        processCounter.textContent = filteredRows.length;
                    }
                    
                    // Atualizar paginação e mostrar a primeira página
                    currentPage = 1;
                    updatePagination();
                    showPage(currentPage);
                };
                
                // Inicializar paginação após carregar a página
                setTimeout(() => {
                    window.filterTable();
                }, 500);
            });
        </script>
    </body>
    </html>
    """
    
    # Salvar arquivo
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(html)
    
    return filepath, filename


def get_download_link(filepath, filename):
    """
    Cria um link para download do arquivo HTML gerado.
    
    Args:
        filepath: Caminho completo do arquivo
        filename: Nome do arquivo para exibição
        
    Returns:
        str: HTML com link para download
    """
    # Ler o conteúdo do arquivo HTML
    with open(filepath, 'r', encoding='utf-8') as f:
        html_content = f.read()
    
    # Aqui criamos um link para download do conteúdo
    html_bytes = html_content.encode('utf-8')
    import base64
    b64 = base64.b64encode(html_bytes).decode('utf-8')
    href = f'data:text/html;base64,{b64}'
    
    return href, filename