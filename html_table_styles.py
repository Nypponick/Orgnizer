"""
Estilos CSS personalizados para as tabelas dos relatórios HTML
"""

# Estilo com fonte Segoe UI e bordas sutis
HTML_STYLES = """
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 20px;
            color: #333;
        }
        .container {
            max-width: 100%;
            margin: 0 auto;
            padding: 20px;
            background: #fff;
            box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
            border-radius: 5px;
        }
        
        /* Estilo de tabela com bordas sutis */
        table {
            width: 100%;
            border-collapse: collapse;
            margin-bottom: 20px;
            border: none;
        }
        table th, table td {
            padding: 8px 10px;
            text-align: left;
            border-bottom: 1px solid #f0f0f0;
            border-right: 1px solid #f0f0f0;
        }
        table th {
            background: #f5f5f5;
            font-weight: 700;
            position: relative;
            padding-right: 20px;
            border-bottom: 1px solid #e0e0e0;
            border-right: 1px solid #e0e0e0;
        }
    </style>
"""

def get_custom_styles():
    """Retorna os estilos CSS personalizados"""
    return HTML_STYLES