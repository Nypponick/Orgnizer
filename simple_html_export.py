"""
Versão simplificada do gerador de HTML com paginação
"""
import os
import uuid
import datetime
from pathlib import Path
import pandas as pd

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

def generate_html_with_pagination(df, title="Processos de Importação/Exportação", include_details=True, client_name=None):
    """
    Gera um HTML com tabela de processos e paginação
    """
    # Criar diretório para exportação se não existir
    export_dir = Path("html_exports")
    export_dir.mkdir(exist_ok=True)
    
    # Gerar nome de arquivo único
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    file_id = str(uuid.uuid4())[:8]
    filename = f"processos_paginados_{timestamp}_{file_id}.html"
    filepath = export_dir / filename
    
    # Cabeçalho do HTML
    html = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f5;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            padding: 20px;
            box-shadow: 0 0 10px rgba(0,0,0,0.1);
            border-radius: 5px;
        }}
        h1 {{
            color: #333;
            margin-top: 0;
            padding-bottom: 10px;
            border-bottom: 1px solid #eee;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
        }}
        th, td {{
            padding: 10px;
            border: 1px solid #ddd;
            text-align: left;
        }}
        th {{
            background-color: #f2f2f2;
            position: sticky;
            top: 0;
        }}
        tr:nth-child(even) {{
            background-color: #f9f9f9;
        }}
        tr:hover {{
            background-color: #f1f1f1;
        }}
        .status-badge {{
            display: inline-block;
            padding: 5px 10px;
            color: white;
            border-radius: 20px;
            font-weight: bold;
            text-align: center;
            min-width: 100px;
        }}
        .pagination {{
            display: flex;
            justify-content: center;
            margin: 20px 0;
            flex-wrap: wrap;
        }}
        .pagination button {{
            margin: 0 5px;
            padding: 8px 12px;
            cursor: pointer;
            background-color: #f2f2f2;
            border: 1px solid #ddd;
            border-radius: 3px;
        }}
        .pagination button.active {{
            background-color: #4CAF50;
            color: white;
            border-color: #4CAF50;
        }}
        .pagination button:hover:not(.active) {{
            background-color: #ddd;
        }}
        .search-container {{
            margin: 20px 0;
        }}
        .search-container input {{
            padding: 8px;
            width: 300px;
            border: 1px solid #ddd;
            border-radius: 4px;
        }}
        .type-filter {{
            margin-left: 20px;
            padding: 8px;
            border: 1px solid #ddd;
            border-radius: 4px;
        }}
        .status-filters {{
            display: flex;
            flex-wrap: wrap;
            gap: 10px;
            margin: 20px 0;
            padding: 10px;
            background-color: #f9f9f9;
            border-radius: 4px;
        }}
        .status-filter {{
            padding: 5px 10px;
            background-color: #fff;
            border: 1px solid #ddd;
            border-radius: 15px;
            cursor: pointer;
        }}
        .status-filter.active {{
            background-color: #e0e0e0;
            font-weight: bold;
        }}
        .status-counter {{
            display: inline-block;
            background-color: #f2f2f2;
            padding: 2px 6px;
            border-radius: 10px;
            font-size: 12px;
            margin-left: 5px;
        }}
        .process-details {{
            display: none;
            padding: 15px;
            background-color: #f9f9f9;
            border: 1px solid #ddd;
            margin-bottom: 10px;
            border-radius: 4px;
        }}
        .details-grid {{
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 10px;
        }}
        @media (max-width: 768px) {{
            .details-grid {{
                grid-template-columns: repeat(2, 1fr);
            }}
        }}
        @media (max-width: 576px) {{
            .details-grid {{
                grid-template-columns: 1fr;
            }}
        }}
        .detail-item {{
            margin-bottom: 5px;
        }}
        .detail-label {{
            font-weight: bold;
            margin-bottom: 3px;
        }}
        .detail-value {{
            padding: 5px;
            background-color: #fff;
            border-radius: 3px;
            border: 1px solid #eee;
        }}
        .timestamp {{
            color: #777;
            font-size: 14px;
            margin-bottom: 20px;
        }}
        .footer {{
            margin-top: 30px;
            text-align: center;
            color: #777;
            font-size: 14px;
            border-top: 1px solid #eee;
            padding-top: 10px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>{title}{' - '+client_name if client_name else ''}</h1>
        <div class="timestamp">Gerado em: {datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")}</div>
        
        <div class="search-container">
            <input type="text" id="searchInput" placeholder="Buscar nos processos...">
            <select class="type-filter" id="typeFilter">
                <option value="todos">Todos os Tipos</option>
                <option value="importacao">Importação</option>
                <option value="exportacao">Exportação</option>
            </select>
        </div>
        
        <div class="status-filters" id="statusFilters">
            <!-- Status filters will be added here via JS -->
        </div>
        
        <div>Total de processos: <span id="processCount">{len(df)}</span></div>
        
        <table id="processTable">
            <thead>
                <tr>
                    <th>ID</th>
                    <th>Status</th>
                    <th>Tipo</th>
                    <th>Referência</th>
                    <th>PO</th>
                    <th>Origem</th>
                    <th>Produto</th>
                    <th>ETA</th>
                    <th>Vencimento FT</th>
                    <th>Dias Armazenados</th>
                    <th>Ações</th>
                </tr>
            </thead>
            <tbody>
"""

    # Adicionar linhas da tabela
    for _, row in df.iterrows():
        process_id = row['id']
        status = row.get('status', '')
        status_color = get_status_color(status)
        
        html += f"""
                <tr data-id="{process_id}" data-status="{status}" data-type="{row.get('type', '')}">
                    <td>{process_id}</td>
                    <td><span class="status-badge" style="background-color: {status_color}">{status}</span></td>
                    <td>{"Exportação" if row.get('type', '') == "exportacao" else "Importação"}</td>
                    <td>{row.get('ref', '')}</td>
                    <td>{row.get('po', '')}</td>
                    <td>{row.get('origin', '')}</td>
                    <td>{row.get('product', '')}</td>
                    <td>{format_date(row.get('eta', ''))}</td>
                    <td>{format_date(row.get('free_time_expiry', ''))}</td>
                    <td>{row.get('storage_days', '')}</td>
                    <td><button onclick="toggleDetails('{process_id}')">Detalhes</button></td>
                </tr>
"""
        
        # Adicionar div de detalhes se solicitado
        if include_details:
            html += f"""
                <tr>
                    <td colspan="11">
                        <div id="details-{process_id}" class="process-details">
                            <div class="details-grid">
                                <div class="detail-item">
                                    <div class="detail-label">ID do Processo</div>
                                    <div class="detail-value">{process_id}</div>
                                </div>
                                <div class="detail-item">
                                    <div class="detail-label">Status</div>
                                    <div class="detail-value">{status}</div>
                                </div>
                                <div class="detail-item">
                                    <div class="detail-label">Tipo</div>
                                    <div class="detail-value">{"Exportação" if row.get('type', '') == "exportacao" else "Importação"}</div>
                                </div>
                                <div class="detail-item">
                                    <div class="detail-label">Referência</div>
                                    <div class="detail-value">{row.get('ref', '')}</div>
                                </div>
                                <div class="detail-item">
                                    <div class="detail-label">PO</div>
                                    <div class="detail-value">{row.get('po', '')}</div>
                                </div>
                                <div class="detail-item">
                                    <div class="detail-label">Origem</div>
                                    <div class="detail-value">{row.get('origin', '')}</div>
                                </div>
                                <div class="detail-item">
                                    <div class="detail-label">Produto</div>
                                    <div class="detail-value">{row.get('product', '')}</div>
                                </div>
                                <div class="detail-item">
                                    <div class="detail-label">ETA</div>
                                    <div class="detail-value">{format_date(row.get('eta', ''))}</div>
                                </div>
                                <div class="detail-item">
                                    <div class="detail-label">Free Time</div>
                                    <div class="detail-value">{row.get('free_time', '')} dias</div>
                                </div>
                                <div class="detail-item">
                                    <div class="detail-label">Vencimento Free Time</div>
                                    <div class="detail-value">{format_date(row.get('free_time_expiry', ''))}</div>
                                </div>
                                <div class="detail-item">
                                    <div class="detail-label">Devolução Vazio</div>
                                    <div class="detail-value">{format_date(row.get('empty_return', ''))}</div>
                                </div>
                                <div class="detail-item">
                                    <div class="detail-label">Entrada no Porto</div>
                                    <div class="detail-value">{format_date(row.get('port_entry_date', ''))}</div>
                                </div>
                                <div class="detail-item">
                                    <div class="detail-label">Início Período</div>
                                    <div class="detail-value">{format_date(row.get('current_period_start', ''))}</div>
                                </div>
                                <div class="detail-item">
                                    <div class="detail-label">Vencimento Período</div>
                                    <div class="detail-value">{format_date(row.get('current_period_expiry', ''))}</div>
                                </div>
                                <div class="detail-item">
                                    <div class="detail-label">Dias Armazenados</div>
                                    <div class="detail-value">{row.get('storage_days', '')}</div>
                                </div>
                            </div>
"""
            
            # Adicionar eventos se existirem
            if 'events' in row and row['events']:
                html += """
                            <h3>Histórico de Eventos</h3>
                            <table style="width: 100%;">
                                <thead>
                                    <tr>
                                        <th>Data</th>
                                        <th>Descrição</th>
                                        <th>Usuário</th>
                                    </tr>
                                </thead>
                                <tbody>
"""
                
                for event in row['events']:
                    # Pular eventos de atribuição se for relatório para cliente
                    if client_name and "atribuído ao cliente" in event.get('description', ''):
                        continue
                        
                    html += f"""
                                    <tr>
                                        <td>{format_date(event.get('date', ''))}</td>
                                        <td>{event.get('description', '')}</td>
                                        <td>{event.get('user', '')}</td>
                                    </tr>
"""
                
                html += """
                                </tbody>
                            </table>
"""
            
            html += """
                        </div>
                    </td>
                </tr>
"""
    
    # Fechar a tabela e adicionar paginação e scripts
    html += """
            </tbody>
        </table>
        
        <div class="pagination" id="pagination"></div>
        
        <div class="footer">
            © 2025 JGR BROKER - Todos os direitos reservados
        </div>
    </div>
    
    <script>
        // Configurações de paginação
        const rowsPerPage = 10;
        let currentPage = 1;
        let filteredRows = [];
        
        // Inicialização quando o DOM estiver carregado
        document.addEventListener('DOMContentLoaded', function() {
            initializeStatusFilters();
            setupFilterListeners();
            applyFilters(); // Isso irá inicializar a paginação também
        });
        
        // Inicializar filtros de status
        function initializeStatusFilters() {
            const rows = Array.from(document.querySelectorAll('#processTable tbody tr[data-id]'));
            const statusFilters = document.getElementById('statusFilters');
            const statusMap = {};
            
            // Contar status
            rows.forEach(row => {
                const status = row.getAttribute('data-status');
                if (status) {
                    statusMap[status] = (statusMap[status] || 0) + 1;
                }
            });
            
            // Adicionar filtro "Todos"
            const allFilter = document.createElement('div');
            allFilter.className = 'status-filter active';
            allFilter.setAttribute('data-status', 'todos');
            allFilter.innerHTML = 'Todos <span class="status-counter">' + rows.length + '</span>';
            allFilter.addEventListener('click', function() {
                setActiveStatusFilter('todos');
                applyFilters();
            });
            statusFilters.appendChild(allFilter);
            
            // Adicionar filtros para cada status
            Object.keys(statusMap).sort().forEach(status => {
                const filter = document.createElement('div');
                filter.className = 'status-filter';
                filter.setAttribute('data-status', status);
                filter.innerHTML = status + ' <span class="status-counter">' + statusMap[status] + '</span>';
                filter.addEventListener('click', function() {
                    setActiveStatusFilter(status);
                    applyFilters();
                });
                statusFilters.appendChild(filter);
            });
        }
        
        // Configurar listeners para os filtros
        function setupFilterListeners() {
            const searchInput = document.getElementById('searchInput');
            const typeFilter = document.getElementById('typeFilter');
            
            if (searchInput) {
                searchInput.addEventListener('input', applyFilters);
            }
            
            if (typeFilter) {
                typeFilter.addEventListener('change', applyFilters);
            }
        }
        
        // Definir filtro de status ativo
        function setActiveStatusFilter(status) {
            document.querySelectorAll('.status-filter').forEach(filter => {
                if (filter.getAttribute('data-status') === status) {
                    filter.classList.add('active');
                } else {
                    filter.classList.remove('active');
                }
            });
        }
        
        // Aplicar todos os filtros e atualizar tabela
        function applyFilters() {
            const searchText = document.getElementById('searchInput').value.toLowerCase();
            const typeFilter = document.getElementById('typeFilter').value;
            const statusFilter = document.querySelector('.status-filter.active').getAttribute('data-status');
            
            const rows = Array.from(document.querySelectorAll('#processTable tbody tr[data-id]'));
            
            // Esconder todos os detalhes
            document.querySelectorAll('.process-details').forEach(details => {
                details.style.display = 'none';
            });
            
            // Filtrar linhas
            filteredRows = rows.filter(row => {
                // Filtro de texto
                let matchesText = !searchText;
                if (searchText) {
                    const cells = Array.from(row.querySelectorAll('td'));
                    for (let cell of cells) {
                        if (cell.textContent.toLowerCase().includes(searchText)) {
                            matchesText = true;
                            break;
                        }
                    }
                }
                
                // Filtro de tipo
                const type = row.getAttribute('data-type');
                const matchesType = typeFilter === 'todos' || 
                                   (type === typeFilter) || 
                                   (typeFilter === 'importacao' && type === '');
                
                // Filtro de status
                const status = row.getAttribute('data-status');
                const matchesStatus = statusFilter === 'todos' || status === statusFilter;
                
                return matchesText && matchesType && matchesStatus;
            });
            
            // Atualizar contador
            document.getElementById('processCount').textContent = filteredRows.length;
            
            // Esconder todas as linhas
            rows.forEach(row => {
                const rowId = row.getAttribute('data-id');
                row.style.display = 'none';
                
                // Esconder linha de detalhe associada também
                const nextRow = row.nextElementSibling;
                if (nextRow) {
                    nextRow.style.display = 'none';
                }
            });
            
            // Inicializar paginação
            updatePagination();
            
            // Mostrar a primeira página
            currentPage = 1;
            showPage(currentPage);
        }
        
        // Atualizar interface de paginação
        function updatePagination() {
            const paginationEl = document.getElementById('pagination');
            paginationEl.innerHTML = '';
            
            const totalPages = Math.ceil(filteredRows.length / rowsPerPage);
            
            // Se tiver apenas uma página, não mostrar a paginação
            if (totalPages <= 1) {
                return;
            }
            
            // Botão para página anterior
            const prevButton = document.createElement('button');
            prevButton.textContent = '⟨';
            prevButton.addEventListener('click', () => {
                if (currentPage > 1) {
                    showPage(currentPage - 1);
                }
            });
            paginationEl.appendChild(prevButton);
            
            // Mostrar no máximo 7 botões de página
            const maxButtons = 7;
            const startPage = Math.max(1, Math.min(
                currentPage - Math.floor(maxButtons / 2),
                totalPages - maxButtons + 1
            ));
            
            const endPage = Math.min(totalPages, startPage + maxButtons - 1);
            
            // Primeiro botão (se não incluído no range normal)
            if (startPage > 1) {
                const firstButton = document.createElement('button');
                firstButton.textContent = '1';
                firstButton.addEventListener('click', () => showPage(1));
                paginationEl.appendChild(firstButton);
                
                // Adicionar elipses se houver gap
                if (startPage > 2) {
                    const ellipsis = document.createElement('span');
                    ellipsis.textContent = '...';
                    ellipsis.style.margin = '0 5px';
                    paginationEl.appendChild(ellipsis);
                }
            }
            
            // Adicionar botões para cada página no range
            for (let i = startPage; i <= endPage; i++) {
                const button = document.createElement('button');
                button.textContent = i.toString();
                if (i === currentPage) {
                    button.classList.add('active');
                }
                button.addEventListener('click', () => showPage(i));
                paginationEl.appendChild(button);
            }
            
            // Último botão (se não incluído no range normal)
            if (endPage < totalPages) {
                // Adicionar elipses se houver gap
                if (endPage < totalPages - 1) {
                    const ellipsis = document.createElement('span');
                    ellipsis.textContent = '...';
                    ellipsis.style.margin = '0 5px';
                    paginationEl.appendChild(ellipsis);
                }
                
                const lastButton = document.createElement('button');
                lastButton.textContent = totalPages.toString();
                lastButton.addEventListener('click', () => showPage(totalPages));
                paginationEl.appendChild(lastButton);
            }
            
            // Botão para próxima página
            const nextButton = document.createElement('button');
            nextButton.textContent = '⟩';
            nextButton.addEventListener('click', () => {
                if (currentPage < totalPages) {
                    showPage(currentPage + 1);
                }
            });
            paginationEl.appendChild(nextButton);
        }
        
        // Mostrar uma página específica
        function showPage(page) {
            currentPage = page;
            
            // Calcular índices
            const startIdx = (page - 1) * rowsPerPage;
            const endIdx = Math.min(startIdx + rowsPerPage, filteredRows.length);
            
            // Mostrar apenas as linhas da página atual
            for (let i = 0; i < filteredRows.length; i++) {
                const row = filteredRows[i];
                const rowId = row.getAttribute('data-id');
                
                // Linha de dados
                if (i >= startIdx && i < endIdx) {
                    row.style.display = '';
                    
                    // Linha de detalhes (sempre mostrar, mas pode estar hidden)
                    const nextRow = row.nextElementSibling;
                    if (nextRow) {
                        nextRow.style.display = '';
                    }
                }
            }
            
            // Atualizar botões de paginação
            document.querySelectorAll('#pagination button').forEach(button => {
                if (button.textContent === page.toString()) {
                    button.classList.add('active');
                } else {
                    button.classList.remove('active');
                }
            });
        }
        
        // Mostrar/ocultar detalhes de um processo
        function toggleDetails(processId) {
            const detailsEl = document.getElementById('details-' + processId);
            if (detailsEl) {
                if (detailsEl.style.display === 'block') {
                    detailsEl.style.display = 'none';
                } else {
                    // Fechar todos os outros detalhes primeiro
                    document.querySelectorAll('.process-details').forEach(details => {
                        details.style.display = 'none';
                    });
                    
                    // Abrir os detalhes deste processo
                    detailsEl.style.display = 'block';
                }
            }
        }
    </script>
</body>
</html>
"""
    
    # Salvar o arquivo HTML
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(html)
    
    return str(filepath), f"html_exports/{filename}"

def export_processes_to_html(filtered_df=None, process_ids=None, title="Relatório de Processos", client_name=None):
    """
    Função de integração para exportar os processos para HTML com paginação
    """
    from data import get_processes_df
    
    # Se não foi fornecido um DataFrame filtrado, criar um
    if filtered_df is None:
        filtered_df = get_processes_df()
        
        # Filtrar por IDs específicos se fornecidos
        if process_ids:
            filtered_df = filtered_df[filtered_df['id'].isin(process_ids)]
    
    return generate_html_with_pagination(filtered_df, title, True, client_name)