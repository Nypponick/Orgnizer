"""
Gerador de HTML para exportar processos com paginação
"""
import os
import uuid
import datetime
from pathlib import Path
import pandas as pd
from custom_html_styles import get_html_styles
from html_post_processor import process_html_file

def format_date(date_str):
    """Formatar data para exibição"""
    if not date_str or pd.isna(date_str):
        return ""
    try:
        if isinstance(date_str, str):
            parts = date_str.split('/')
            if len(parts) == 3:
                return date_str
            return date_str
        return date_str.strftime("%d/%m/%Y") if hasattr(date_str, 'strftime') else str(date_str)
    except Exception:
        return str(date_str)

def get_status_color(status):
    """Obter cor para o status"""
    status_colors = {
        "Novo Processo": "#17a2b8",  # Ciano
        "Pendente": "#ffc107",       # Amarelo
        "Liberado": "#28a745",       # Verde
        "Em andamento": "#007bff",   # Azul
        "Atrasado": "#dc3545",       # Vermelho
        "BL liberado": "#28a745",    # Verde
        "Chegada do navio alterada": "#ffc107",  # Amarelo
        "Aguardando documentos": "#ffc107",     # Amarelo
        "Aguardando chegada": "#17a2b8",        # Ciano
        "Em desembaraço": "#007bff",            # Azul
        "Nacionalizado": "#28a745",             # Verde
        "Concluído": "#6c757d",                # Cinza
    }
    
    return status_colors.get(status, "#6c757d")  # Cinza como padrão

