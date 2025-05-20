"""
Gerador de HTML paginado com visual original
"""
import os
import uuid
import datetime
from pathlib import Path
import pandas as pd
from html_generator import generate_processes_table_html, get_download_link

def generate_paginated_html(filtered_df=None, process_ids=None, title="Relatório de Processos", include_details=True, client_name=None, archived=False):
    """
    Gera um arquivo HTML paginado mantendo o visual original.
    
    Args:
        filtered_df: DataFrame com os processos filtrados
        process_ids: Lista de IDs de processos para incluir
        title: Título do relatório
        include_details: Se True, inclui a seção de detalhes
        client_name: Nome do cliente para personalizar o relatório
        archived: Se True, indica que estamos gerando relatório para processos arquivados
        
    Returns:
        tuple: (caminho do arquivo gerado, URL relativo)
    """
    from data import get_processes_df
    
    # Se não foi fornecido um DataFrame filtrado, criar um
    if filtered_df is None:
        filtered_df = get_processes_df(include_archived=archived)
        
        # Filtrar por IDs específicos se fornecidos
        if process_ids:
            filtered_df = filtered_df[filtered_df['id'].isin(process_ids)]
    
    # Gerar HTML usando a função original
    filepath, filename = generate_processes_table_html(
        filtered_df=filtered_df,
        process_ids=process_ids,
        include_details=include_details,
        client_name=client_name,
        archived=archived
    )
    
    # Agora vamos adicionar a paginação ao arquivo HTML
    with open(filepath, 'r', encoding='utf-8') as f:
        html_content = f.read()
    
    # Inserir o CSS da paginação antes do fechamento do head
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
    """
    
    html_content = html_content.replace('</style>', css_pagination + '\n</style>')
    
    # Adicionar o container de paginação antes do footer
    html_content = html_content.replace(
        '<div class="footer">',
        '<!-- Container para paginação -->\n<div id="pagination-container"></div>\n\n<div class="footer">'
    )
    
    # Script de paginação
    pagination_script = """
    <script>
        // Configuração de paginação
        const ROWS_PER_PAGE = 10;
        let currentPage = 1;
        let filteredRows = [];
        
        // Inicializar paginação quando a página carregar
        document.addEventListener('DOMContentLoaded', function() {
            // Após a tabela estar pronta e os filtros inicializados
            setTimeout(initPagination, 500);
        });
        
        // Inicializar paginação
        function initPagination() {
            console.log("Inicializando paginação...");
            
            // Interceptar as funções originais
            const originalFilterTable = window.filterTable;
            const originalToggleDetails = window.toggleDetails;
            const originalOpenTab = window.openTab;
            
            // Substituir a função para abrir abas nos detalhes
            window.openTab = function(evt, tabId) {
                // Implementar a funcionalidade de abas
                const tabcontent = document.getElementsByClassName("tabcontent");
                for (let i = 0; i < tabcontent.length; i++) {
                    tabcontent[i].style.display = "none";
                }
                
                const tablinks = document.getElementsByClassName("tablink");
                for (let i = 0; i < tablinks.length; i++) {
                    tablinks[i].className = tablinks[i].className.replace(" active", "");
                }
                
                const tabElement = document.getElementById(tabId);
                if (tabElement) {
                    tabElement.style.display = "block";
                }
                
                if (evt && evt.currentTarget) {
                    evt.currentTarget.className += " active";
                }
                
                // Chamar a função original se existir
                if (originalOpenTab && typeof originalOpenTab === 'function') {
                    originalOpenTab.call(this, evt, tabId);
                }
            };
            
            // Substituir a função toggleDetails original para trabalhar com a paginação
            window.toggleDetails = function(processId) {
                // Primeiro, fechar todas as linhas de detalhes que estejam abertas
                document.querySelectorAll('#processesTable tbody tr.details-row').forEach(row => {
                    row.style.display = 'none';
                });
                
                // Depois, alternar a visibilidade da linha de detalhes clicada
                const detailsRow = document.getElementById('details-' + processId);
                if (detailsRow) {
                    // Se estiver oculto, mostrar (e já sabemos que está oculto porque fechamos todos)
                    if (detailsRow.style.display === 'none') {
                        detailsRow.style.display = 'table-row';
                        
                        // Garantir que a primeira aba esteja ativa por padrão
                        const firstTablink = detailsRow.querySelector('.tablink');
                        let firstTabId = null;
                        
                        // Extrair o ID da aba do atributo onclick de forma mais robusta
                        if (firstTablink) {
                            const onclickAttr = firstTablink.getAttribute('onclick');
                            if (onclickAttr) {
                                // Tentar diferentes padrões possíveis
                                const match1 = onclickAttr.match(/openTab\(event,\s*['"]([^'"]+)['"]\)/);
                                const match2 = onclickAttr.match(/openTab\(this,\s*['"]([^'"]+)['"]\)/);
                                const match3 = onclickAttr.match(/openTab\([^,]*,\s*['"]([^'"]+)['"]\)/);
                                
                                if (match1 && match1[1]) firstTabId = match1[1];
                                else if (match2 && match2[1]) firstTabId = match2[1];
                                else if (match3 && match3[1]) firstTabId = match3[1];
                            }
                        }
                        
                        if (firstTabId) {
                            // Resetar todas as abas
                            const tabcontents = detailsRow.querySelectorAll('.tabcontent');
                            tabcontents.forEach(tab => tab.style.display = 'none');
                            
                            const tablinks = detailsRow.querySelectorAll('.tablink');
                            tablinks.forEach(link => link.classList.remove('active'));
                            
                            // Ativar a primeira aba
                            const firstTab = document.getElementById(firstTabId);
                            if (firstTab) {
                                firstTab.style.display = 'block';
                            }
                            
                            if (firstTablink) {
                                firstTablink.classList.add('active');
                            }
                        }
                    } else {
                        // Caso extremamente raro, se por algum motivo ainda estiver visível, ocultar
                        detailsRow.style.display = 'none';
                    }
                }
                
                // Chamar a função original se existir, para manter outros comportamentos
                if (originalToggleDetails && typeof originalToggleDetails === 'function') {
                    originalToggleDetails.call(this, processId);
                }
            };
            
            window.filterTable = function() {
                // Primeiro, executar a função original para aplicar os filtros na tabela
                if (originalFilterTable) {
                    originalFilterTable();
                }
                
                // Depois, coletar as linhas visíveis para paginação
                const rows = Array.from(document.querySelectorAll('#processesTable tbody tr.process-row'));
                
                // Fechar todos os detalhes antes de filtrar
                rows.forEach(row => {
                    const rowId = row.getAttribute('data-id');
                    if (rowId) {
                        const detailsRow = document.getElementById('details-' + rowId);
                        if (detailsRow) {
                            detailsRow.style.display = 'none';
                        }
                    }
                });
                
                // Filtrar apenas as linhas que estão visíveis após o filtro ser aplicado
                filteredRows = rows.filter(row => row.style.display !== 'none');
                
                // Esconder todas as linhas (paginação vai mostrar as relevantes)
                rows.forEach(row => {
                    row.style.display = 'none';
                });
                
                // Resetar para a primeira página e atualizar a paginação
                currentPage = 1;
                updatePagination();
                showPage(currentPage);
            };
            
            // Inicializar a paginação aplicando o filtro atual
            filterTable();
        }
        
        // Atualizar controles de paginação
        function updatePagination() {
            const totalPages = Math.ceil(filteredRows.length / ROWS_PER_PAGE);
            const paginationContainer = document.getElementById('pagination-container');
            paginationContainer.innerHTML = '';
            
            // Se tiver apenas uma página, não mostrar paginação
            if (totalPages <= 1) {
                return;
            }
            
            // Criar container de paginação
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
            
            // Botões de página
            const maxButtons = Math.min(7, totalPages);
            let startPage = Math.max(1, Math.min(
                currentPage - Math.floor(maxButtons / 2),
                totalPages - maxButtons + 1
            ));
            let endPage = Math.min(totalPages, startPage + maxButtons - 1);
            
            // Primeiro botão (se não estiver no range)
            if (startPage > 1) {
                const firstPageBtn = document.createElement('button');
                firstPageBtn.className = 'pagination-button';
                firstPageBtn.innerText = '1';
                firstPageBtn.addEventListener('click', () => showPage(1));
                pagination.appendChild(firstPageBtn);
                
                // Adicionar elipses se houver gap
                if (startPage > 2) {
                    const ellipsis = document.createElement('span');
                    ellipsis.className = 'pagination-ellipsis';
                    ellipsis.innerText = '...';
                    pagination.appendChild(ellipsis);
                }
            }
            
            // Botões de página numerados
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
                // Adicionar elipses se houver gap
                if (endPage < totalPages - 1) {
                    const ellipsis = document.createElement('span');
                    ellipsis.className = 'pagination-ellipsis';
                    ellipsis.innerText = '...';
                    pagination.appendChild(ellipsis);
                }
                
                const lastPageBtn = document.createElement('button');
                lastPageBtn.className = 'pagination-button';
                lastPageBtn.innerText = totalPages.toString();
                lastPageBtn.addEventListener('click', () => showPage(totalPages));
                pagination.appendChild(lastPageBtn);
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
            
            // Informação sobre a página atual
            const pageInfo = document.createElement('div');
            pageInfo.className = 'pagination-info';
            pageInfo.id = 'pagination-info';
            pageInfo.innerText = `Página ${currentPage} de ${totalPages}`;
            pagination.appendChild(pageInfo);
            
            paginationContainer.appendChild(pagination);
        }
        
        // Mostrar uma página específica
        function showPage(page) {
            console.log("Mostrando página", page);
            currentPage = page;
            
            // Calcular índices
            const startIdx = (page - 1) * ROWS_PER_PAGE;
            const endIdx = Math.min(startIdx + ROWS_PER_PAGE, filteredRows.length);
            
            // Variável para armazenar o ID do processo com detalhes atualmente abertos (se houver)
            let currentlyOpenDetailId = null;
            
            // Verificar se há algum detalhe aberto atualmente
            document.querySelectorAll('#processesTable tbody tr.details-row').forEach(detailsRow => {
                if (detailsRow.style.display !== 'none') {
                    currentlyOpenDetailId = detailsRow.id.replace('details-', '');
                }
            });
            
            // Ocultar todas as linhas principais e de detalhes primeiro
            document.querySelectorAll('#processesTable tbody tr').forEach(row => {
                row.style.display = 'none';
            });
            
            // Mostrar apenas as linhas principais da página atual
            for (let i = startIdx; i < endIdx; i++) {
                const row = filteredRows[i];
                row.style.display = '';
                
                // Obter o ID do processo desta linha
                const processId = row.getAttribute('data-id');
                if (processId) {
                    // Verificar se existe linha de detalhes
                    const detailsRow = document.getElementById('details-' + processId);
                    if (detailsRow) {
                        // Se este for o processo com detalhes abertos e ele está na página atual,
                        // mantê-lo aberto. Isso assegura que apenas 1 esteja aberto por vez.
                        if (processId === currentlyOpenDetailId) {
                            detailsRow.style.display = 'table-row';
                        }
                    }
                }
            }
            
            // Atualizar botões de paginação
            document.querySelectorAll('.pagination-button').forEach(button => {
                button.classList.remove('active');
                if (button.innerText === page.toString()) {
                    button.classList.add('active');
                }
            });
            
            // Atualizar info da página
            const pageInfo = document.getElementById('pagination-info');
            if (pageInfo) {
                const totalPages = Math.ceil(filteredRows.length / ROWS_PER_PAGE);
                pageInfo.innerText = `Página ${page} de ${totalPages}`;
            }
        }
    </script>
    """
    
    # Adicionar script de paginação antes do fechamento do body
    html_content = html_content.replace('</body>', pagination_script + '\n</body>')
    
    # Sobrescrever o arquivo original com o conteúdo modificado
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(html_content)
        
    return filepath, filename