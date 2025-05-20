// Inicializar os eventos após a página carregar completamente
document.addEventListener('DOMContentLoaded', function() {
    // Configurar os filtros
    document.getElementById('filterInput').addEventListener('keyup', filterTable);
    document.getElementById('processTypeFilter').addEventListener('change', filterTable);
    document.getElementById('statusFilter').addEventListener('change', filterTable);
    
    // Inicializar contadores de status
    initializeStatusFilters();
    
    // Inicializar ordenação da tabela
    initializeSorting();
    
    // Ajustar para dispositivos móveis
    adjustTableForMobile();
    window.addEventListener('resize', adjustTableForMobile);
});

// Inicializar os filtros e contadores de status
function initializeStatusFilters() {
    const table = document.getElementById('processesTable');
    const rows = table.getElementsByClassName('process-row');
    const statusSelect = document.getElementById('statusFilter');
    const statusCountsContainer = document.getElementById('statusCounts');
    
    // Mapas para armazenar status e suas cores
    const statusMap = new Map();
    const statusColors = new Map();
    
    // Coletar todos os status e suas contagens
    for (let i = 0; i < rows.length; i++) {
        const row = rows[i];
        const statusCell = row.cells[1]; // Coluna de status
        const statusBadge = statusCell.querySelector('.status-badge');
        
        if (statusBadge) {
            const status = statusBadge.textContent.trim();
            const statusColor = statusBadge.style.backgroundColor;
            
            if (!statusMap.has(status)) {
                statusMap.set(status, 1);
                statusColors.set(status, statusColor);
                
                // Adicionar ao dropdown de status
                const option = document.createElement('option');
                option.value = status;
                option.textContent = status;
                statusSelect.appendChild(option);
            } else {
                statusMap.set(status, statusMap.get(status) + 1);
            }
        }
    }
    
    // Criar os contadores de status
    statusCountsContainer.innerHTML = '';
    statusMap.forEach((count, status) => {
        const statusColor = statusColors.get(status);
        const statusItem = document.createElement('div');
        statusItem.className = 'status-count-item';
        statusItem.style.backgroundColor = statusColor;
        statusItem.innerHTML = `${status} <span class="status-count-badge">${count}</span>`;
        
        // Adicionar evento de clique para filtrar
        statusItem.addEventListener('click', function() {
            // Remover seleção de todos os itens de status
            document.querySelectorAll('.status-count-item').forEach(item => {
                item.classList.remove('selected');
            });
            
            // Adicionar classe de seleção ao item atual
            this.classList.add('selected');
            
            statusSelect.value = status;
            filterTable();
        });
        
        statusCountsContainer.appendChild(statusItem);
    });
    
    // Realizar filtragem inicial
    filterTable();
}

// Filtrar a tabela com base nos critérios selecionados
function filterTable() {
    const filterValue = document.getElementById('filterInput').value.toLowerCase();
    const typeFilter = document.getElementById('processTypeFilter').value;
    const statusFilter = document.getElementById('statusFilter').value;
    const table = document.getElementById('processesTable');
    const rows = table.getElementsByClassName('process-row');
    const visibleStatusMap = new Map();
    
    // Atualizar o estado visual dos contadores de status
    document.querySelectorAll('.status-count-item').forEach(item => {
        const itemStatus = item.textContent.split(' ')[0];
        if (statusFilter === 'all' || statusFilter === '') {
            // Se "Todos" selecionado, remove destaque de todos
            item.classList.remove('selected');
        } else if (itemStatus === statusFilter) {
            // Destacar o status selecionado
            item.classList.add('selected');
        } else {
            // Remover destaque dos outros status
            item.classList.remove('selected');
        }
    });
    
    for (let i = 0; i < rows.length; i++) {
        const row = rows[i];
        const cells = row.getElementsByTagName('td');
        const processId = row.getAttribute('data-id');
        const processType = row.getAttribute('data-type') || '';
        const detailsRow = document.getElementById('details-' + processId);
        
        // Verificar correspondência de texto
        let matchesText = false;
        for (let j = 0; j < cells.length; j++) {
            if (cells[j].textContent.toLowerCase().includes(filterValue)) {
                matchesText = true;
                break;
            }
        }
        
        // Verificar correspondência de tipo
        let matchesType = true;
        if (typeFilter !== 'todos') {
            matchesType = (processType === typeFilter) || 
                        (typeFilter === 'importacao' && processType === '');
        }
        
        // Verificar correspondência de status
        let matchesStatus = true;
        if (statusFilter !== 'todos') {
            const statusCell = cells[1]; // Coluna de status
            const statusBadge = statusCell.querySelector('.status-badge');
            if (statusBadge) {
                const status = statusBadge.textContent.trim();
                matchesStatus = (status === statusFilter);
            }
        }
        
        // Aplicar filtros
        const visible = matchesText && matchesType && matchesStatus;
        row.style.display = visible ? '' : 'none';
        
        // Gerenciar linha de detalhes correspondente
        if (detailsRow) {
            detailsRow.style.display = (visible && row.classList.contains('active')) ? 'table-row' : 'none';
        }
        
        // Contabilizar status visíveis
        if (visible) {
            const statusCell = cells[1];
            const statusBadge = statusCell.querySelector('.status-badge');
            if (statusBadge) {
                const status = statusBadge.textContent.trim();
                visibleStatusMap.set(status, (visibleStatusMap.get(status) || 0) + 1);
            }
        }
    }
    
    // Atualizar contadores de status
    updateStatusCounters(visibleStatusMap, statusFilter);
}

