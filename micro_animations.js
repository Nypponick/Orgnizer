/**
 * Micro-Interaction Feedback Animations
 * Este script adiciona pequenas animações interativas para melhorar a experiência do usuário
 * nos relatórios HTML exportados do sistema JGR Broker.
 */

document.addEventListener('DOMContentLoaded', function() {
    // Inicializar todas as animações
    initButtonAnimations();
    initStatusBadgeAnimations();
    initTableRowAnimations();
    initFilterAnimations();
    initExpandCollapseAnimations();
});

/**
 * Adiciona animações aos botões
 */
function initButtonAnimations() {
    const buttons = document.querySelectorAll('.tabs button, .pagination-button, .close-details');
    
    buttons.forEach(button => {
        // Efeito de pulsação ao clicar
        button.addEventListener('click', function(e) {
            const button = e.currentTarget;
            button.classList.add('pulse-animation');
            setTimeout(() => {
                button.classList.remove('pulse-animation');
            }, 300);
        });
        
        // Efeito de hover com transformação suave
        button.addEventListener('mouseenter', function(e) {
            e.currentTarget.classList.add('hover-transform');
        });
        
        button.addEventListener('mouseleave', function(e) {
            e.currentTarget.classList.remove('hover-transform');
        });
    });
}

/**
 * Adiciona animações aos status badges
 */
function initStatusBadgeAnimations() {
    const statusBadges = document.querySelectorAll('.status-badge, .status-count-item');
    
    statusBadges.forEach(badge => {
        // Efeito de pulsação ao clicar
        badge.addEventListener('click', function(e) {
            const badge = e.currentTarget;
            badge.classList.add('pulse-animation');
            setTimeout(() => {
                badge.classList.remove('pulse-animation');
            }, 300);
        });
        
        // Efeito de hover com elevação
        badge.addEventListener('mouseenter', function(e) {
            e.currentTarget.classList.add('hover-lift');
        });
        
        badge.addEventListener('mouseleave', function(e) {
            e.currentTarget.classList.remove('hover-lift');
        });
    });
}

/**
 * Adiciona animações às linhas da tabela
 */
function initTableRowAnimations() {
    const tableRows = document.querySelectorAll('table tr:not(.details-row)');
    
    tableRows.forEach(row => {
        // Efeito de destaque ao clicar
        row.addEventListener('click', function(e) {
            if (e.target.tagName.toLowerCase() !== 'button' && 
                e.target.tagName.toLowerCase() !== 'a' && 
                !e.target.classList.contains('close-details')) {
                const row = e.currentTarget;
                row.classList.add('row-highlight-animation');
                setTimeout(() => {
                    row.classList.remove('row-highlight-animation');
                }, 300);
            }
        });
    });
}

/**
 * Adiciona animações aos elementos de filtro
 */
function initFilterAnimations() {
    const filterInput = document.getElementById('filterInput');
    
    if (filterInput) {
        // Efeito de transição quando o input recebe foco
        filterInput.addEventListener('focus', function(e) {
            e.currentTarget.classList.add('input-focus-animation');
        });
        
        filterInput.addEventListener('blur', function(e) {
            e.currentTarget.classList.remove('input-focus-animation');
        });
        
        // Efeito de digitação
        filterInput.addEventListener('input', function(e) {
            const input = e.currentTarget;
            input.classList.add('input-typing-animation');
            setTimeout(() => {
                input.classList.remove('input-typing-animation');
            }, 300);
        });
    }
}

/**
 * Adiciona animações para expansão/colapso de detalhes
 */
function initExpandCollapseAnimations() {
    // Função para encontrar a linha de detalhes associada a uma linha
    function findDetailsRow(processId) {
        return document.getElementById(`details-${processId}`);
    }
    
    // Adicionar animação ao expandir/colapsar detalhes
    document.addEventListener('click', function(e) {
        if (e.target.matches('.expand-btn') || e.target.parentElement.matches('.expand-btn')) {
            const btn = e.target.matches('.expand-btn') ? e.target : e.target.parentElement;
            const processId = btn.getAttribute('data-id');
            const detailsRow = findDetailsRow(processId);
            
            if (detailsRow) {
                if (detailsRow.style.display === 'none' || detailsRow.style.display === '') {
                    // Expandindo
                    detailsRow.style.display = 'table-row';
                    detailsRow.classList.add('expand-animation');
                    setTimeout(() => {
                        detailsRow.classList.remove('expand-animation');
                    }, 300);
                } else {
                    // Colapsando
                    detailsRow.classList.add('collapse-animation');
                    setTimeout(() => {
                        detailsRow.style.display = 'none';
                        detailsRow.classList.remove('collapse-animation');
                    }, 300);
                }
            }
        }
    });
}