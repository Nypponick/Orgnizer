// Função para adicionar a funcionalidade de ocultar/mostrar colunas
document.addEventListener('DOMContentLoaded', function() {
    // Inicializar a funcionalidade de toggle de colunas
    initColumnToggle();
});

// Inicializar os controles para ocultar/mostrar colunas
function initColumnToggle() {
    const table = document.getElementById('processesTable');
    if (!table) return;

    const headerRow = table.querySelector('thead tr');
    if (!headerRow) return;

    // Adicionar ícones de expandir/recolher aos cabeçalhos
    const headers = headerRow.querySelectorAll('th');
    headers.forEach((header, index) => {
        // Não adicionar para a primeira coluna (ID) e a coluna de status
        if (index > 1) {
            // Guardar o texto original do cabeçalho
            const originalText = header.textContent;
            
            // Criar ícone de toggle
            const toggleIcon = document.createElement('span');
            toggleIcon.className = 'column-toggle-icon';
            toggleIcon.innerHTML = '&#8722;'; // Ícone de menos (-)
            toggleIcon.title = 'Clique para ocultar esta coluna';
            toggleIcon.style.marginLeft = '5px';
            toggleIcon.style.cursor = 'pointer';
            toggleIcon.style.fontWeight = 'bold';
            
            // Adicionar evento ao ícone
            toggleIcon.addEventListener('click', function(e) {
                e.stopPropagation(); // Evitar que o clique acione a ordenação
                toggleColumn(index);
                
                // Alternar ícone
                if (this.innerHTML === '&#8722;') {
                    this.innerHTML = '&#43;'; // Ícone de mais (+)
                    this.title = 'Clique para mostrar esta coluna';
                } else {
                    this.innerHTML = '&#8722;'; // Ícone de menos (-)
                    this.title = 'Clique para ocultar esta coluna';
                }
            });
            
            // Limpar conteúdo original e adicionar de volta com o ícone
            header.innerHTML = '';
            
            // Adicionar span para o texto original
            const textSpan = document.createElement('span');
            textSpan.textContent = originalText;
            header.appendChild(textSpan);
            header.appendChild(toggleIcon);
        }
    });
}

// Função para mostrar/ocultar uma coluna específica
function toggleColumn(columnIndex) {
    const table = document.getElementById('processesTable');
    if (!table) return;
    
    // Alternar visibilidade da coluna em todas as linhas
    const rows = table.querySelectorAll('tr');
    rows.forEach(row => {
        // Pular linhas de detalhes (elas não têm células individuais)
        if (row.classList.contains('details-row')) return;
        
        const cells = row.querySelectorAll('th, td');
        if (cells.length > columnIndex) {
            const cell = cells[columnIndex];
            
            // Verificar o estado atual e alterná-lo
            if (cell.style.display === 'none') {
                cell.style.display = '';
            } else {
                cell.style.display = 'none';
            }
        }
    });
}

// Adicionar ao escopo global para uso fora do módulo
window.toggleColumn = toggleColumn;
window.initColumnToggle = initColumnToggle;