// Função para tornar as colunas da tabela redimensionáveis (como no Excel)
document.addEventListener('DOMContentLoaded', function() {
    // Inicializar colunas redimensionáveis
    initResizableColumns();
});

// Inicializar as colunas redimensionáveis
function initResizableColumns() {
    const table = document.getElementById('processesTable');
    if (!table) return;

    const headers = table.querySelectorAll('th');
    
    headers.forEach(header => {
        // Adicionar a alça de redimensionamento
        const resizeHandle = document.createElement('div');
        resizeHandle.className = 'resize-handle';
        resizeHandle.style.position = 'absolute';
        resizeHandle.style.top = '0';
        resizeHandle.style.right = '0';
        resizeHandle.style.bottom = '0';
        resizeHandle.style.width = '5px';
        resizeHandle.style.cursor = 'col-resize';
        resizeHandle.style.userSelect = 'none';
        
        // Adicionar hover effect
        resizeHandle.addEventListener('mouseover', function() {
            resizeHandle.style.backgroundColor = 'rgba(0,0,0,0.1)';
        });
        
        resizeHandle.addEventListener('mouseout', function() {
            resizeHandle.style.backgroundColor = 'transparent';
        });
        
        // Configurar posição relativa para o cabeçalho
        header.style.position = 'relative';
        header.style.overflow = 'visible'; // Garantir que a alça não fique cortada
        
        // Adicionar a alça de redimensionamento ao cabeçalho
        header.appendChild(resizeHandle);
        
        // Adicionar os eventos de redimensionamento
        let startX, startWidth;
        
        resizeHandle.addEventListener('mousedown', function(e) {
            // Impedir que o evento de clique se propague para o cabeçalho (evitar ordenação)
            e.stopPropagation();
            
            startX = e.pageX;
            startWidth = header.offsetWidth;
            
            // Adicionar evento para redimensionar enquanto arrasta
            document.addEventListener('mousemove', resize);
            document.addEventListener('mouseup', stopResize);
            
            // Adicionar indicador visual durante o redimensionamento
            document.body.style.cursor = 'col-resize';
            header.classList.add('resizing');
            
            // Destacar visualmente a coluna sendo redimensionada
            const index = Array.from(headers).indexOf(header);
            const cells = table.querySelectorAll(`tbody tr td:nth-child(${index + 1})`);
            cells.forEach(cell => cell.classList.add('column-highlight'));
        });
        
        // Função para redimensionar enquanto o mouse se move
        function resize(e) {
            const width = startWidth + (e.pageX - startX);
            
            // Limitar largura mínima
            if (width >= 50) {
                header.style.width = `${width}px`;
                header.style.minWidth = `${width}px`;
                
                // Ajustar todas as células correspondentes na mesma coluna
                const index = Array.from(headers).indexOf(header);
                const cells = table.querySelectorAll(`tbody tr td:nth-child(${index + 1})`);
                cells.forEach(cell => {
                    cell.style.width = `${width}px`;
                    cell.style.minWidth = `${width}px`;
                });
            }
        }
        
        // Função para parar o redimensionamento
        function stopResize() {
            document.removeEventListener('mousemove', resize);
            document.removeEventListener('mouseup', stopResize);
            
            // Restaurar cursor
            document.body.style.cursor = '';
            header.classList.remove('resizing');
            
            // Remover destaque das células
            table.querySelectorAll('.column-highlight').forEach(cell => {
                cell.classList.remove('column-highlight');
            });
        }
    });
}

// Disponibilizar função no escopo global
window.initResizableColumns = initResizableColumns;