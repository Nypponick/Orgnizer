"""
Gerador de HTML com exportação e paginação mantendo o visual original
"""
import os
import uuid
import datetime
from pathlib import Path
import pandas as pd
from data import get_processes_df
from html_generator import generate_processes_table_html, get_download_link
from html_post_processor import process_html_file

def export_html_with_pagination(filtered_df=None, process_ids=None, title="Relatório de Processos", include_details=True, client_name=None, client_logo=None, archived=False):
    """
    Gera um arquivo HTML com a tabela de processos e adiciona paginação, mantendo o visual original.
    A versão responsiva para dispositivos móveis é automaticamente incluída.
    
    Args:
        filtered_df: DataFrame com os processos filtrados
        process_ids: Lista de IDs de processos para incluir
        title: Título do relatório
        include_details: Se True, inclui a seção de detalhes
        client_name: Nome do cliente para personalizar o relatório
        client_logo: Caminho para o logo do cliente
        archived: Se True, indica que estamos gerando relatório para processos arquivados
        
    Returns:
        tuple: (caminho do arquivo gerado, URL relativo)
    """
    # Primeiro geramos o HTML normal utilizando a função original
    filepath, filename = generate_processes_table_html(
        filtered_df=filtered_df,
        process_ids=process_ids,
        include_details=include_details,
        client_name=client_name,
        client_logo=client_logo,
        archived=archived
    )
    
    # Verificar se o arquivo foi gerado com sucesso
    if not filepath or not os.path.exists(filepath):
        return None, None
    
    # Aplicar as modificações de estilo para usar fonte Segoe UI e bordas sutis
    process_html_file(filepath)
    
    # Agora adicionamos o código de paginação ao arquivo gerado
    with open(filepath, 'r', encoding='utf-8') as f:
        html_content = f.read()
    
    # Adicionar CSS para paginação
    css_pagination = """
    /* Estilos para paginação */
    .pagination {
        display: flex;
        justify-content: center;
        align-items: center;
        flex-wrap: wrap;
        margin: 25px 0;
        user-select: none;
        gap: 8px;
    }
    
    .pagination-button {
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
    }
    
    .pagination-button:hover {
        background: #e0e0e0;
        border-color: #999;
    }
    
    .pagination-button.active {
        background: #2c3e50;
        color: white;
        border-color: #2c3e50;
        font-weight: bold;
        box-shadow: 0 2px 4px rgba(0,0,0,0.2);
    }
    
    .pagination-info {
        margin: 0 15px;
        font-size: 14px;
        color: #666;
        align-self: center;
        font-weight: 500;
    }
    
    .pagination-ellipsis {
        margin: 0 5px;
        color: #666;
        font-size: 16px;
        align-self: center;
    }
    
    /* Estilos para contadores de status */
    #statusCounts {
        display: flex;
        flex-wrap: wrap;
        gap: 8px;
        margin: 15px 0;
    }
    
    .status-count-item {
        padding: 6px 10px;
        border-radius: 15px;
        color: white;
        font-weight: bold;
        cursor: pointer;
        display: flex;
        align-items: center;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        transition: transform 0.2s, box-shadow 0.2s;
    }
    
    .status-count-item:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.15);
    }
    
    .status-count-badge {
        background-color: rgba(255,255,255,0.25);
        color: white;
        border-radius: 10px;
        padding: 2px 8px;
        margin-left: 8px;
        font-size: 0.85em;
    }
    
    /* Estilos para cabeçalhos ordenáveis */
    #processesTable th {
        position: relative;
        padding-right: 20px;  /* Espaço para o indicador */
        user-select: none;  /* Evitar seleção de texto ao clicar */
        transition: background-color 0.2s;
    }
    
    #processesTable th:not(:first-child) {
        cursor: pointer;
    }
    
    #processesTable th:not(:first-child):hover {
        background-color: #e9ecef;
    }
    
    .sort-indicator {
        position: absolute;
        right: 6px;
        top: 50%;
        transform: translateY(-50%);
        font-size: 0.75em;
        color: #495057;
    }
    
    /* Estilos para colunas redimensionáveis */
    .resize-handle {
        position: absolute;
        top: 0;
        right: 0;
        bottom: 0;
        width: 5px;
        cursor: col-resize;
        user-select: none;
    }
    
    .resize-handle:hover, .resizing .resize-handle {
        background-color: rgba(0,0,0,0.1);
    }
    
    .column-highlight {
        background-color: rgba(0,0,0,0.05);
    }
    
    th.resizing {
        background-color: #eaeaea !important;
    }
    """
    
    # Inserir CSS antes do fechamento do elemento style
    html_content = html_content.replace('</style>', css_pagination + '\n</style>')
    
    # Adicionar os containers para paginação e contadores de status antes do footer
    html_content = html_content.replace(
        '<div class="footer">',
        '<!-- Container para contadores de status -->\n<div id="statusCounts"></div>\n\n<!-- Container para paginação -->\n<div id="pagination-container"></div>\n\n<div class="footer">'
    )
    
    # Adicionar código para colunas redimensionáveis
    resizable_columns_script = ""
    if os.path.exists("resizable_columns.js"):
        with open("resizable_columns.js", "r", encoding="utf-8") as f:
            resizable_columns_script = f.read()
    
    # Incluir o script de micro-interações
    micro_animations_script = ""
    if os.path.exists("micro_animations.js"):
        with open("micro_animations.js", "r", encoding="utf-8") as f:
            micro_animations_script = f.read()
            
    # Adicionar o script de paginação
    pagination_script = """
    <script>
    """ + resizable_columns_script + """
    """ + micro_animations_script + """
        // Configuração de paginação
        const ROWS_PER_PAGE = 10;
        let currentPage = 1;
        let filteredRows = [];
        
        // Inicializar paginação quando a página carregar
        document.addEventListener('DOMContentLoaded', function() {
            // Após a tabela estar pronta e os filtros inicializados
            setTimeout(initPagination, 500);
            
            // Configurar seletores de filtro
            setTimeout(initStatusFilters, 600);
            
            // Adicionar evento de tecla Enter no campo de busca
            setTimeout(function() {
                const searchInput = document.getElementById('filterInput');
                if (searchInput) {
                    searchInput.addEventListener('keypress', function(e) {
                        if (e.key === 'Enter') {
                            e.preventDefault(); // Evitar comportamento padrão
                            filterTable(); // Executar a busca
                        }
                    });
                }
            }, 600);
            
            // Inicializar colunas redimensionáveis
            setTimeout(function() {
                if (typeof initResizableColumns === 'function') {
                    initResizableColumns();
                }
            }, 700);
            
            // Configurar ordenação de colunas
            setTimeout(initTableSorting, 700);
        });
        
        // Inicializar filtros de status
        function initStatusFilters() {
            console.log("Inicializando filtros de status...");
            
            // Obter status únicos da tabela
            const statusSet = new Set();
            document.querySelectorAll('#processesTable tbody tr.process-row').forEach(row => {
                const statusCell = row.querySelector('td:nth-child(2)');
                if (statusCell) {
                    const statusText = statusCell.textContent.trim();
                    if (statusText) {
                        statusSet.add(statusText);
                    }
                }
            });
            
            // Preencher dropdown de filtro de status
            const statusFilter = document.getElementById('statusFilter');
            if (statusFilter) {
                // Limpar todas as opções exceto a primeira (Todos)
                while (statusFilter.options.length > 1) {
                    statusFilter.remove(1);
                }
                
                // Adicionar cada status como opção
                statusSet.forEach(status => {
                    const option = document.createElement('option');
                    option.value = status;
                    option.textContent = status;
                    statusFilter.appendChild(option);
                });
                
                // Adicionar listener para mudanças no filtro
                statusFilter.addEventListener('change', filterTable);
            }
            
            // Também configurar os contadores de status
            updateStatusCounters();
        }
        
        // Atualizar contadores de status e adicionar listeners
        function updateStatusCounters() {
            const statusCounts = {};
            
            // Contar ocorrências de cada status
            document.querySelectorAll('#processesTable tbody tr.process-row').forEach(row => {
                const statusCell = row.querySelector('td:nth-child(2)');
                if (statusCell) {
                    const statusText = statusCell.textContent.trim();
                    statusCounts[statusText] = (statusCounts[statusText] || 0) + 1;
                }
            });
            
            // Criar elementos de contador de status
            const statusCountsContainer = document.getElementById('statusCounts');
            if (statusCountsContainer) {
                statusCountsContainer.innerHTML = '';
                
                Object.keys(statusCounts).forEach(status => {
                    const count = statusCounts[status];
                    const statusColor = getStatusColor(status);
                    
                    const statusItem = document.createElement('div');
                    statusItem.className = 'status-count-item';
                    statusItem.style.backgroundColor = statusColor;
                    statusItem.innerHTML = `
                        ${status}
                        <span class="status-count-badge">${count}</span>
                    `;
                    
                    // Adicionar listener para filtrar por status
                    statusItem.addEventListener('click', function() {
                        const statusFilter = document.getElementById('statusFilter');
                        if (statusFilter) {
                            statusFilter.value = status;
                            filterTable();
                        }
                    });
                    
                    statusCountsContainer.appendChild(statusItem);
                });
            }
        }
        
        // Função para obter a cor do status (mesma cor para todos os contadores)
        function getStatusColor(status) {
            // Usar a cor do status "Concluído" para todos os contadores
            return '#2c3e50';  // Cor padrão para todos
        }
        
        // Função para alternar entre abas nos detalhes
        function openTab(evt, tabId) {
            // Obter o ID do processo (primeira parte do ID da aba)
            const processId = tabId.split('-')[0];
            
            // Ocultar apenas os conteúdos de aba deste processo
            var tabcontent = document.getElementsByClassName("tabcontent");
            for (var i = 0; i < tabcontent.length; i++) {
                if (tabcontent[i].id.startsWith(processId)) {
                    tabcontent[i].style.display = "none";
                }
            }
            
            // Remover a classe "active" apenas das abas deste processo
            var tablinks = evt.currentTarget.parentNode.getElementsByClassName("tab");
            for (var i = 0; i < tablinks.length; i++) {
                tablinks[i].className = tablinks[i].className.replace(" active", "");
            }
            
            // Mostrar a aba atual e adicionar a classe "active" ao botão que abriu a aba
            document.getElementById(tabId).style.display = "block";
            evt.currentTarget.className += " active";
        }
        
        // Função para mostrar uma página específica
        function showPage(page) {
            // Validar página
            currentPage = page;
            const totalPages = Math.ceil(filteredRows.length / ROWS_PER_PAGE);
            
            if (currentPage < 1) currentPage = 1;
            if (currentPage > totalPages) currentPage = totalPages;
            
            // Calcular linhas para mostrar
            const startIdx = (currentPage - 1) * ROWS_PER_PAGE;
            const endIdx = Math.min(startIdx + ROWS_PER_PAGE, filteredRows.length);
            
            console.log(`Mostrando página ${currentPage} de ${totalPages} (${startIdx} a ${endIdx})`);
            
            // Mostrar apenas as linhas da página atual
            for (let i = 0; i < filteredRows.length; i++) {
                filteredRows[i].style.display = (i >= startIdx && i < endIdx) ? "" : "none";
            }
            
            // Atualizar controles de paginação
            updatePaginationControls();
        }
        
        // Atualizar controles de paginação
        function updatePaginationControls() {
            const totalPages = Math.ceil(filteredRows.length / ROWS_PER_PAGE);
            const paginationContainer = document.getElementById('pagination-container');
            
            if (!paginationContainer) return;
            
            // Criar HTML para navegação de páginas
            let paginationHTML = '<div class="pagination">';
            
            // Botão anterior
            paginationHTML += `<button ${currentPage === 1 ? 'disabled' : ''} onclick="showPage(${currentPage - 1})">Anterior</button>`;
            
            // Mostrar número da página atual e total
            paginationHTML += `<span class="page-info">Página ${currentPage} de ${totalPages || 1}</span>`;
            
            // Botão próximo
            paginationHTML += `<button ${currentPage >= totalPages ? 'disabled' : ''} onclick="showPage(${currentPage + 1})">Próximo</button>`;
            
            paginationHTML += '</div>';
            
            paginationContainer.innerHTML = paginationHTML;
        }
        
        // Função para atualizar a paginação
        function updatePagination() {
            const totalPages = Math.ceil(filteredRows.length / ROWS_PER_PAGE);
            console.log(`Atualizando paginação: ${filteredRows.length} linhas, ${totalPages} páginas`);
            
            // Garantir que página atual é válida
            if (currentPage < 1) currentPage = 1;
            if (currentPage > totalPages && totalPages > 0) currentPage = totalPages;
            
            // Atualizar visualização
            showPage(currentPage);
        }
        
        // Estado de ordenação da tabela
        let currentSortColumn = -1;
        let sortDirection = 'asc';
        
        // Inicializar ordenação de colunas
        function initTableSorting() {
            console.log("Inicializando ordenação de colunas...");
            
            // Adicionar indicadores de ordenação e cursores aos cabeçalhos das colunas
            const headers = document.querySelectorAll('#processesTable thead th');
            headers.forEach((header, index) => {
                // Ignorar a primeira coluna (detalhes)
                if (index === 0) return;
                
                // Adicionar estilo cursor e indicador
                header.style.cursor = 'pointer';
                header.style.position = 'relative';
                
                // Adicionar evento de clique
                header.addEventListener('click', () => sortTable(index));
                
                // Adicionar indicador de ordenação (inicialmente oculto)
                const sortIndicator = document.createElement('span');
                sortIndicator.className = 'sort-indicator';
                sortIndicator.style.display = 'none';
                sortIndicator.style.position = 'absolute';
                sortIndicator.style.right = '8px';
                sortIndicator.style.fontSize = '0.8em';
                header.appendChild(sortIndicator);
            });
        }
        
        // Função para ordenar a tabela
        function sortTable(columnIndex) {
            console.log(`Ordenando coluna ${columnIndex}`);
            
            // Atualizar direção se estamos clicando na mesma coluna
            if (columnIndex === currentSortColumn) {
                sortDirection = sortDirection === 'asc' ? 'desc' : 'asc';
            } else {
                currentSortColumn = columnIndex;
                sortDirection = 'asc';
            }
            
            // Atualizar indicadores visuais
            updateSortIndicators(columnIndex);
            
            // Coletar todas as linhas (não apenas as filtradas)
            const rows = Array.from(document.querySelectorAll('#processesTable tbody tr.process-row'));
            
            // Ordenar as linhas
            rows.sort((rowA, rowB) => {
                // Obter células da coluna que estamos ordenando
                const cellA = rowA.cells[columnIndex].textContent.trim();
                const cellB = rowB.cells[columnIndex].textContent.trim();
                
                // Determinar se a célula contém uma data (formato DD/MM/YYYY)
                const isDateA = /^(\d{1,2})\/(\d{1,2})\/(\d{4})$/.test(cellA);
                const isDateB = /^(\d{1,2})\/(\d{1,2})\/(\d{4})$/.test(cellB);
                
                // Comparar datas se ambas forem datas
                if (isDateA && isDateB) {
                    // Converter formato DD/MM/YYYY para um formato adequado para comparação
                    // Formato: ANO-MÊS-DIA para garantir ordenação lexicográfica correta
                    const partsA = cellA.split('/');
                    const partsB = cellB.split('/');
                    
                    // Verificar se temos 3 partes em cada data (dia, mês, ano)
                    if (partsA.length != 3 || partsB.length != 3) {
                        // Fallback para comparação de texto se formato for inválido
                        return sortDirection === 'asc' 
                            ? cellA.localeCompare(cellB) 
                            : cellB.localeCompare(cellA);
                    }
                    
                    // Valores dos dias, meses e anos
                    // No formato brasileiro: DD/MM/AAAA
                    // partsA[0] = Dia, partsA[1] = Mês, partsA[2] = Ano
                    
                    // Garantir que anos tenham 4 dígitos
                    const yearA = partsA[2].padStart(4, '0');
                    const yearB = partsB[2].padStart(4, '0');
                    
                    // Garantir que meses e dias tenham 2 dígitos
                    const monthA = partsA[1].padStart(2, '0');
                    const monthB = partsB[1].padStart(2, '0');
                    const dayA = partsA[0].padStart(2, '0');
                    const dayB = partsB[0].padStart(2, '0');
                    
                    // Criar strings no formato AAAA-MM-DD para comparação lexicográfica
                    const dateStrA = `${yearA}-${monthA}-${dayA}`;
                    const dateStrB = `${yearB}-${monthB}-${dayB}`;
                    
                    // Comparar as strings de data no formato AAAA-MM-DD
                    // Para ETA (data estimada de chegada):
                    // - Ordem crescente (asc): mostra primeiro as datas mais próximas/antigas (ex: 2024-05-01 antes de 2024-06-01)
                    // - Ordem decrescente (desc): mostra primeiro as datas mais distantes/recentes (ex: 2024-06-01 antes de 2024-05-01)
                    return sortDirection === 'asc' 
                        ? dateStrA.localeCompare(dateStrB)  // Crescente: data mais antiga/próxima primeiro
                        : dateStrB.localeCompare(dateStrA);  // Decrescente: data mais recente/distante primeiro
                }
                
                // Determinar se ambas as células contêm números
                const isNumberA = !isNaN(parseFloat(cellA)) && isFinite(cellA);
                const isNumberB = !isNaN(parseFloat(cellB)) && isFinite(cellB);
                
                // Comparar numericamente se ambos forem números
                if (isNumberA && isNumberB) {
                    return sortDirection === 'asc' 
                        ? parseFloat(cellA) - parseFloat(cellB) 
                        : parseFloat(cellB) - parseFloat(cellA);
                }
                
                // Comparação padrão para texto
                return sortDirection === 'asc' 
                    ? cellA.localeCompare(cellB) 
                    : cellB.localeCompare(cellA);
            });
            
            // Reordenar as linhas no DOM
            const tbody = document.querySelector('#processesTable tbody');
            rows.forEach(row => {
                tbody.appendChild(row);
                
                // Também mover a linha de detalhes associada, se houver
                const detailsRow = document.getElementById(`details-${row.id.replace('row-', '')}`);
                if (detailsRow) {
                    tbody.appendChild(detailsRow);
                }
            });
            
            // Atualizar filteredRows com base no filtro atual
            filterTable();
        }
        
        // Atualizar indicadores de ordenação
        function updateSortIndicators(columnIndex) {
            const indicators = document.querySelectorAll('.sort-indicator');
            
            indicators.forEach((indicator, index) => {
                // Ocultar todos os indicadores primeiro
                indicator.style.display = 'none';
                
                // Mostrar apenas o indicador na coluna atual
                if (index + 1 === columnIndex) {  // +1 porque pulamos a coluna 0 ao adicionar os indicadores
                    indicator.style.display = 'inline';
                    indicator.textContent = sortDirection === 'asc' ? '▲' : '▼';
                }
            });
        }
        
        // Inicializar paginação
        function initPagination() {
            console.log("Inicializando paginação...");
            
            // Preservar a função original de alternar detalhes e de filtrar
            const originalToggleDetails = window.toggleDetails;
            const originalFilterTable = window.filterTable;
            
            // Substituir a função de alternar detalhes para garantir que apenas um seja aberto por vez
            window.toggleDetails = function(processId) {
                // Fechar todos os detalhes primeiro
                document.querySelectorAll('.details-row').forEach(row => {
                    // Armazenar o ID do processo desta linha
                    const rowId = row.id.replace('details-', '');
                    
                    // Se for diferente do processo atual, fechar
                    if (rowId !== processId) {
                        row.style.display = 'none';
                    }
                });
                
                // Alternar a visibilidade da linha clicada
                const detailsRow = document.getElementById('details-' + processId);
                if (detailsRow) {
                    // Alternar a visibilidade da linha de detalhes
                    if (detailsRow.style.display === 'none') {
                        detailsRow.style.display = 'table-row';
                        
                        // Ativar a primeira aba por padrão quando abre os detalhes
                        const firstTablink = detailsRow.querySelector('.tab');
                        if (firstTablink) {
                            // Extrair o ID da aba do onclick de forma mais robusta
                            const onclickAttr = firstTablink.getAttribute('onclick');
                            let tabId = null;
                            
                            // Tentar diferentes padrões para acomodar várias formas de definir onclick
                            const match1 = onclickAttr.match(/openTab\(event,\s*['"]([^'"]+)['"]\)/);
                            const match2 = onclickAttr.match(/openTab\(this,\s*['"]([^'"]+)['"]\)/);
                            const match3 = onclickAttr.match(/openTab\([^,]*,\s*['"]([^'"]+)['"]\)/);
                            
                            if (match1 && match1[1]) tabId = match1[1];
                            else if (match2 && match2[1]) tabId = match2[1];
                            else if (match3 && match3[1]) tabId = match3[1];
                            if (tabId) {
                                // Obter ID do processo
                                const processId = tabId.split('-')[0];
                                
                                // Ocultar todas as abas de conteúdo deste processo
                                const tabcontents = document.querySelectorAll('.tabcontent');
                                tabcontents.forEach(tab => {
                                    if (tab.id.startsWith(processId)) {
                                        tab.style.display = 'none';
                                    }
                                });
                                
                                // Mostrar a primeira aba
                                const firstTab = document.getElementById(tabId);
                                if (firstTab) {
                                    firstTab.style.display = 'block';
                                }
                                
                                // Remover classe ativa de todas as abas deste processo
                                const tabs = detailsRow.querySelectorAll('.tab');
                                tabs.forEach(tab => tab.classList.remove('active'));
                                
                                // Marcar a primeira aba como ativa
                                firstTablink.classList.add('active');
                            }
                        }
                    } else {
                        detailsRow.style.display = 'none';
                    }
                }
                
                // Chamar a função original para manter outros comportamentos
                if (typeof originalToggleDetails === 'function') {
                    originalToggleDetails(processId);
                }
            };
            
            // Substituir a função de filtragem para implementar a paginação
            window.filterTable = function() {
                // Obter valores de filtro
                const searchText = document.getElementById('filterInput')?.value.toLowerCase() || '';
                const selectedType = document.getElementById('processTypeFilter')?.value.toLowerCase() || 'todos';
                const selectedStatus = document.getElementById('statusFilter')?.value || 'todos';
                
                console.log(`Filtrando: texto="${searchText}", tipo="${selectedType}", status="${selectedStatus}"`);
                
                // Aplicar os filtros a todas as linhas
                const rows = Array.from(document.querySelectorAll('#processesTable tbody tr.process-row'));
                
                rows.forEach(row => {
                    let showRow = true;
                    
                    // Filtrar por texto de busca
                    if (searchText) {
                        const rowText = row.textContent.toLowerCase();
                        if (!rowText.includes(searchText)) {
                            showRow = false;
                        }
                    }
                    
                    // Filtrar por tipo de processo
                    if (selectedType !== 'todos') {
                        // Obter o tipo como atributo data-type para maior precisão
                        const rowType = row.getAttribute('data-type') || '';
                        // Também buscar o texto da célula como backup
                        const processTypeText = row.querySelector('td:nth-child(3)')?.textContent.toLowerCase() || '';
                        
                        console.log(`Comparando tipo: row-type="${rowType}", selectedType="${selectedType}", célula="${processTypeText}"`);
                        
                        // Verificar correspondência no atributo data-type ou no texto da célula
                        const matchesType = 
                            rowType.toLowerCase() === selectedType || 
                            processTypeText.includes('importação') && selectedType === 'importacao' ||
                            processTypeText.includes('exportação') && selectedType === 'exportacao';
                            
                        if (!matchesType) {
                            showRow = false;
                        }
                    }
                    
                    // Filtrar por status
                    if (selectedStatus !== 'todos') {
                        const statusText = row.querySelector('td:nth-child(2)')?.textContent.trim() || '';
                        if (statusText !== selectedStatus) {
                            showRow = false;
                        }
                    }
                    
                    // Aplicar visibilidade temporária para que possamos coletar linhas visíveis
                    row.style.display = showRow ? '' : 'none';
                });
                
                // Coletar linhas que passaram no filtro
                filteredRows = rows.filter(row => row.style.display !== 'none');
                
                // Fechar todos os detalhes
                document.querySelectorAll('.details-row').forEach(row => {
                    row.style.display = 'none';
                });
                
                // Esconder todas as linhas principais novamente (serão exibidas pela paginação)
                rows.forEach(row => {
                    row.style.display = 'none';
                });
                
                // Voltar para a primeira página e atualizar
                currentPage = 1;
                updatePagination();
                updateStatusCounters();
                showPage(currentPage);
                
                // Executar a função original depois da nossa implementação
                if (typeof originalFilterTable === 'function') {
                    originalFilterTable();
                }
            };
            
            // Aplicar a filtragem inicialmente
            filterTable();
        }
        
        // Atualizar controles de paginação
        function updatePagination() {
            const totalPages = Math.ceil(filteredRows.length / ROWS_PER_PAGE);
            const paginationContainer = document.getElementById('pagination-container');
            
            // Limpar container
            paginationContainer.innerHTML = '';
            
            // Se houver apenas uma página, não mostrar paginação
            if (totalPages <= 1) {
                return;
            }
            
            // Criar div de paginação
            const pagination = document.createElement('div');
            pagination.className = 'pagination';
            
            // Botão Anterior
            const prevButton = document.createElement('button');
            prevButton.className = 'pagination-button';
            prevButton.innerText = '« Anterior';
            prevButton.addEventListener('click', () => {
                if (currentPage > 1) {
                    showPage(currentPage - 1);
                }
            });
            pagination.appendChild(prevButton);
            
            // Determinar quais botões de página mostrar
            const maxButtons = 7;
            let startPage = Math.max(1, currentPage - Math.floor(maxButtons / 2));
            let endPage = Math.min(startPage + maxButtons - 1, totalPages);
            
            if (endPage - startPage + 1 < maxButtons) {
                startPage = Math.max(1, endPage - maxButtons + 1);
            }
            
            // Primeiro botão (se não estiver no range)
            if (startPage > 1) {
                const firstButton = document.createElement('button');
                firstButton.className = 'pagination-button';
                firstButton.innerText = '1';
                firstButton.addEventListener('click', () => showPage(1));
                pagination.appendChild(firstButton);
                
                // Elipses se houver gap
                if (startPage > 2) {
                    const ellipsis = document.createElement('span');
                    ellipsis.className = 'pagination-ellipsis';
                    ellipsis.innerText = '...';
                    pagination.appendChild(ellipsis);
                }
            }
            
            // Botões numerados
            for (let i = startPage; i <= endPage; i++) {
                const pageButton = document.createElement('button');
                pageButton.className = 'pagination-button';
                if (i === currentPage) {
                    pageButton.classList.add('active');
                }
                pageButton.innerText = i.toString();
                pageButton.addEventListener('click', () => showPage(i));
                pagination.appendChild(pageButton);
            }
            
            // Último botão (se não estiver no range)
            if (endPage < totalPages) {
                // Elipses se houver gap
                if (endPage < totalPages - 1) {
                    const ellipsis = document.createElement('span');
                    ellipsis.className = 'pagination-ellipsis';
                    ellipsis.innerText = '...';
                    pagination.appendChild(ellipsis);
                }
                
                const lastButton = document.createElement('button');
                lastButton.className = 'pagination-button';
                lastButton.innerText = totalPages.toString();
                lastButton.addEventListener('click', () => showPage(totalPages));
                pagination.appendChild(lastButton);
            }
            
            // Botão Próximo
            const nextButton = document.createElement('button');
            nextButton.className = 'pagination-button';
            nextButton.innerText = 'Próximo »';
            nextButton.addEventListener('click', () => {
                if (currentPage < totalPages) {
                    showPage(currentPage + 1);
                }
            });
            pagination.appendChild(nextButton);
            
            // Info de paginação
            const pageInfo = document.createElement('div');
            pageInfo.className = 'pagination-info';
            pageInfo.innerText = `Página ${currentPage} de ${totalPages} (${filteredRows.length} processos)`;
            pagination.appendChild(pageInfo);
            
            // Adicionar ao container
            paginationContainer.appendChild(pagination);
        }
        
        // Mostrar uma página específica
        function showPage(page) {
            // Atualizar página atual
            currentPage = page;
            
            // Calcular índices da página
            const startIdx = (page - 1) * ROWS_PER_PAGE;
            const endIdx = Math.min(startIdx + ROWS_PER_PAGE, filteredRows.length);
            
            // Ocultar todas as linhas primeiro
            filteredRows.forEach(row => row.style.display = 'none');
            
            // Mostrar linhas da página atual
            for (let i = startIdx; i < endIdx; i++) {
                filteredRows[i].style.display = '';
            }
            
            // Ocultar linhas de detalhes (para garantir state consistente)
            document.querySelectorAll('.details-row').forEach(row => {
                row.style.display = 'none';
            });
            
            // Atualizar botões da paginação
            document.querySelectorAll('.pagination-button').forEach(button => {
                button.classList.remove('active');
                if (button.innerText === page.toString()) {
                    button.classList.add('active');
                }
            });
            
            // Atualizar info de paginação
            const pageInfo = document.querySelector('.pagination-info');
            if (pageInfo) {
                const totalPages = Math.ceil(filteredRows.length / ROWS_PER_PAGE);
                pageInfo.innerText = `Página ${page} de ${totalPages} (${filteredRows.length} processos)`;
            }
        }
    </script>
    """
    
    # Adicionar script antes do fechamento do body
    html_content = html_content.replace('</body>', pagination_script + '\n</body>')
    
    # Salvar o arquivo modificado
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    return filepath, filename