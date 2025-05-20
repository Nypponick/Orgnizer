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

// Função para modificar o comportamento da função filterTable 
function setupPagination() {
    // Verificar se o evento DOMContentLoaded já foi disparado
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initPagination);
    } else {
        // Se o DOM já estiver carregado, inicializar imediatamente
        initPagination();
    }
}

function initPagination() {
    // Obter a função original filterTable
    const originalFilterTable = window.filterTable;
    
    // Sobrescrever com nossa versão que inclui paginação
    window.filterTable = function() {
        console.log("Aplicando filtros com paginação");
        
        // Coletar linhas que seriam visíveis com a função original
        const filterValue = document.getElementById('filterInput')?.value?.toLowerCase() || '';
        const typeFilter = document.getElementById('processTypeFilter')?.value || 'todos';
        const statusFilter = document.getElementById('statusFilter')?.value || 'todos';
        
        const table = document.getElementById('processesTable');
        if (!table) {
            console.error("Tabela não encontrada para paginação");
            return;
        }
        
        // Obter todas as linhas de processos
        const rows = Array.from(table.querySelectorAll('tbody tr.process-row'));
        
        // Redefinir as linhas filtradas para paginação
        filteredRows = [];
        
        // Esconder detalhes expandidos
        document.querySelectorAll('tr[id^="details-"]').forEach(row => {
            row.style.display = 'none';
        });
        
        rows.forEach(row => {
            // Esconder todas as linhas inicialmente
            row.style.display = 'none';
            
            const cells = row.cells;
            const processId = row.getAttribute('data-id');
            const processType = row.getAttribute('data-type') || '';
            
            // Aplicar filtro de texto
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
                const rowStatus = row.getAttribute('data-status');
                matchesStatus = (rowStatus === statusFilter);
            }
            
            // Se a linha passa por todos os filtros, adicioná-la às linhas filtradas
            if (matchesText && matchesType && matchesStatus) {
                filteredRows.push(row);
            }
        });
        
        // Chamar a função original para atualizar contadores, etc.
        if (originalFilterTable) {
            originalFilterTable();
        }
        
        // Atualizar a contagem total no topo
        const processCounter = document.getElementById('process-counter');
        if (processCounter) {
            processCounter.textContent = filteredRows.length;
        }
        
        // Mostrar/ocultar mensagem de nenhum resultado
        const noResults = document.getElementById('no-results-message');
        if (noResults) {
            noResults.style.display = filteredRows.length === 0 ? 'block' : 'none';
        }
        
        // Atualizar paginação e mostrar a primeira página
        currentPage = 1;
        updatePagination();
        showPage(currentPage);
    };
    
    // Executar a função filterTable para inicializar a paginação
    window.filterTable();
}

// Iniciar paginação quando o script for carregado
setupPagination();