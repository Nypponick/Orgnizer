"""
Módulo para processar arquivos HTML após sua geração,
aplicando estilos personalizados e outras modificações
"""

import re
import os

# Carregar estilos de animação
ANIMATION_CSS_PATH = "animation_styles.css"
ANIMATION_CSS = ""
if os.path.exists(ANIMATION_CSS_PATH):
    with open(ANIMATION_CSS_PATH, 'r', encoding='utf-8') as f:
        ANIMATION_CSS = f.read()

def apply_style_changes(html_content):
    """
    Aplica mudanças de estilo no conteúdo HTML
    
    Args:
        html_content: Conteúdo HTML original
    
    Returns:
        str: Conteúdo HTML modificado com os estilos atualizados
    """
    # Verificar se é um relatório de processo individual
    is_individual_process = False
    if "Processo de Importação - " in html_content or "Processo de Exportação - " in html_content:
        is_individual_process = True
        
    # Remover o logo da JGR de relatórios individuais de processos
    if is_individual_process:
        html_content = re.sub(
            r'<div class="logo-container">\s*<img src="data:image/png;base64,[^"]*" alt="JGR Broker Logo" class="jgr-logo">\s*</div>',
            '<!-- Logo JGR removido de relatórios individuais de processos -->',
            html_content
        )
    # Substituir a fonte Arial por Segoe UI
    html_content = re.sub(
        r"font-family:\s*Arial,\s*sans-serif",
        "font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif",
        html_content
    )
    
    # Substituir bordas das tabelas por bordas mais sutis
    html_content = re.sub(
        r"border:\s*1px\s+solid\s+#ddd", 
        "border: none",
        html_content
    )
    
    html_content = re.sub(
        r"border-bottom:\s*1px\s+solid\s+#eee", 
        "border-bottom: 1px solid #f0f0f0",
        html_content
    )
    
    # Adicionar contorno no cabeçalho da tabela (borda inferior mais destacada), centralizar texto
    # e ajustar tamanho e peso da fonte
    html_content = re.sub(
        r"(table th\s*{[^}]*?)(background:\s*#f5f5f5;)",
        r"\1\2 border-bottom: 2px solid #2c3e50; border-right: 1px solid #ddd; text-align: center; font-size: 0.9em; font-weight: 600;",
        html_content
    )
    
    # Adicionar bordas sutis à direita para células de tabela, centralizar texto
    # e aplicar tamanho e estilo de fonte, além de linhas separadoras entre as linhas
    html_content = re.sub(
        r"(table th, table td \{[^\}]*?)text-align: left;(\s*border-bottom:[^;\}]*;)",
        r"\1text-align: center;\2 border-right: 1px solid #f0f0f0; border-bottom: 1px solid #eaeaea; font-size: 0.9em; font-weight: 500;",
        html_content
    )
    
    # Adicionar efeito hover e linhas zebradas nas tabelas para melhor organização visual
    if "table tr:hover" not in html_content:
        html_content = html_content.replace(
            "table td {",
            "table tr:hover {\n"
            "            background-color: rgba(0,0,0,0.03);\n"
            "        }\n"
            "        table tr:nth-child(even) {\n"
            "            background-color: rgba(0,0,0,0.01);\n"
            "        }\n"
            "        table td {"
        )
    
    # Adicionar estilos para destacar os status selecionados
    if "status-count-item.selected" not in html_content:
        html_content = html_content.replace(
            ".status-count-item:hover {",
            ".status-count-item.selected {\n"
            "            border: 2px solid white;\n"
            "            box-shadow: 0 0 0 2px #2c3e50;\n"
            "        }\n"
            "        .status-count-item:hover {"
        )
    
    # Adicionar estilos de animação
    if "pulse-animation" not in html_content and ANIMATION_CSS:
        html_content = html_content.replace(
            "</style>",
            ANIMATION_CSS + "\n</style>"
        )
    
    # Adicionar estilos responsivos para dispositivos móveis
    if "@media only screen and (max-width: 767px)" not in html_content:
        html_content = html_content.replace(
            "</style>",
            """
            /* Estilos responsivos para dispositivos móveis */
            @media only screen and (max-width: 767px) {
                body {
                    padding: 8px !important;
                    margin: 0 !important;
                    font-size: 14px !important;
                }
                
                .container {
                    padding: 10px !important;
                    margin: 0 !important;
                    box-shadow: none !important;
                }
                
                .jgr-logo {
                    max-width: 180px !important;
                }
                
                h1 {
                    font-size: 1.4em !important;
                    margin-bottom: 10px !important;
                    padding-bottom: 8px !important;
                }
                
                .header {
                    margin-bottom: 10px !important;
                }
                
                .header > div {
                    flex-direction: column !important;
                    align-items: flex-start !important;
                    width: 100% !important;
                }
                
                .header > div > div {
                    width: 100% !important;
                    margin-bottom: 10px !important;
                    text-align: center !important;
                }
                
                table {
                    display: block !important;
                    overflow-x: auto !important;
                    white-space: nowrap !important;
                    width: 100% !important;
                    font-size: 0.85em !important;
                    border-collapse: collapse !important;
                }
                
                table th, table td {
                    padding: 6px !important;
                    font-size: 12px !important;
                }
                
                .filter-container {
                    flex-direction: column !important;
                    align-items: flex-start !important;
                    padding: 10px !important;
                }
                
                .filter-input {
                    width: 100% !important;
                    margin-top: 5px !important;
                    box-sizing: border-box !important;
                }
                
                .status-filter {
                    flex-wrap: wrap !important;
                    margin-top: 10px !important;
                    justify-content: flex-start !important;
                }
                
                .status-badge, .status-count-item {
                    margin-bottom: 5px !important;
                    font-size: 0.8em !important;
                    padding: 4px 6px !important;
                }
                
                .detail-section {
                    padding: 10px !important;
                }
                
                .pagination {
                    flex-wrap: wrap !important;
                    gap: 4px !important;
                }
                
                .pagination-button {
                    margin: 2px !important;
                    padding: 5px 8px !important;
                    font-size: 12px !important;
                }
                
                .tabs {
                    flex-wrap: wrap !important;
                }
                
                .tabs button {
                    padding: 6px 8px !important;
                    font-size: 0.9em !important;
                    margin-bottom: 5px !important;
                    flex-grow: 1 !important;
                }
                
                .close-details {
                    font-size: 1.2em !important;
                    padding: 2px 8px !important;
                    right: 5px !important;
                    top: 5px !important;
                }
                
                .details-row td {
                    padding: 5px !important;
                }
                
                /* Esconder colunas menos importantes em dispositivos móveis */
                table th:nth-child(4), 
                table td:nth-child(4),
                table th:nth-child(6), 
                table td:nth-child(6),
                table th:nth-child(12), 
                table td:nth-child(12) {
                    display: none !important;
                }
            }
            </style>
            """,
            1
        )
    
    return html_content

def process_html_file(filepath):
    """
    Processa um arquivo HTML, aplicando estilos personalizados
    
    Args:
        filepath: Caminho do arquivo HTML
    
    Returns:
        bool: True se o arquivo foi processado com sucesso, False caso contrário
    """
    try:
        with open(filepath, 'r', encoding='utf-8') as file:
            content = file.read()
        
        modified_content = apply_style_changes(content)
        
        with open(filepath, 'w', encoding='utf-8') as file:
            file.write(modified_content)
        
        return True
    except Exception as e:
        print(f"Erro ao processar o arquivo HTML: {e}")
        return False