// Atualizar os contadores de status após filtrar
function updateStatusCounters(visibleStatusMap, selectedStatus) {
    const statusItems = document.querySelectorAll('.status-count-item');
    statusItems.forEach(item => {
        const status = item.textContent.split(' ')[0]; // Nome do status (antes do contador)
        const countBadge = item.querySelector('.status-count-badge');
        const count = visibleStatusMap.get(status) || 0;
        
        // Atualizar número
        countBadge.textContent = count;
        
        // Destacar o status selecionado
        item.style.border = (status === selectedStatus) ? '2px solid #333' : 'none';
    });
}

// Configurar a ordenação da tabela
function initializeSorting() {
    document.querySelectorAll('#processesTable th').forEach((header, index) => {
        header.addEventListener('click', () => sortTable(index));
    });
}

// Ordenar a tabela pela coluna especificada
function sortTable(columnIndex) {
    const table = document.getElementById('processesTable');
    const tbody = table.querySelector('tbody');
    const rows = Array.from(table.querySelectorAll('.process-row'));
    const detailsRowsMap = {};
    
    // Guardar mapeamento dos detalhes
    rows.forEach(row => {
        const processId = row.getAttribute('data-id');
        const detailsRow = document.getElementById('details-' + processId);
        if (detailsRow) {
            detailsRowsMap[processId] = detailsRow;
        }
    });
    
    // Ordenar as linhas
    rows.sort((rowA, rowB) => {
        const cellA = rowA.cells[columnIndex];
        const cellB = rowB.cells[columnIndex];
        
        let valueA = cellA.textContent.trim();
        let valueB = cellB.textContent.trim();
        
        // Verificar se são datas no formato DD/MM/YYYY
        if (/^\d{2}\/\d{2}\/\d{4}$/.test(valueA) && /^\d{2}\/\d{2}\/\d{4}$/.test(valueB)) {
            const [dayA, monthA, yearA] = valueA.split('/');
            const [dayB, monthB, yearB] = valueB.split('/');
            
            const dateA = new Date(`${yearA}-${monthA}-${dayA}`);
            const dateB = new Date(`${yearB}-${monthB}-${dayB}`);
            
            return dateA - dateB;
        }
        
        // Ordenação padrão (texto)
        return valueA.localeCompare(valueB);
    });
    
    // Reconstruir a tabela com as linhas ordenadas
    tbody.innerHTML = '';
    rows.forEach(row => {
        const processId = row.getAttribute('data-id');
        tbody.appendChild(row);
        
        const detailsRow = detailsRowsMap[processId];
        if (detailsRow) {
            tbody.appendChild(detailsRow);
        }
    });
}

// Expandir/colapsar detalhes de um processo
function toggleDetails(processId) {
    const row = document.querySelector(`tr[data-id="${processId}"]`);
    const detailsRow = document.getElementById('details-' + processId);
    
    if (!detailsRow) return;
    
    if (detailsRow.style.display === 'table-row') {
        // Ocultar detalhes
        detailsRow.style.display = 'none';
        row.classList.remove('active');
    } else {
        // Mostrar detalhes
        detailsRow.style.display = 'table-row';
        row.classList.add('active');
        
        // Garantir que a primeira aba esteja ativa
        const firstTab = detailsRow.querySelector('.tab');
        const firstTabContent = detailsRow.querySelector('.tabcontent');
        
        if (firstTab && firstTabContent) {
            const tabs = detailsRow.querySelectorAll('.tab');
            const tabContents = detailsRow.querySelectorAll('.tabcontent');
            
            // Resetar todas as abas
            tabs.forEach(tab => tab.classList.remove('active'));
            tabContents.forEach(content => content.style.display = 'none');
            
            // Ativar a primeira aba
            firstTab.classList.add('active');
            firstTabContent.style.display = 'block';
        }
    }
}

// Alternar entre abas nos detalhes do processo
function openTab(evt, tabId) {
    const processId = tabId.split('-')[0];
    const detailsRow = document.getElementById('details-' + processId);
    
    if (!detailsRow) return;
    
    // Esconder todos os conteúdos
    const contents = detailsRow.querySelectorAll('.tabcontent');
    contents.forEach(content => {
        content.style.display = 'none';
    });
    
    // Desativar todas as abas
    const tabs = detailsRow.querySelectorAll('.tab');
    tabs.forEach(tab => {
        tab.classList.remove('active');
    });
    
    // Ativar a aba selecionada
    document.getElementById(tabId).style.display = 'block';
    evt.currentTarget.classList.add('active');
}

// Ajustar a visualização para dispositivos móveis
function adjustTableForMobile() {
    const width = window.innerWidth;
    const table = document.getElementById('processesTable');
    
    if (!table) return;
    
    const rows = table.querySelectorAll('tr');
    
    if (width < 768) {
        // Em dispositivos móveis, mostrar apenas as 5 primeiras colunas
        rows.forEach(row => {
            if (row.classList.contains('process-row')) {
                const cells = row.cells;
                for (let i = 0; i < cells.length; i++) {
                    cells[i].style.display = (i < 5) ? '' : 'none';
                }
            }
        });
        
        // Ajustar cabeçalhos da tabela
        const headerRow = table.querySelector('thead tr');
        if (headerRow) {
            const headerCells = headerRow.cells;
            for (let i = 0; i < headerCells.length; i++) {
                headerCells[i].style.display = (i < 5) ? '' : 'none';
            }
        }
    } else {
        // Em desktop, mostrar todas as colunas
        rows.forEach(row => {
            if (row.tagName === 'TR') {
                const cells = row.cells;
                for (let i = 0; i < cells.length; i++) {
                    cells[i].style.display = '';
                }
            }
        });
    }
}