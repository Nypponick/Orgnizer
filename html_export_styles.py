"""
Estilos CSS padrão para exportações HTML
"""

# Estilo da fonte padrão para todas as exportações HTML
DEFAULT_FONT_STYLE = "'Segoe UI', Tahoma, Geneva, Verdana, sans-serif"

def get_basic_styles():
    """Retorna os estilos CSS básicos para os relatórios HTML"""
    return f"""
    <style>
        body {{
            font-family: {DEFAULT_FONT_STYLE};
            margin: 0;
            padding: 20px;
            color: #333;
        }}
        
        table {{
            width: 100%;
            border-collapse: collapse;
            margin-bottom: 20px;
            border: none;
        }}
        
        table th, table td {{
            padding: 8px 10px;
            text-align: left;
            border-bottom: 1px solid #f0f0f0;
            border-right: 1px solid #f0f0f0;
        }}
        
        table th {{
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
        }}
        
        .status-badge {{
            color: white;
            padding: 4px 12px;
            border-radius: 50px;
            font-weight: bold;
            display: inline-block;
            box-shadow: 0 1px 3px rgba(0,0,0,0.12), 0 1px 2px rgba(0,0,0,0.24);
            font-size: 0.75em;
            letter-spacing: 0.3px;
            min-width: 40px;
            max-width: 100%;
            text-align: center;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
            line-height: 1.5;
        }}
        
        .status-count-item {{
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
        }}
        
        .status-count-item.selected {{
            border: 2px solid white;
            box-shadow: 0 0 0 2px #2c3e50;
        }}
        
        .status-count-item:hover {{
            transform: translateY(-2px);
        }}
    </style>
    """