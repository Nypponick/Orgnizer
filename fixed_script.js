document.addEventListener('DOMContentLoaded', function() {
    // Adicionar event listeners para os filtros
    document.getElementById('filterInput').addEventListener('keyup', filterTable);
    document.getElementById('processTypeFilter').addEventListener('change', filterTable);
    document.getElementById('statusFilter').addEventListener('change', filterTable);
    
    // Inicializar os filtros de status e contadores
    initStatusFilters();
    
    // Inicializar responsividade
    adjustTableForMobile();
    window.addEventListener('resize', adjustTableForMobile);
});

// Inicializar os filtros de status e contadores
function initStatusFilters() {
    const table = document.getElementById('processesTable');
    if (!table) return;
    
    const rows = table.getElementsByClassName('process-row');
    const statusSelect = document.getElementById('statusFilter');
    const statusContainer = document.getElementById('statusCounts');
    
    // Mapas para armazenar status e suas cores
    const statusMap = {};
    const statusColors = {};
    
    // Coletar todos os status existentes na tabela
    for (let i = 0; i < rows.length; i++) {
        const row = rows[i];
        const statusCell = row.cells[1]; // Coluna de status
        if (!statusCell) continue;
        
        const statusBadge = statusCell.querySelector('.status-badge');
        if (!statusBadge) continue;
        
        const status = statusBadge.textContent.trim();
        const color = statusBadge.style.backgroundColor;
        
        if (!statusMap[status]) {
            statusMap[status] = 1;
            statusColors[status] = color;
            
            // Adicionar ao dropdown
            const option = document.createElement('option');
            option.value = status;
            option.textContent = status;
            statusSelect.appendChild(option);
        } else {
            statusMap[status]++;
        }
    }
    
    // Criar os contadores visuais
    statusContainer.innerHTML = '';
    
    for (const status in statusMap) {
        const count = statusMap[status];
        const color = statusColors[status];
        
        const item = document.createElement('div');
        item.className = 'status-count-item';
        item.style.backgroundColor = color;
        item.innerHTML = `${status} <span class="status-count-badge">${count}</span>`;
        
        // Adicionar evento de clique para filtrar
        item.addEventListener('click', function() {
            // Remover a classe 'selected' de todos os items
            document.querySelectorAll('.status-count-item').forEach(i => {
                i.classList.remove('selected');
            });
            
            // Se estamos selecionando um filtro diferente de vazio, adicione a classe 'selected'
            if (status !== '') {
                this.classList.add('selected');
            }
            
            statusSelect.value = status;
            filterTable();
        });
        
        statusContainer.appendChild(item);
    }
    
    // Filtrar inicialmente
    filterTable();
}