def generate_html_with_pagination(filtered_df, title="Relatório de Processos", include_details=True, client_name=None, archived=False):
    """
    Gera um arquivo HTML contendo uma tabela de processos com paginação.
    
    Args:
        filtered_df: DataFrame com os processos filtrados
        title: Título do relatório
        include_details: Se True, inclui a seção de detalhes
        client_name: Nome do cliente para personalizar o relatório (opcional)
        archived: Se True, indica que estamos gerando relatório para processos arquivados
        
    Returns:
        tuple: (caminho do arquivo gerado, URL relativo)
    """
    # Criar diretório para exportação se não existir
    export_dir = Path("html_exports")
    export_dir.mkdir(exist_ok=True)
    
    # Gerar nome de arquivo único
    file_id = str(uuid.uuid4())[:8]
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    
    if archived:
        filename = f"processos_arquivados_{timestamp}_{file_id}.html"
    else:
        filename = f"processos_{timestamp}_{file_id}.html"
    
    filepath = export_dir / filename
    
    # Iniciar HTML com estilos
    html = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            color: #333;
            margin: 0;
            padding: 20px;
            background-color: #f7f9fc;
        }}
        .container {{
            max-width: 1400px;
            margin: 0 auto;
            background: white;
            padding: 20px;
            box-shadow: 0 0 10px rgba(0,0,0,0.1);
            border-radius: 5px;
        }}
        h1 {{
            color: #2c3e50;
            margin-top: 0;
            border-bottom: 2px solid #eee;
            padding-bottom: 10px;
            font-size: 24px;
        }}
        .timestamp {{
            color: #666;
            font-size: 14px;
            margin-bottom: 20px;
            font-style: italic;
        }}
        .info-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 20px;
            flex-wrap: wrap;
        }}
        .process-count {{
            font-size: 16px;
            color: #2c3e50;
            font-weight: bold;
        }}
        .process-count span {{
            color: #007bff;
            font-size: 18px;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin-bottom: 20px;
            font-size: 14px;
            table-layout: auto;
            overflow-x: auto;
            display: block;
        }}
        table th, table td {{
            text-align: center;
            padding: 10px;
            border: 1px solid #ddd;
            word-break: break-word;
            vertical-align: middle;
        }}
        /* Ajustando alinhamento específico por coluna */
        table td:nth-child(1), table th:nth-child(1) {{ text-align: center; }} /* ID */
        table td:nth-child(2), table th:nth-child(2) {{ text-align: center; }} /* Status */
        table td:nth-child(3), table th:nth-child(3) {{ text-align: center; }} /* Tipo */
        table td:nth-child(4), table th:nth-child(4) {{ text-align: left; }}   /* Referência */
        table td:nth-child(5), table th:nth-child(5) {{ text-align: left; }}   /* PO */
        table td:nth-child(6), table th:nth-child(6) {{ text-align: left; }}   /* Origem/Destino */
        table td:nth-child(7), table th:nth-child(7) {{ text-align: left; }}   /* Produto */
        table th {{
            background-color: #f2f2f2;
            color: #2c3e50;
            font-weight: bold;
            white-space: nowrap;
            position: sticky;
            top: 0;
            z-index: 10;
            cursor: pointer;
        }}
        table tr:nth-child(even) {{
            background-color: #f9f9f9;
        }}
        table tr:hover {{
            background-color: #f1f7fd;
        }}
        .status-badge {{
            display: inline-block;
            padding: 6px 12px;
            border-radius: 50px;
            font-weight: bold;
            font-size: 12px;
            text-transform: uppercase;
            color: white;
            text-align: center;
            box-shadow: 0 1px 3px rgba(0, 0, 0, 0.12);
            min-width: 100px;
            transition: transform 0.2s ease;
        }}
        .status-badge:hover {{
            transform: scale(1.05);
        }}
        .filter-container {{
            margin-bottom: 20px;
            padding: 15px;
            background: #f8f9fa;
            border-radius: 5px;
            border: 1px solid #e9ecef;
        }}
        .filter-label {{
            font-weight: bold;
            margin-right: 10px;
            color: #495057;
        }}
        .filter-input {{
            padding: 8px;
            border: 1px solid #ced4da;
            border-radius: 4px;
            margin-right: 15px;
            min-width: 200px;
        }}
        #no-results-message {{
            padding: 20px;
            background-color: #f8d7da;
            color: #721c24;
            border: 1px solid #f5c6cb;
            border-radius: 4px;
            margin: 20px 0;
            display: none;
        }}
        .status-counts-wrapper {{
            margin: 20px 0;
            padding: 15px;
            border: 1px solid #e9ecef;
            border-radius: 5px;
            background: #f8f9fa;
        }}
        .status-counts-wrapper h3 {{
            margin-top: 0;
            font-size: 16px;
            color: #495057;
            border-bottom: 1px solid #dee2e6;
            padding-bottom: 8px;
        }}
        .status-counts {{
            display: flex;
            flex-wrap: wrap;
            gap: 10px;
            margin-top: 10px;
        }}
        .status-count-item {{
            padding: 8px 12px;
            border-radius: 5px;
            background: white;
            box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
            font-size: 13px;
            cursor: pointer;
            display: flex;
            align-items: center;
            transition: transform 0.2s, box-shadow 0.2s;
        }}
        .status-count-item:hover {{
            transform: translateY(-2px);
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }}
        .status-count-badge {{
            display: inline-block;
            min-width: 20px;
            height: 20px;
            line-height: 20px;
            text-align: center;
            background: #e9ecef;
            border-radius: 10px;
            margin-left: 8px;
            font-size: 12px;
            font-weight: bold;
            color: #495057;
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
        table th:nth-child(17), table td:nth-child(17) {{
            width: 40px; /* Coluna Dias Armazenados */
            text-align: center;
        }}
        
        /* Estilos para paginação */
        .pagination {{
            display: flex;
            justify-content: center;
            align-items: center;
            flex-wrap: wrap;
            margin: 25px 0;
            user-select: none;
            gap: 8px;
        }}
        
        .pagination-button {{
            border: 1px solid #ccc;
            background: #f5f5f5;
            padding: 8px 12px;
            cursor: pointer;
            border-radius: 4px;
            font-size: 14px;
            color: #333;
            min-width: 40px;
            text-align: center;
            transition: all 0.2s ease;
            line-height: 1;
            font-family: inherit;
        }}
        
        .pagination-button:hover {{
            background: #e0e0e0;
            border-color: #999;
        }}
        
        .pagination-button.active {{
            background: #2c3e50;
            color: white;
            border-color: #2c3e50;
            font-weight: bold;
            box-shadow: 0 2px 4px rgba(0,0,0,0.2);
        }}
        
        .pagination-info {{
            margin: 0 15px;
            font-size: 14px;
            color: #666;
            align-self: center;
            font-weight: 500;
        }}
        
        .pagination-ellipsis {{
            margin: 0 5px;
            color: #666;
            font-size: 16px;
            align-self: center;
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
            transition: all 0.2s ease;
        }}
        .process-row:hover {{
            background-color: #f1f7fd;
            box-shadow: 0 0 5px rgba(0,0,0,0.1);
            transform: translateY(-1px);
        }}
        .details-row {{
            display: none;
        }}
        .details-container {{
            padding: 15px;
            background: #f9f9f9;
            border-radius: 5px;
            margin: 10px 0;
            box-shadow: 0 2px 4px rgba(0,0,0,0.05);
            border-left: 3px solid #2c3e50;
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
            font-weight: 500;
            border-bottom: 2px solid transparent;
        }}
        .tab:hover {{
            background-color: #ddd;
        }}
        .tab.active {{
            background-color: #2c3e50;
            color: white;
            border-bottom: 2px solid #007bff;
        }}
        
        /* Estilo para o botão de fechar */
        .close-btn {{
            display: inline-block;
            padding: 3px 8px;
            background: #f1f1f1;
            border: none;
            border-radius: 50%;
            cursor: pointer;
            color: #555;
            font-weight: bold;
            font-size: 18px;
            line-height: 18px;
            transition: all 0.2s ease;
        }}
        .close-btn:hover {{
            background: #e0e0e0;
            color: #333;
            transform: scale(1.1);
        }}
        
        .tabcontent {{
            display: none;
            padding: 15px;
            border: 1px solid #ccc;
            border-top: none;
            box-shadow: 0 2px 3px rgba(0,0,0,0.05) inset;
            border-radius: 0 0 5px 5px;
        }}
        /* Estilo para badges de tipo de processo */
        .process-type-badge {{
            display: inline-block;
            padding: 3px 8px;
            border-radius: 4px;
            font-size: 11px;
            background-color: #f8f9fa;
            color: #495057;
            border: 1px solid #dee2e6;
            margin-right: 5px;
            font-weight: 500;
        }}
        .process-type-importacao {{
            background-color: #e6f7ff;
            border-color: #91d5ff;
            color: #0050b3;
        }}
        .process-type-exportacao {{
            background-color: #f6ffed;
            border-color: #b7eb8f;
            color: #237804;
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
            font-size: 0.9em;
            color: #2c3e50;
            border-bottom: 1px dotted #ddd;
            padding-bottom: 3px;
            margin-bottom: 3px;
        }}
        .details-value {{
            background: #f5f5f5;
            padding: 8px;
            border-radius: 4px;
            font-size: 0.95em;
            box-shadow: 0 1px 2px rgba(0,0,0,0.05) inset;
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
                display: table-row !important;
            }}
            .details-container {{
                padding: 5px;
            }}
            table {{
                page-break-inside: auto;
            }}
            tr {{
                page-break-inside: avoid;
            }}
            .pagination {{
                display: none !important;
            }}
        }}
        @media (max-width: 768px) {{
            table {{
                font-size: 12px;
            }}
            table th, table td {{
                padding: 6px;
            }}
            .details-grid {{
                grid-template-columns: repeat(2, 1fr);
            }}
            .filter-input {{
                margin-bottom: 10px;
                min-width: unset;
                width: 100%;
            }}
            .filter-label {{
                display: block;
                margin-bottom: 5px;
            }}
            .status-badge {{
                font-size: 10px;
                padding: 4px 8px;
            }}
        }}
        @media (max-width: 576px) {{
            .details-grid {{
                grid-template-columns: 1fr;
            }}
            table {{ 
                font-size: 11px;
            }}
            table th, table td {{
                padding: 4px;
            }}
            .status-badge {{
                font-size: 9px;
                padding: 3px 6px;
                min-width: 60px;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>{title}{' - '+client_name if client_name else ''}</h1>
        <div class="timestamp">Gerado em: {datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")}</div>
        
        <div class="info-header">
            <div class="process-count">
                Total de processos: <span id="process-counter">{len(filtered_df)}</span>
            </div>
        </div>
        
        <div class="filter-container">
            <span class="filter-label">Buscar:</span>
            <input type="text" id="filterInput" class="filter-input" placeholder="Digite para filtrar...">
            
            <span class="filter-label" style="margin-left: 20px;">Tipo de Processo:</span>
            <select id="processTypeFilter" class="filter-input">
                <option value="todos">Todos</option>
                <option value="importacao">Importação</option>
                <option value="exportacao">Exportação</option>
            </select>
        </div>
        
        <div class="status-counts-wrapper">
            <h3>Status dos Processos</h3>
            <div id="statusCounts" class="status-counts">
                <!-- Contadores de status serão adicionados aqui via JavaScript -->
            </div>
        </div>
        
        <div id="no-results-message">
            <p>Nenhum processo encontrado com os filtros aplicados.</p>
        </div>
        
        <table id="processesTable">
            <thead>
                <tr>
                    <th style="text-align: center;">ID</th>
                    <th style="text-align: center;">Status</th>
                    <th style="text-align: center;">Tipo de Processo</th>
                    <th style="text-align: left;">Referência</th>
                    <th style="text-align: left;">PO</th>
                    <th style="text-align: left;">Origem</th>
                    <th style="text-align: left;">Produto</th>
                    <th style="text-align: center;">ETA</th>
                    <th style="text-align: center;">Free Time</th>
                    <th style="text-align: center;">Vencimento Free Time</th>
                    <th style="text-align: center;">Devolução de Vazio</th>
                    <th style="text-align: left;">Mapa</th>
                    <th style="text-align: left;">Nota Fiscal</th>
                    <th style="text-align: center;">Entrada no Porto</th>
                    <th style="text-align: center;">Início do Período</th>
                    <th style="text-align: center;">Vencimento do Período</th>
                    <th style="text-align: center;">Dias Armazenados</th>
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
        html += f"""
                <tr class="process-row" data-id="{process_id}" data-type="{row.get('type', '')}" data-status="{status}" onclick="toggleDetails('{process_id}')">
                    <td style="text-align: center;">{process_id}</td>
                    <td style="text-align: center;"><div class="status-badge" style="background-color: {status_color}">{status.upper() if status else ''}</div></td>
                    <td style="text-align: center;"><span class="process-type-badge process-type-{row.get('type', 'importacao')}">{"Exportação" if row.get('type', '') == "exportacao" else "Importação"}</span></td>
                    <td style="text-align: left;">{row.get('ref', '')}</td>
                    <td style="text-align: left;">{row.get('po', '')}</td>
                    <td style="text-align: left;">{row.get('origin', '')}</td>
                    <td style="text-align: left;">{row.get('product', '')}</td>
                    <td style="text-align: center;">{format_date(row.get('eta', ''))}</td>
                    <td style="text-align: center;">{row.get('free_time', '')}</td>
                    <td style="text-align: center;">{format_date(row.get('free_time_expiry', ''))}</td>
                    <td style="text-align: center;">{format_date(row.get('empty_return', ''))}</td>
                    <td style="text-align: left;">{row.get('map', '')}</td>
                    <td style="text-align: left;">{row.get('invoice_number', '')}</td>
                    <td style="text-align: center;">{format_date(row.get('port_entry_date', ''))}</td>
                    <td style="text-align: center;">{format_date(row.get('current_period_start', ''))}</td>
                    <td style="text-align: center;">{format_date(row.get('current_period_expiry', ''))}</td>
                    <td style="text-align: center;">{row.get('storage_days', '')}</td>
                </tr>
        """
        
        if include_details:
            # Linha de detalhes (inicialmente escondida)
            html += f"""
                <tr id="details-{process_id}" class="details-row">
                    <td colspan="17">
                        <div class="details-container">
                            <div style="text-align: right; margin-bottom: 5px;">
                                <span class="close-btn" onclick="toggleDetails('{process_id}')" title="Fechar detalhes">&times;</span>
                            </div>
                            <div class="tab-container">
                                <button class="tab active" onclick="openTab(event, '{process_id}-info')">Informações</button>
                                <button class="tab" onclick="openTab(event, '{process_id}-dates')">Datas</button>
                                <button class="tab" onclick="openTab(event, '{process_id}-storage')">Armazenagem</button>
                                <button class="tab" onclick="openTab(event, '{process_id}-docs')">Documentos</button>
                                {f'<button class="tab" onclick="openTab(event, \'{process_id}-events\')">Eventos</button>' if 'events' in row and row['events'] else ''}
                            </div>
                            
                            <div id="{process_id}-info" class="tabcontent" style="display: block;">
                                <h3>Informações Gerais</h3>
                                <div class="details-grid">
                                    <div class="details-item">
                                        <div class="details-label">ID do Processo</div>
                                        <div class="details-value">{process_id}</div>
                                    </div>
                                    <div class="details-item">
                                        <div class="details-label">Status</div>
                                        <div class="details-value">{status.upper() if status else ''}</div>
                                    </div>
                                    <div class="details-item">
                                        <div class="details-label">Tipo de Processo</div>
                                        <div class="details-value">{"Exportação" if row.get('type', '') == "exportacao" else "Importação"}</div>
                                    </div>
                                    <div class="details-item">
                                        <div class="details-label">Referência</div>
                                        <div class="details-value">{row.get('ref', '')}</div>
                                    </div>
                                    <div class="details-item">
                                        <div class="details-label">PO</div>
                                        <div class="details-value">{row.get('po', '')}</div>
                                    </div>
                                    <div class="details-item">
                                        <div class="details-label">Origem/Destino</div>
                                        <div class="details-value">{row.get('origin', '')}</div>
                                    </div>
                                    <div class="details-item">
                                        <div class="details-label">Produto</div>
                                        <div class="details-value">{row.get('product', '')}</div>
                                    </div>
                                    <div class="details-item">
                                        <div class="details-label">Navio</div>
                                        <div class="details-value">{row.get('ship', '')}</div>
                                    </div>
                                    <div class="details-item">
                                        <div class="details-label">Container</div>
                                        <div class="details-value">{row.get('container', '')}</div>
                                    </div>
                                </div>
                            </div>
                            
                            <div id="{process_id}-dates" class="tabcontent">
                                <h3>Datas</h3>
                                <div class="details-grid">
                                    <div class="details-item">
                                        <div class="details-label">ETA</div>
                                        <div class="details-value">{format_date(row.get('eta', ''))}</div>
                                    </div>
                                    <div class="details-item">
                                        <div class="details-label">Previsão de Chegada</div>
                                        <div class="details-value">{format_date(row.get('arrival_date', ''))}</div>
                                    </div>
                                    <div class="details-item">
                                        <div class="details-label">Free Time</div>
                                        <div class="details-value">{row.get('free_time', '')} dias</div>
                                    </div>
                                    <div class="details-item">
                                        <div class="details-label">Vencimento Free Time</div>
                                        <div class="details-value">{format_date(row.get('free_time_expiry', ''))}</div>
                                    </div>
                                    <div class="details-item">
                                        <div class="details-label">Devolução de Vazio</div>
                                        <div class="details-value">{format_date(row.get('empty_return', ''))}</div>
                                    </div>
                                </div>
                            </div>
                            
                            <div id="{process_id}-storage" class="tabcontent">
                                <h3>Armazenagem</h3>
                                <div class="details-grid">
                                    <div class="details-item">
                                        <div class="details-label">Terminal</div>
                                        <div class="details-value">{row.get('terminal', '')}</div>
                                    </div>
                                    <div class="details-item">
                                        <div class="details-label">Entrada no Porto/Recinto</div>
                                        <div class="details-value">{format_date(row.get('port_entry_date', ''))}</div>
                                    </div>
                                    <div class="details-item">
                                        <div class="details-label">Início do Período Atual</div>
                                        <div class="details-value">{format_date(row.get('current_period_start', ''))}</div>
                                    </div>
                                    <div class="details-item">
                                        <div class="details-label">Vencimento do Período</div>
                                        <div class="details-value">{format_date(row.get('current_period_expiry', ''))}</div>
                                    </div>
                                    <div class="details-item">
                                        <div class="details-label">Dias Armazenados</div>
                                        <div class="details-value">{row.get('storage_days', '0')}</div>
                                    </div>
                                    <div class="details-item">
                                        <div class="details-label">Mapa</div>
                                        <div class="details-value">{row.get('map', '')}</div>
                                    </div>
                                </div>
                            </div>
                            
                            <div id="{process_id}-docs" class="tabcontent">
                                <h3>Documentos</h3>
                                <div class="details-grid">
                                    <div class="details-item">
                                        <div class="details-label">Nota Fiscal</div>
                                        <div class="details-value">{row.get('invoice_number', '')}</div>
                                    </div>
                                    <div class="details-item">
                                        <div class="details-label">D.I.</div>
                                        <div class="details-value">{row.get('di', '')}</div>
                                    </div>
                                    <div class="details-item">
                                        <div class="details-label">Documentos Originais</div>
                                        <div class="details-value">{row.get('original_docs', '')}</div>
                                    </div>
                                    <div class="details-item">
                                        <div class="details-label">Data de Devolução</div>
                                        <div class="details-value">{format_date(row.get('return_date', ''))}</div>
                                    </div>
                                </div>
                            </div>
        """
        
        if include_details and 'events' in row and row['events']:
            process_details_html += f"""
                            <div id="{process_id}-events" class="tabcontent">
                                <h3>Histórico de Eventos</h3>
                                <table>
                                    <thead>
                                        <tr>
                                            <th style="text-align: center;">Data</th>
                                            <th style="text-align: left;">Descrição</th>
                                            <th style="text-align: left;">Usuário</th>
                                        </tr>
                                    </thead>
                                    <tbody>
            """
            
            # Adicionar eventos, apenas os que não contêm "atribuído ao cliente" para 
            # relatórios de clientes
            for event in row['events']:
                # Pular eventos de atribuição se for relatório para cliente
                if client_name and "atribuído ao cliente" in event.get('description', ''):
                    continue
                    
                process_details_html += f"""
                                        <tr>
                                            <td>{format_date(event.get('date', ''))}</td>
                                            <td>{event.get('description', '')}</td>
                                            <td>{event.get('user', '')}</td>
                                        </tr>
                """
            
            process_details_html += """
                                    </tbody>
                                </table>
                            </div>
            """
        
        html += process_details_html + """
                        </div>
                    </td>
                </tr>
        """
    
    # Adicionar detalhes de processos ao HTML
    html += process_details_html
    
    # Adicionar container de paginação e scripts
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
        document.addEventListener('DOMContentLoaded', function() {
            // Filtros e contadores de status
            initializeFilters();
            
            // Ordenação da tabela
            initTableSorting();
            
            // Responsividade para mobile
            adjustTableForMobile();
        });
        
        // Inicializar filtros e contadores
        function initializeFilters() {
            const filterInput = document.getElementById('filterInput');
            const processTypeFilter = document.getElementById('processTypeFilter');
            const statusContainer = document.getElementById('statusCounts');
            
            // Coletar todos os status únicos
            const table = document.getElementById('processesTable');
            const rows = Array.from(table.querySelectorAll('tbody tr.process-row'));
            const statusMap = {};
            
            // Criar objeto com contagem de cada status
            rows.forEach(row => {
                const status = row.getAttribute('data-status');
                if (status) {
                    if (statusMap[status]) {
                        statusMap[status].count++;
                    } else {
                        // Obter a cor do status
                        const statusBadge = row.querySelector('.status-badge');
                        const color = statusBadge ? statusBadge.style.backgroundColor : '#ccc';
                        
                        statusMap[status] = {
                            count: 1,
                            color: color
                        };
                    }
                }
            });
            
            // Criar "Todos" contador
            const allItem = document.createElement('div');
            allItem.className = 'status-count-item';
            allItem.setAttribute('data-status', 'todos');
            allItem.innerHTML = `Todos <span class="status-count-badge">${rows.length}</span>`;
            allItem.addEventListener('click', () => filterByStatus('todos'));
            statusContainer.appendChild(allItem);
            
            // Criar contadores para cada status
            Object.keys(statusMap).sort().forEach(status => {
                const item = document.createElement('div');
                item.className = 'status-count-item';
                item.setAttribute('data-status', status);
                item.innerHTML = `${status} <span class="status-count-badge">${statusMap[status].count}</span>`;
                
                // Adicionar evento de clique para filtrar
                item.addEventListener('click', () => filterByStatus(status));
                statusContainer.appendChild(item);
            });
            
            // Adicionar eventos para os filtros
            if (filterInput) {
                filterInput.addEventListener('input', filterTable);
            }
            
            if (processTypeFilter) {
                processTypeFilter.addEventListener('change', filterTable);
            }
            
            // Aplicar filtros iniciais
            filterTable();
        }
        
        // Filtrar por status ao clicar nos contadores
        function filterByStatus(status) {
            // Atualizar o select de status
            const statusFilter = document.getElementById('statusFilter');
            if (statusFilter) {
                statusFilter.value = status;
            }
            
            // Destacar o contador selecionado
            const statusItems = document.querySelectorAll('.status-count-item');
            statusItems.forEach(item => {
                if (item.getAttribute('data-status') === status) {
                    item.style.fontWeight = 'bold';
                    item.style.border = '2px solid #333';
                    item.style.transform = 'translateY(-2px)';
                    item.style.boxShadow = '0 4px 6px rgba(0, 0, 0, 0.15)';
                } else {
                    item.style.fontWeight = 'normal';
                    item.style.border = 'none';
                    item.style.transform = 'none';
                    item.style.boxShadow = '0 1px 3px rgba(0, 0, 0, 0.1)';
                }
            });
            
            // Aplicar filtro
            filterTable();
        }
        
        // Função para filtrar a tabela
        function filterTable() {
            const filterValue = document.getElementById('filterInput').value.toLowerCase();
            const typeFilter = document.getElementById('processTypeFilter').value;
            const statusFilter = document.querySelector('.status-count-item[style*="bold"]')?.getAttribute('data-status') || 'todos';
            
            const table = document.getElementById('processesTable');
            const rows = Array.from(table.querySelectorAll('tbody tr.process-row'));
            let visibleCount = 0;
            
            // Esconder todos os detalhes
            document.querySelectorAll('tr.details-row').forEach(row => {
                row.style.display = 'none';
            });
            
            // Aplicar filtros
            rows.forEach(row => {
                // Esconder a linha inicialmente
                row.style.display = 'none';
                
                const cells = Array.from(row.cells);
                const processType = row.getAttribute('data-type') || '';
                const rowStatus = row.getAttribute('data-status') || '';
                
                // Verificar filtro de texto
                let textMatch = !filterValue;
                if (filterValue) {
                    cells.forEach(cell => {
                        if (cell.textContent.toLowerCase().includes(filterValue)) {
                            textMatch = true;
                        }
                    });
                }
                
                // Verificar filtro de tipo
                const typeMatch = typeFilter === 'todos' || processType === typeFilter || 
                                 (typeFilter === 'importacao' && processType === '');
                
                // Verificar filtro de status
                const statusMatch = statusFilter === 'todos' || rowStatus === statusFilter;
                
                // Aplicar visibilidade
                const isVisible = textMatch && typeMatch && statusMatch;
                if (isVisible) {
                    visibleCount++;
                }
            });
            
            // Atualizar contador total
            const processCounter = document.getElementById('process-counter');
            if (processCounter) {
                processCounter.textContent = visibleCount;
            }
            
            // Mostrar mensagem se não há resultados
            const noResults = document.getElementById('no-results-message');
            if (noResults) {
                noResults.style.display = visibleCount === 0 ? 'block' : 'none';
            }
            
            // Inicializar paginação
            initPagination(rows, filterValue, typeFilter, statusFilter);
        }
        
        // Configuração de paginação
        const ROWS_PER_PAGE = 10;
        let currentPage = 1;
        let totalPages = 1;
        let filteredRows = [];
        
        // Inicializar paginação com os filtros aplicados
        function initPagination(allRows, filterText, typeFilter, statusFilter) {
            // Filtrar as linhas
            filteredRows = allRows.filter(row => {
                const cells = Array.from(row.cells);
                const processType = row.getAttribute('data-type') || '';
                const rowStatus = row.getAttribute('data-status') || '';
                
                // Verificar filtro de texto
                let textMatch = !filterText;
                if (filterText) {
                    cells.forEach(cell => {
                        if (cell.textContent.toLowerCase().includes(filterText)) {
                            textMatch = true;
                        }
                    });
                }
                
                // Verificar filtro de tipo
                const typeMatch = typeFilter === 'todos' || processType === typeFilter || 
                                 (typeFilter === 'importacao' && processType === '');
                
                // Verificar filtro de status
                const statusMatch = statusFilter === 'todos' || rowStatus === statusFilter;
                
                // Retornar true se passar por todos os filtros
                return textMatch && typeMatch && statusMatch;
            });
            
            // Calcular número total de páginas
            totalPages = Math.ceil(filteredRows.length / ROWS_PER_PAGE);
            
            // Criar os controles de paginação
            createPaginationControls();
            
            // Mostrar a primeira página
            currentPage = 1;
            showPage(currentPage);
        }
        
        // Criar controles de paginação
        function createPaginationControls() {
            const paginationContainer = document.getElementById('pagination-container');
            if (!paginationContainer) return;
            
            // Limpar container
            paginationContainer.innerHTML = '';
            
            // Se tiver apenas uma página, não mostrar controles
            if (totalPages <= 1) return;
            
            // Criar container de paginação
            const pagination = document.createElement('div');
            pagination.className = 'pagination';
            
            // Botão Anterior
            const prevButton = document.createElement('button');
            prevButton.innerText = '« Anterior';
            prevButton.className = 'pagination-button';
            prevButton.onclick = () => {
                if (currentPage > 1) {
                    showPage(currentPage - 1);
                }
            };
            pagination.appendChild(prevButton);
            
            // Botões com números de página
            const maxButtons = Math.min(5, totalPages);
            let startPage = Math.max(1, currentPage - Math.floor(maxButtons / 2));
            let endPage = Math.min(totalPages, startPage + maxButtons - 1);
            
            // Ajustar range se necessário
            if (endPage - startPage + 1 < maxButtons) {
                startPage = Math.max(1, endPage - maxButtons + 1);
            }
            
            // Botão para primeira página (se não estiver no intervalo)
            if (startPage > 1) {
                const firstButton = document.createElement('button');
                firstButton.innerText = '1';
                firstButton.className = 'pagination-button';
                firstButton.onclick = () => showPage(1);
                pagination.appendChild(firstButton);
                
                // Adicionar elipses se houver um gap
                if (startPage > 2) {
                    const ellipsis = document.createElement('span');
                    ellipsis.innerText = '...';
                    ellipsis.className = 'pagination-ellipsis';
                    pagination.appendChild(ellipsis);
                }
            }
            
            // Botões numéricos de página
            for (let i = startPage; i <= endPage; i++) {
                const pageButton = document.createElement('button');
                pageButton.innerText = i.toString();
                pageButton.className = 'pagination-button';
                if (i === currentPage) {
                    pageButton.classList.add('active');
                }
                pageButton.onclick = () => showPage(i);
                pagination.appendChild(pageButton);
            }
            
            // Botão para última página (se não estiver no intervalo)
            if (endPage < totalPages) {
                // Adicionar elipses se houver um gap
                if (endPage < totalPages - 1) {
                    const ellipsis = document.createElement('span');
                    ellipsis.innerText = '...';
                    ellipsis.className = 'pagination-ellipsis';
                    pagination.appendChild(ellipsis);
                }
                
                const lastButton = document.createElement('button');
                lastButton.innerText = totalPages.toString();
                lastButton.className = 'pagination-button';
                lastButton.onclick = () => showPage(totalPages);
                pagination.appendChild(lastButton);
            }
            
            // Botão Próximo
            const nextButton = document.createElement('button');
            nextButton.innerText = 'Próximo »';
            nextButton.className = 'pagination-button';
            nextButton.onclick = () => {
                if (currentPage < totalPages) {
                    showPage(currentPage + 1);
                }
            };
            pagination.appendChild(nextButton);
            
            // Informação da página atual
            const pageInfo = document.createElement('div');
            pageInfo.id = 'page-info';
            pageInfo.className = 'pagination-info';
            pageInfo.innerText = `Página ${currentPage} de ${totalPages}`;
            pagination.appendChild(pageInfo);
            
            // Adicionar a navegação ao container
            paginationContainer.appendChild(pagination);
        }
        
        // Mostrar uma página específica
        function showPage(pageNum) {
            // Validar número da página
            if (pageNum < 1 || pageNum > totalPages) return;
            
            // Atualizar página atual
            currentPage = pageNum;
            
            // Calcular intervalo de linhas a mostrar
            const startIdx = (pageNum - 1) * ROWS_PER_PAGE;
            const endIdx = Math.min(startIdx + ROWS_PER_PAGE, filteredRows.length);
            
            // Esconder todas as linhas
            filteredRows.forEach(row => {
                row.style.display = 'none';
            });
            
            // Mostrar apenas as linhas da página atual
            for (let i = startIdx; i < endIdx; i++) {
                if (filteredRows[i]) {
                    filteredRows[i].style.display = '';
                }
            }
            
            // Atualizar controles de paginação
            updatePaginationControls();
        }
        
        // Atualizar controles de paginação (destacar página atual)
        function updatePaginationControls() {
            // Atualizar classe ativa nos botões de página
            const buttons = document.querySelectorAll('.pagination-button');
            buttons.forEach(button => {
                if (button.innerText === currentPage.toString()) {
                    button.classList.add('active');
                } else {
                    button.classList.remove('active');
                }
            });
            
            // Atualizar texto informativo
            const pageInfo = document.getElementById('page-info');
            if (pageInfo) {
                pageInfo.innerText = `Página ${currentPage} de ${totalPages}`;
            }
        }
        
        // Expandir/colapsar detalhes
        function toggleDetails(processId) {
            const detailsRow = document.getElementById('details-' + processId);
            if (!detailsRow) return;
            
            // Verificar estado atual
            const isVisible = detailsRow.style.display === 'table-row';
            
            // Fechar todos os detalhes
            document.querySelectorAll('tr.details-row').forEach(row => {
                row.style.display = 'none';
            });
            
            // Remover classe active de todas as linhas
            document.querySelectorAll('tr.process-row').forEach(row => {
                row.classList.remove('active');
            });
            
            // Se não estava visível, abrir
            if (!isVisible) {
                detailsRow.style.display = 'table-row';
                document.querySelector(`tr[data-id="${processId}"]`).classList.add('active');
            }
        }
        
        // Alternar entre abas
        function openTab(evt, tabId) {
            // Esconder todos os conteúdos
            const tabcontents = document.getElementsByClassName('tabcontent');
            for (let i = 0; i < tabcontents.length; i++) {
                if (tabcontents[i].id.startsWith(tabId.split('-')[0])) {
                    tabcontents[i].style.display = 'none';
                }
            }
            
            // Remover classe active de todas as abas
            const tabs = evt.currentTarget.parentElement.getElementsByClassName('tab');
            for (let i = 0; i < tabs.length; i++) {
                tabs[i].className = tabs[i].className.replace(' active', '');
            }
            
            // Mostrar conteúdo atual e ativar aba
            document.getElementById(tabId).style.display = 'block';
            evt.currentTarget.className += ' active';
        }
        
        // Inicializar ordenação da tabela
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
                header.style.position = 'relative';
                header.style.paddingRight = '20px';
                header.style.cursor = 'pointer';
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
            
            // Guardar IDs das linhas na ordem original
            const processRows = {};
            const detailsRows = {};
            rows.forEach(row => {
                const processId = row.getAttribute('data-id');
                processRows[processId] = row;
                detailsRows[processId] = document.getElementById('details-' + processId);
            });
            
            // Remover todas as linhas
            rows.forEach(row => {
                const processId = row.getAttribute('data-id');
                if (processRows[processId]) tbody.removeChild(processRows[processId]);
                if (detailsRows[processId]) tbody.removeChild(detailsRows[processId]);
            });
            
            // Adicionar na nova ordem
            rows.forEach(row => {
                const processId = row.getAttribute('data-id');
                if (processRows[processId]) tbody.appendChild(processRows[processId]);
                if (detailsRows[processId]) tbody.appendChild(detailsRows[processId]);
            });
            
            // Salvar estado de ordenação
            tbody.setAttribute('data-sort-column', column);
            tbody.setAttribute('data-sort-dir', direction);
            
            // Atualizar filtro e paginação após ordenar
            filterTable();
        }
        
        // Ajustar para mobile
        function adjustTableForMobile() {
            if (window.innerWidth < 768) {
                const table = document.getElementById('processesTable');
                if (table) {
                    const headers = table.querySelectorAll('th');
                    
                    // Ajustar algumas colunas para ocuparem menos espaço
                    if (headers[5]) headers[5].style.display = 'none'; // Origem
                    if (headers[6]) headers[6].style.display = 'none'; // Produto
                    if (headers[10]) headers[10].style.display = 'none'; // Devolução vazio
                    if (headers[11]) headers[11].style.display = 'none'; // Mapa
                    if (headers[12]) headers[12].style.display = 'none'; // Nota fiscal
                    
                    // Esconder mesmas colunas nas linhas
                    table.querySelectorAll('tr').forEach(row => {
                        const cells = row.cells;
                        if (cells[5]) cells[5].style.display = 'none';
                        if (cells[6]) cells[6].style.display = 'none';
                        if (cells[10]) cells[10].style.display = 'none';
                        if (cells[11]) cells[11].style.display = 'none';
                        if (cells[12]) cells[12].style.display = 'none';
                    });
                }
            }
        }
    </script>
</body>
</html>"""
    
    # Salvar arquivo
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(html)
    
    return str(filepath), f"html_exports/{filename}"

def generate_html_report(filtered_df=None, process_ids=None, title="Relatório de Processos", include_details=True, client_filter=None, client_name=None, archived=False):
    """
    Função simplificada para gerar relatório HTML
    """
    from data import get_processes_df
    
    # Se não foi fornecido um DataFrame filtrado, criar um
    if filtered_df is None:
        filtered_df = get_processes_df(include_archived=archived)
        
        # Filtrar por IDs específicos se fornecidos
        if process_ids is not None:
            if isinstance(process_ids, list) and len(process_ids) > 0:
                filtered_df = filtered_df[filtered_df['id'].isin(process_ids)]
            else:
                # Se process_ids for vazio ou inválido, retornar DataFrame vazio
                import pandas as pd
                filtered_df = pd.DataFrame()
        
        # Filtrar por cliente
        if client_filter:
            from components.auth import get_users
            users = get_users()
            for user in users:
                if user.get('id') == client_filter and 'processes' in user:
                    client_processes = user.get('processes', [])
                    if client_processes:
                        filtered_df = filtered_df[filtered_df['id'].isin(client_processes)]
                    else:
                        # Se o cliente não tem processos atribuídos, retornar DataFrame vazio
                        import pandas as pd
                        filtered_df = pd.DataFrame()
    
    return generate_html_with_pagination(filtered_df, title, include_details, client_name, archived)