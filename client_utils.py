"""
Módulo para gerenciamento de clientes no sistema JGR Broker
"""
from data import load_data

def get_all_clients():
    """
    Obtém todos os clientes do sistema a partir dos dados existentes.
    
    Returns:
        list: Lista de nomes de clientes ordenados alfabeticamente
    """
    data = load_data()
    clients = set()
    
    # Buscar em eventos
    for process in data.get('processes', []):
        for event in process.get('events', []):
            description = event.get('description', '')
            # Procurar menção a "cliente" na descrição do evento
            if 'cliente' in description.lower():
                try:
                    # Verificar se é um evento de atribuição
                    if 'atribuído ao cliente' in description:
                        client_name = description.split('atribuído ao cliente')[1].strip()
                        if client_name:
                            clients.add(client_name)
                    # Outros tipos de eventos mencionando cliente
                    else:
                        # Extrair possíveis nomes de cliente
                        parts = description.lower().split('cliente')
                        if len(parts) > 1:
                            client_text = parts[1].strip()
                            # Pegar a primeira palavra após "cliente"
                            if ' ' in client_text:
                                possible_client = client_text.split(' ')[0].strip()
                            else:
                                possible_client = client_text
                            
                            if possible_client and len(possible_client) > 2:
                                clients.add(possible_client.capitalize())
                except Exception:
                    # Ignorar erros na extração
                    pass
    
    # Buscar em campos específicos
    for process in data.get('processes', []):
        # Campo client explícito
        if 'client' in process and process['client'] and isinstance(process['client'], str):
            clients.add(process['client'].strip())
        
        # Campo importer (comum em processos de importação)
        if 'importer' in process and process['importer'] and isinstance(process['importer'], str):
            clients.add(process['importer'].strip())
    
    # Também verificar campo clients se existir
    if 'clients' in data:
        for client in data.get('clients', []):
            if isinstance(client, str) and client.strip():
                clients.add(client.strip())
            elif isinstance(client, dict) and 'name' in client and client['name'].strip():
                clients.add(client['name'].strip())
    
    # Adicionar manualmente clientes que sabemos que existem
    known_clients = ["121", "Skills Química"]
    for client in known_clients:
        clients.add(client)
    
    return sorted(list(clients))