// Função de filtragem da tabela
function filterTable() {
    const filterValue = document.getElementById('filterInput').value.toLowerCase();
    const typeFilter = document.getElementById('processTypeFilter').value;
    const statusFilter = document.getElementById('statusFilter').value;
    
    const table = document.getElementById('processesTable');
    if (!table) return;
    
    const rows = table.getElementsByClassName('process-row');
    const visibleStatusCounts = {};
    
    // Inicializar contadores com zero
    const statusItems = document.querySelectorAll('.status-count-item');
    statusItems.forEach(item => {
        const status = item.textContent.split(' ')[0];
        visibleStatusCounts[status] = 0;
    });
    
    // Aplicar filtros a cada linha
    for (let i = 0; i < rows.length; i++) {
        const row = rows[i];
        const cells = row.cells;
        const processId = row.getAttribute('data-id');
        const processType = row.getAttribute('data-type') || '';
        
        // Verificar filtro de texto
        let matchesText = false;
        for (let j = 0; j < cells.length; j++) {
            const cellText = cells[j].textContent.toLowerCase();
            if (cellText.includes(filterValue)) {
                matchesText = true;
                break;
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
            const statusCell = cells[1];
            const statusText = statusCell.textContent.trim();
            matchesStatus = statusText.includes(statusFilter);
        }
        
        // Aplicar visibilidade
        const isVisible = matchesText && matchesType && matchesStatus;
        row.style.display = isVisible ? '' : 'none';
        
        // Fechar detalhes se a linha for ocultada
        const detailsRow = document.getElementById('details-' + processId);
        if (detailsRow) {
            detailsRow.style.display = 'none';
            row.classList.remove('active');
        }
        
        // Atualizar contadores de status visíveis
        if (isVisible) {
            const statusCell = cells[1];
            const statusBadge = statusCell.querySelector('.status-badge');
            if (statusBadge) {
                const status = statusBadge.textContent.trim();
                visibleStatusCounts[status] = (visibleStatusCounts[status] || 0) + 1;
            }
        }
    }
    
    // Atualizar os contadores visuais
    statusItems.forEach(item => {
        const status = item.textContent.split(' ')[0];
        const badge = item.querySelector('.status-count-badge');
        if (badge) {
            badge.textContent = visibleStatusCounts[status] || 0;
        }
        
        // Destacar o status selecionado
        if (status === statusFilter) {
            item.style.border = '2px solid #333';
        } else {
            item.style.border = 'none';
        }
    });
}

// Função para expandir/colapsar detalhes
function toggleDetails(processId) {
    const row = document.querySelector(`tr[data-id="${processId}"]`);
    const detailsRow = document.getElementById('details-' + processId);
    
    if (!detailsRow) {
        console.error('Details row not found for process:', processId);
        return;
    }
    
    // Verificar estado atual
    const isVisible = detailsRow.style.display === 'table-row';
    
    // Fechar detalhes se estiver aberto
    if (isVisible) {
        detailsRow.style.display = 'none';
        row.classList.remove('active');
    } else {
        // Abrir detalhes
        detailsRow.style.display = 'table-row';
        row.classList.add('active');
        
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

// Função para alternar entre abas
function openTab(evt, tabId) {
    // Extrair o ID do processo a partir do ID da aba
    const processId = tabId.split('-')[0];
    const detailsRow = document.getElementById('details-' + processId);
    
    if (!detailsRow) return;
    
    // Ocultar todos os conteúdos
    const tabContents = detailsRow.querySelectorAll('.tabcontent');
    tabContents.forEach(content => content.style.display = 'none');
    
    // Remover 'active' de todas as abas
    const tabs = detailsRow.querySelectorAll('.tab');
    tabs.forEach(tab => tab.classList.remove('active'));
    
    // Mostrar o conteúdo selecionado
    const selectedContent = document.getElementById(tabId);
    if (selectedContent) {
        selectedContent.style.display = 'block';
    }
    
    // Marcar a aba como ativa
    evt.currentTarget.classList.add('active');
}

// Ajustar a tabela para dispositivos móveis
function adjustTableForMobile() {
    const width = window.innerWidth;
    const table = document.getElementById('processesTable');
    
    if (!table) return;
    
    const headerRow = table.querySelector('thead tr');
    const dataRows = table.querySelectorAll('.process-row');
    
    if (width < 768) {
        // Em dispositivos móveis, mostrar apenas as primeiras 5 colunas
        if (headerRow) {
            const headerCells = headerRow.cells;
            for (let i = 0; i < headerCells.length; i++) {
                headerCells[i].style.display = (i < 5) ? '' : 'none';
            }
        }
        
        // Ajustar células de dados
        dataRows.forEach(row => {
            const cells = row.cells;
            for (let i = 0; i < cells.length; i++) {
                cells[i].style.display = (i < 5) ? '' : 'none';
            }
        });
    } else {
        // Em desktop, mostrar todas as colunas
        if (headerRow) {
            const headerCells = headerRow.cells;
            for (let i = 0; i < headerCells.length; i++) {
                headerCells[i].style.display = '';
            }
        }
        
        // Mostrar todas as células de dados
        dataRows.forEach(row => {
            const cells = row.cells;
            for (let i = 0; i < cells.length; i++) {
                cells[i].style.display = '';
            }
        });
    }
}