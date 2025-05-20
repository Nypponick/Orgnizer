"""
Módulo para definir estilos personalizados para os relatórios HTML
"""

def get_html_styles():
    """Retorna os estilos CSS padrão para relatórios HTML"""
    return """
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 20px;
            color: #333;
            background-color: #f7f9fc;
        }
        
        .container {
            max-width: 100%;
            margin: 0 auto;
            padding: 20px;
            background: #fff;
            box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
            border-radius: 5px;
        }
        
        h1 {
            color: #2c3e50;
            margin-top: 0;
            border-bottom: 1px solid #eee;
            padding-bottom: 10px;
            font-size: 24px;
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
            cursor: pointer;
            position: relative;
            padding-right: 20px;
            border-bottom: 1px solid #e0e0e0;
            border-right: 1px solid #e0e0e0;
            font-size: 13px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            color: #000000;
        }
        
        .header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 20px;
            border-radius: 4px;
            border-bottom: 1px solid #eee;
            padding-bottom: 10px;
        }
        
        .status-badge {
            color: white;
            padding: 4px 12px;
            border-radius: 50px;
            font-weight: bold;
            display: inline-block;
            margin: 0 auto;
        }
        
        .status-count-item {
            background-color: #2c3e50;
            color: white;
            margin: 0 5px 5px 0;
            padding: 8px 15px;
            border-radius: 30px;
            display: inline-flex;
            align-items: center;
            cursor: pointer;
            transition: all 0.2s ease;
            border: 2px solid transparent;
        }
        
        .status-count-item.selected {
            border: 2px solid white;
            box-shadow: 0 0 0 2px #2c3e50;
        }
        
        .status-count-item:hover {
            transform: translateY(-2px);
        }
    </style>
    """