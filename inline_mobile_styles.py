"""
Módulo para definir estilos CSS responsivos para dispositivos móveis
que serão incluídos diretamente nos relatórios HTML
"""

def get_mobile_styles():
    """Retorna estilos CSS responsivos para dispositivos móveis"""
    return """
/* Estilos para dispositivos móveis */
@media only screen and (max-width: 767px) {
    * {
        max-width: 100% !important;
        box-sizing: border-box !important;
    }
    
    body {
        padding: 5px !important;
        margin: 0 !important;
        font-size: 14px !important;
        width: 100% !important;
        overflow-x: hidden !important;
    }
    
    .container {
        padding: 8px !important;
        margin: 0 !important;
        width: 100% !important;
        box-shadow: none !important;
        overflow-x: hidden !important;
    }
    
    .logo-container {
        text-align: center !important;
        margin-bottom: 10px !important;
    }
    
    .jgr-logo {
        max-width: 150px !important;
        height: auto !important;
    }
    
    h1 {
        font-size: 18px !important;
        margin: 5px 0 !important;
        padding-bottom: 5px !important;
        text-align: center !important;
    }
    
    .header {
        margin-bottom: 10px !important;
        padding-bottom: 5px !important;
    }
    
    .header > div {
        display: block !important;
        width: 100% !important;
    }
    
    .header > div > div {
        width: 100% !important;
        margin-bottom: 8px !important;
        text-align: center !important;
        display: block !important;
    }
    
    table {
        display: block !important;
        width: 100% !important;
        font-size: 11px !important;
        border: none !important;
        overflow-x: auto !important;
    }
    
    table th, table td {
        padding: 4px !important;
        font-size: 11px !important;
        white-space: nowrap !important;
    }
    
    .filter-container {
        display: block !important;
        padding: 5px !important;
        margin-bottom: 10px !important;
    }
    
    .filter-input {
        width: 100% !important;
        margin: 5px 0 !important;
        padding: 5px !important;
    }
    
    .status-filter {
        display: flex !important;
        flex-wrap: wrap !important;
        justify-content: center !important;
        margin-top: 5px !important;
    }
    
    .status-badge, .status-count-item {
        margin: 2px !important;
        padding: 3px 5px !important;
        font-size: 10px !important;
    }
    
    .pagination {
        display: flex !important;
        flex-wrap: wrap !important;
        justify-content: center !important;
        margin: 10px 0 !important;
    }
    
    .pagination-button {
        margin: 2px !important;
        padding: 4px 6px !important;
        font-size: 11px !important;
        min-width: 25px !important;
    }
    
    .tabs {
        display: flex !important;
        flex-wrap: wrap !important;
        justify-content: center !important;
    }
    
    .tabs button {
        padding: 5px !important;
        font-size: 11px !important;
        margin: 2px !important;
        flex-grow: 1 !important;
    }
    
    .close-details {
        font-size: 16px !important;
        padding: 2px 6px !important;
        right: 5px !important;
        top: 5px !important;
    }
    
    .detail-section {
        padding: 5px !important;
        margin-bottom: 5px !important;
    }
    
    /* Esconder colunas menos importantes */
    table th:nth-child(4), table td:nth-child(4),
    table th:nth-child(6), table td:nth-child(6),
    table th:nth-child(8), table td:nth-child(8),
    table th:nth-child(10), table td:nth-child(10),
    table th:nth-child(12), table td:nth-child(12) {
        display: none !important;
    }
}
"""