// Configuração de paginação
const ROWS_PER_PAGE = 10;
let currentPage = 1;
let totalPages = 1;
let tableRows = [];

// Inicializar paginação
function initPagination() {
    // Obter todas as linhas da tabela
    const table = document.getElementById('processesTable');
    if (!table) return;
    
    const tbody = table.querySelector('tbody');
    if (!tbody) return;
    
    // Obter todas as linhas de processo (não as linhas de detalhes)
    tableRows = Array.from(tbody.querySelectorAll('tr.process-row'));
    
    // Calcular número total de páginas
    totalPages = Math.ceil(tableRows.length / ROWS_PER_PAGE);
    
    // Criar a navegação de paginação
    createPaginationControls();
    
    // Mostrar a primeira página
    showPage(1);
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
    const endIdx = Math.min(startIdx + ROWS_PER_PAGE, tableRows.length);
    
    // Esconder todas as linhas
    tableRows.forEach(row => {
        row.style.display = 'none';
        
        // Esconder também detalhes expandidos
        const processId = row.getAttribute('data-id');
        if (processId) {
            const detailsRow = document.getElementById(`details-${processId}`);
            if (detailsRow) {
                detailsRow.style.display = 'none';
            }
        }
    });
    
    // Mostrar apenas as linhas da página atual
    for (let i = startIdx; i < endIdx; i++) {
        if (tableRows[i]) {
            tableRows[i].style.display = '';
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

// Inicializar paginação quando a página carregar
document.addEventListener('DOMContentLoaded', () => {
    setTimeout(initPagination, 500); // Pequeno delay para garantir que a tabela já está carregada
});