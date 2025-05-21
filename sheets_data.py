"""
Módulo para gerenciar dados usando Google Sheets como banco de dados
"""
import os
import json
import datetime
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
import streamlit as st

# Constantes
PROCESSES_SHEET_NAME = "Processos"
USERS_SHEET_NAME = "Usuários"
CONFIG_SHEET_NAME = "Configurações"
STATUS_SHEET_NAME = "Status"

def get_credentials():
    """
    Verifica e retorna as credenciais para acessar a API do Google Sheets.
    Procura credenciais nas variáveis de ambiente do Streamlit ou em arquivo local.
    
    Returns:
        ServiceAccountCredentials: Credenciais para acesso à API
    """
    # Verificar se as credenciais estão no Streamlit Secrets
    creds_json = {}
    creds_file = "credentials.json"
    
    # Tentar obter credenciais do Streamlit Secrets
    try:
        if hasattr(st, 'secrets') and 'GOOGLE_CREDENTIALS' in st.secrets:
            creds_json = st.secrets['GOOGLE_CREDENTIALS']
            # Se for uma string JSON, converter para dicionário
            if isinstance(creds_json, str):
                creds_json = json.loads(creds_json)
    except Exception as e:
        st.warning(f"Secrets não configurados: {str(e)}")
    
    # Se não encontrar no Streamlit Secrets, tentar ler do arquivo
    if not creds_json and os.path.exists(creds_file):
        try:
            with open(creds_file, 'r') as f:
                creds_json = json.load(f)
        except Exception as e:
            st.error(f"Erro ao carregar credenciais do arquivo: {str(e)}")
    
    # Se ainda não tiver credenciais, mostrar erro
    if not creds_json:
        st.error("Credenciais do Google não encontradas. Consulte a documentação para configurar.")
        return None
    
    # Escopos necessários para acessar a API
    scope = 'https://spreadsheets.google.com/feeds https://www.googleapis.com/auth/drive'
    
    try:
        # Criar credenciais
        if isinstance(creds_json, dict):
            credentials = ServiceAccountCredentials.from_json_keyfile_dict(creds_json, scope)
        else:
            credentials = ServiceAccountCredentials.from_json_keyfile_name(creds_json, scope)
        return credentials
    except Exception as e:
        st.error(f"Erro ao criar credenciais: {str(e)}")
        return None

def get_google_sheets_client():
    """
    Obter cliente autenticado do Google Sheets
    
    Returns:
        gspread.Client: Cliente autenticado para acesso às planilhas
    """
    credentials = get_credentials()
    if credentials:
        try:
            # Convertemos explicitamente para garantir compatibilidade de tipos
            client = gspread.authorize(credentials)
            return client
        except Exception as e:
            st.error(f"Erro ao autorizar cliente do Google Sheets: {str(e)}")
    return None

def get_spreadsheet(spreadsheet_id=None, spreadsheet_name=None):
    """
    Obter ou criar a planilha para armazenar os dados
    
    Args:
        spreadsheet_id: ID da planilha (opcional)
        spreadsheet_name: Nome da planilha (opcional, usado se id não for fornecido)
    
    Returns:
        gspread.Spreadsheet: Objeto de planilha
    """
    client = get_google_sheets_client()
    if not client:
        return None
    
    try:
        # Tentar obter por ID se fornecido
        if spreadsheet_id:
            return client.open_by_key(spreadsheet_id)
        
        # Se não tiver ID mas tiver nome, tentar obter por nome
        if spreadsheet_name:
            try:
                return client.open(spreadsheet_name)
            except gspread.exceptions.SpreadsheetNotFound:
                # Se não encontrar, criar uma nova
                return client.create(spreadsheet_name)
        
        # Se não tiver ID nem nome, usar o padrão
        spreadsheet_name = "JGR Broker - Dados"
        try:
            return client.open(spreadsheet_name)
        except gspread.exceptions.SpreadsheetNotFound:
            return client.create(spreadsheet_name)
            
    except Exception as e:
        st.error(f"Erro ao acessar planilha: {str(e)}")
        return None

def initialize_sheets(spreadsheet):
    """
    Inicializa as planilhas necessárias se não existirem
    
    Args:
        spreadsheet: Objeto de planilha do Google Sheets
    """
    if not spreadsheet:
        return
    
    try:
        # Verificar as planilhas existentes
        existing_sheets = [sheet.title for sheet in spreadsheet.worksheets()]
        
        # Criar planilhas necessárias se não existirem
        if PROCESSES_SHEET_NAME not in existing_sheets:
            processes_sheet = spreadsheet.add_worksheet(title=PROCESSES_SHEET_NAME, rows=1000, cols=50)
            # Adicionar cabeçalhos
            headers = ["id", "tipo", "status", "ref", "po", "origin", "product", "eta", 
                      "free_time", "free_time_expiry", "empty_return", "terminal", 
                      "port_entry_date", "current_period_start", "current_period_expiry", 
                      "storage_days", "map", "invoice", "original_docs", "exporter", 
                      "ship", "agent", "bl_number", "container", "arrival_date", 
                      "di", "invoice_number", "return_date", "archived", "client_id",
                      "observations", "events", "last_update"]
            processes_sheet.append_row(headers)
        
        if USERS_SHEET_NAME not in existing_sheets:
            users_sheet = spreadsheet.add_worksheet(title=USERS_SHEET_NAME, rows=100, cols=10)
            # Adicionar cabeçalhos
            headers = ["username", "password", "name", "role", "client_id", "email", "phone", "logo_path"]
            users_sheet.append_row(headers)
            
            # Adicionar usuário admin padrão
            admin_user = ["admin", "admin", "Administrador", "admin", "", "", "", ""]
            users_sheet.append_row(admin_user)
        
        if CONFIG_SHEET_NAME not in existing_sheets:
            config_sheet = spreadsheet.add_worksheet(title=CONFIG_SHEET_NAME, rows=100, cols=2)
            # Adicionar cabeçalhos
            headers = ["key", "value"]
            config_sheet.append_row(headers)
            
            # Adicionar configurações padrão
            config_sheet.append_row(["storage_days_per_period", "15"])
            config_sheet.append_row(["last_sync", datetime.datetime.now().isoformat()])
        
        if STATUS_SHEET_NAME not in existing_sheets:
            status_sheet = spreadsheet.add_worksheet(title=STATUS_SHEET_NAME, rows=100, cols=3)
            # Adicionar cabeçalhos
            headers = ["status", "color", "process_type"]
            status_sheet.append_row(headers)
            
            # Adicionar status padrão
            default_status = [
                ["Novo Processo", "#6a0dad", "both"],
                ["Em andamento", "orange", "both"],
                ["Concluído", "green", "both"],
                ["Navio em Santos", "#4169e1", "importacao"],
                ["Documentos recebidos", "#20b2aa", "exportacao"]
            ]
            for status in default_status:
                status_sheet.append_row(status)
        
    except Exception as e:
        st.error(f"Erro ao inicializar planilhas: {str(e)}")

def sheet_to_dataframe(worksheet):
    """
    Converte uma planilha para um DataFrame do pandas
    
    Args:
        worksheet: Planilha do Google Sheets
    
    Returns:
        pandas.DataFrame: DataFrame com os dados da planilha
    """
    if not worksheet:
        return pd.DataFrame()
    
    try:
        data = worksheet.get_all_records()
        df = pd.DataFrame(data)
        return df
    except Exception as e:
        st.error(f"Erro ao converter planilha para DataFrame: {str(e)}")
        return pd.DataFrame()

def dataframe_to_sheet(df, worksheet, clear=True):
    """
    Salva um DataFrame do pandas em uma planilha do Google Sheets
    
    Args:
        df: DataFrame a ser salvo
        worksheet: Planilha onde salvar os dados
        clear: Se True, limpa a planilha antes de salvar
    """
    if df.empty or not worksheet:
        return
    
    try:
        # Obter cabeçalhos atuais da planilha
        headers = worksheet.row_values(1)
        
        if clear:
            # Limpar planilha mantendo os cabeçalhos
            worksheet.resize(rows=1)
            worksheet.resize(rows=df.shape[0] + 1)  # +1 para os cabeçalhos
        
        # Converter eventos e outras colunas complexas para string JSON
        for col in df.columns:
            if col in ['events'] or df[col].apply(lambda x: isinstance(x, (dict, list))).any():
                df[col] = df[col].apply(lambda x: json.dumps(x) if x else "")
        
        # Preparar valores para atualização
        values = [df.columns.tolist()]  # cabeçalhos
        values.extend(df.values.tolist())  # dados
        
        # Atualizar planilha
        cells_range = f'A1:{chr(64 + len(values[0]))}{len(values)}'
        cell_list = worksheet.range(cells_range)
        
        # Preencher valores
        for i, row in enumerate(values):
            for j, val in enumerate(row):
                cell_list[i * len(row) + j].value = val
        
        # Atualizar células
        worksheet.update_cells(cell_list)
        
    except Exception as e:
        st.error(f"Erro ao salvar DataFrame na planilha: {str(e)}")

def load_from_sheets():
    """
    Carrega todos os dados das planilhas do Google Sheets
    
    Returns:
        dict: Dicionário com todos os dados (processes, users, status_config)
    """
    # Obter planilha
    spreadsheet = get_spreadsheet()
    if not spreadsheet:
        st.error("Não foi possível acessar o Google Sheets. Usando dados locais...")
        from data import load_data
        return load_data()
    
    # Inicializar planilhas se necessário
    initialize_sheets(spreadsheet)
    
    try:
        # Carregar dados de processos
        processes_sheet = spreadsheet.worksheet(PROCESSES_SHEET_NAME)
        processes_df = sheet_to_dataframe(processes_sheet)
        
        # Converter colunas de eventos e outras de JSON para dicionários/listas
        if not processes_df.empty and 'events' in processes_df.columns:
            processes_df['events'] = processes_df['events'].apply(
                lambda x: json.loads(x) if x and isinstance(x, str) else []
            )
        
        # Converter DataFrame para lista de dicionários
        processes = processes_df.to_dict('records') if not processes_df.empty else []
        
        # Carregar dados de usuários
        users_sheet = spreadsheet.worksheet(USERS_SHEET_NAME)
        users_df = sheet_to_dataframe(users_sheet)
        
        # Converter DataFrame para dicionários indexados por username
        users = {}
        if not users_df.empty:
            for _, row in users_df.iterrows():
                users[row['username']] = row.to_dict()
        
        # Carregar configurações
        config_sheet = spreadsheet.worksheet(CONFIG_SHEET_NAME)
        config_df = sheet_to_dataframe(config_sheet)
        
        # Converter DataFrame para dicionário
        config = {}
        if not config_df.empty:
            for _, row in config_df.iterrows():
                # Tentar converter valor para número se possível
                try:
                    value = str(row['value'])
                    if value.isdigit():
                        value = int(value)
                    elif value.replace('.', '', 1).isdigit():
                        value = float(value)
                    config[str(row['key'])] = value
                except:
                    config[str(row['key'])] = str(row['value'])
        
        # Carregar configurações de status
        status_sheet = spreadsheet.worksheet(STATUS_SHEET_NAME)
        status_df = sheet_to_dataframe(status_sheet)
        
        # Converter DataFrame para formato usado pela aplicação
        status_config = {"importacao": [], "exportacao": [], "both": []}
        if not status_df.empty:
            for _, row in status_df.iterrows():
                status_item = {"status": row['status'], "color": row['color']}
                process_type = row['process_type']
                
                # Adicionar status ao grupo apropriado
                if process_type in status_config:
                    status_config[process_type].append(status_item)
                    
                # Se for "both", adicionar também a importação e exportação
                if process_type == "both":
                    status_config["importacao"].append(status_item)
                    status_config["exportacao"].append(status_item)
        
        # Criar dicionário com todos os dados
        data = {
            "processes": processes,
            "users": users,
            "config": config,
            "status_config": status_config
        }
        
        # Atualizar timestamp da última sincronização
        update_sync_timestamp(spreadsheet)
        
        return data
    
    except Exception as e:
        st.error(f"Erro ao carregar dados do Google Sheets: {str(e)}")
        st.warning("Usando dados locais como fallback...")
        from data import load_data
        return load_data()

def save_to_sheets(data):
    """
    Salva todos os dados nas planilhas do Google Sheets
    
    Args:
        data: Dicionário com todos os dados (processes, users, config, status_config)
    
    Returns:
        bool: True se os dados foram salvos com sucesso, False caso contrário
    """
    # Obter planilha
    spreadsheet = get_spreadsheet()
    if not spreadsheet:
        st.error("Não foi possível acessar o Google Sheets. Salvando dados localmente...")
        from data import save_data
        return save_data(data)
    
    # Inicializar planilhas se necessário
    initialize_sheets(spreadsheet)
    
    try:
        # Salvar dados de processos
        processes = data.get("processes", [])
        processes_df = pd.DataFrame(processes)
        processes_sheet = spreadsheet.worksheet(PROCESSES_SHEET_NAME)
        dataframe_to_sheet(processes_df, processes_sheet)
        
        # Salvar dados de usuários
        users = data.get("users", {})
        users_list = list(users.values())
        users_df = pd.DataFrame(users_list)
        users_sheet = spreadsheet.worksheet(USERS_SHEET_NAME)
        dataframe_to_sheet(users_df, users_sheet)
        
        # Salvar configurações
        config = data.get("config", {})
        config_list = [{"key": k, "value": str(v)} for k, v in config.items()]
        config_df = pd.DataFrame(config_list)
        config_sheet = spreadsheet.worksheet(CONFIG_SHEET_NAME)
        dataframe_to_sheet(config_df, config_sheet)
        
        # Salvar configurações de status
        status_config = data.get("status_config", {})
        status_list = []
        
        # Processar status para importação
        for status_item in status_config.get("importacao", []):
            # Verificar se já existe na exportação
            exists_in_export = any(
                s["status"] == status_item["status"] 
                for s in status_config.get("exportacao", [])
            )
            
            # Se existir em ambos, marcar como "both"
            if exists_in_export:
                status_list.append({
                    "status": status_item["status"],
                    "color": status_item["color"],
                    "process_type": "both"
                })
            else:
                status_list.append({
                    "status": status_item["status"],
                    "color": status_item["color"],
                    "process_type": "importacao"
                })
        
        # Adicionar status exclusivos de exportação
        for status_item in status_config.get("exportacao", []):
            # Verificar se já foi adicionado (como "both")
            already_added = any(
                s["status"] == status_item["status"] 
                for s in status_list
            )
            
            if not already_added:
                status_list.append({
                    "status": status_item["status"],
                    "color": status_item["color"],
                    "process_type": "exportacao"
                })
        
        status_df = pd.DataFrame(status_list)
        status_sheet = spreadsheet.worksheet(STATUS_SHEET_NAME)
        dataframe_to_sheet(status_df, status_sheet)
        
        # Atualizar timestamp da última sincronização
        update_sync_timestamp(spreadsheet)
        
        return True
    
    except Exception as e:
        st.error(f"Erro ao salvar dados no Google Sheets: {str(e)}")
        st.warning("Salvando dados localmente como fallback...")
        from data import save_data
        return save_data(data)

def update_sync_timestamp(spreadsheet):
    """
    Atualiza o timestamp da última sincronização
    
    Args:
        spreadsheet: Objeto de planilha do Google Sheets
    """
    try:
        config_sheet = spreadsheet.worksheet(CONFIG_SHEET_NAME)
        now = datetime.datetime.now().isoformat()
        
        # Verificar se já existe a linha
        cell = config_sheet.find("last_sync")
        if cell:
            config_sheet.update_cell(cell.row, 2, now)
        else:
            config_sheet.append_row(["last_sync", now])
    except Exception as e:
        print(f"Erro ao atualizar timestamp de sincronização: {str(e)}")

def get_sync_status():
    """
    Verifica o status de sincronização com o Google Sheets
    
    Returns:
        dict: Dicionário com informações sobre a sincronização
    """
    # Verificar se existem credenciais
    creds_file = "credentials.json"
    if not os.path.exists(creds_file):
        return {
            "connected": False,
            "spreadsheet_name": None,
            "last_sync": None,
            "sheets": [],
            "error": "Credenciais não encontradas. Por favor, faça upload do arquivo de credenciais."
        }
    
    # Obter planilha
    spreadsheet = get_spreadsheet()
    if not spreadsheet:
        return {
            "connected": False,
            "spreadsheet_name": None,
            "last_sync": None,
            "sheets": []
        }
    
    try:
        # Obter informações sobre as planilhas
        sheets = [sheet.title for sheet in spreadsheet.worksheets()]
        
        # Obter timestamp da última sincronização
        last_sync = None
        try:
            config_sheet = spreadsheet.worksheet(CONFIG_SHEET_NAME)
            cell = config_sheet.find("last_sync")
            if cell:
                last_sync = config_sheet.cell(cell.row, 2).value
        except:
            pass
        
        return {
            "connected": True,
            "spreadsheet_name": spreadsheet.title,
            "spreadsheet_url": f"https://docs.google.com/spreadsheets/d/{spreadsheet.id}",
            "last_sync": last_sync,
            "sheets": sheets
        }
    except Exception as e:
        st.error(f"Erro ao verificar status de sincronização: {str(e)}")
        return {
            "connected": False,
            "error": str(e),
            "spreadsheet_name": None,
            "last_sync": None,
            "sheets": []
        }

def upload_credentials(uploaded_file):
    """
    Salva as credenciais do Google Sheets a partir de um arquivo JSON
    
    Args:
        uploaded_file: Arquivo JSON com as credenciais
        
    Returns:
        bool: True se as credenciais foram salvas com sucesso, False caso contrário
    """
    try:
        # Salvar o arquivo
        with open("credentials.json", "wb") as f:
            f.write(uploaded_file.getbuffer())
        
        # Verificar se as credenciais são válidas
        credentials = get_credentials()
        if not credentials:
            os.remove("credentials.json")
            return False
        
        return True
    except Exception as e:
        st.error(f"Erro ao salvar credenciais: {str(e)}")
        return False

def display_sheets_settings():
    """
    Exibe interface para configurar integração com Google Sheets
    """
    st.header("Configuração do Google Sheets")
    
    # Verificar se a integração está ativada
    if 'use_google_sheets' not in st.session_state:
        st.session_state.use_google_sheets = False
    
    # Instruções iniciais
    st.markdown("""
    ### Como usar a integração com Google Sheets

    Esta funcionalidade permite armazenar os dados do sistema em uma planilha do Google Sheets, facilitando:
    - **Acesso remoto** aos dados de qualquer lugar
    - **Colaboração em tempo real** entre múltiplos usuários
    - **Backup automático** dos seus dados
    - **Edição direta** das informações quando necessário
    
    Para começar a usar, siga os passos abaixo:
    """)
    
    # Opção para ativar/desativar a integração
    st.session_state.use_google_sheets = st.toggle(
        "Ativar integração com Google Sheets",
        value=st.session_state.use_google_sheets,
        help="Se ativado, os dados serão sincronizados com o Google Sheets"
    )
    
    if st.session_state.use_google_sheets:
        st.success("✅ Integração com Google Sheets ativada!")
    else:
        st.warning("⚠️ Integração com Google Sheets desativada. Os dados serão salvos apenas localmente.")
    
    st.divider()
    
    # Verificar status atual
    try:
        sync_status = get_sync_status()
        
        # Exibir status atual
        if sync_status["connected"]:
            st.success("✅ Conectado ao Google Sheets")
            st.write(f"**Planilha:** {sync_status['spreadsheet_name']}")
            st.write(f"**URL:** {sync_status['spreadsheet_url']}")
            st.write(f"**Última sincronização:** {sync_status['last_sync']}")
            st.write(f"**Abas disponíveis:** {', '.join(sync_status['sheets'])}")
        else:
            st.warning("⚠️ Não conectado ao Google Sheets")
            if "error" in sync_status:
                st.info(sync_status["error"])
    except Exception as e:
        st.warning("⚠️ Não foi possível verificar o status da conexão com o Google Sheets")
        st.info("Você precisa primeiro configurar as credenciais do Google Sheets para usar esta funcionalidade.")
    
    st.divider()
    
    # Upload de credenciais
    st.subheader("Credenciais do Google Sheets")
    st.write("""
    Para usar o Google Sheets como banco de dados, você precisa fornecer um arquivo de credenciais JSON.
    
    ### Passo a passo para obter suas credenciais:
    
    1. **Acesse o Google Cloud Console:**
       - Vá para [console.cloud.google.com](https://console.cloud.google.com/)
       - Faça login com sua conta Google
    
    2. **Crie um novo projeto:**
       - Clique no seletor de projetos no topo da página
       - Clique em "Novo Projeto"
       - Dê um nome para seu projeto (ex: "JGR Broker") e clique em "Criar"
       
    3. **Ative as APIs necessárias:**
       - No menu lateral, navegue até "APIs e Serviços" > "Biblioteca"
       - Ative as seguintes APIs (pesquise por elas):
         * Google Sheets API
         * Google Drive API
    
    4. **Crie uma conta de serviço:**
       - No menu lateral, navegue até "APIs e Serviços" > "Credenciais"
       - Clique em "Criar Credenciais" > "Conta de serviço"
       - Dê um nome para a conta (ex: "jgr-broker-service")
       - Opcional: adicione uma descrição
       - Clique em "Criar e Continuar"
       - No passo de "Conceder acesso", escolha o papel "Editor" e clique em "Continuar"
       - Clique em "Concluído"
    
    5. **Crie uma chave JSON:**
       - Na lista de contas de serviço, clique na conta que você acabou de criar
       - Vá para a aba "Chaves"
       - Clique em "Adicionar Chave" > "Criar nova chave"
       - Selecione "JSON" e clique em "Criar"
       - O arquivo JSON será baixado automaticamente para seu computador
    
    6. **Faça upload do arquivo JSON aqui:**
       - Use o campo abaixo para enviar o arquivo de credenciais
    
    7. **Compartilhe sua planilha (opcional):**
       - Se você já tem uma planilha específica que deseja usar, compartilhe-a com o e-mail da conta de serviço
       - O e-mail está no formato `nome-da-conta@nome-do-projeto.iam.gserviceaccount.com`
       - Se não compartilhar, o sistema criará uma nova planilha automaticamente
    """)
    
    uploaded_file = st.file_uploader("Selecione o arquivo de credenciais JSON", type=["json"])
    
    if uploaded_file is not None:
        if upload_credentials(uploaded_file):
            st.success("✅ Credenciais salvas com sucesso!")
            st.rerun()
        else:
            st.error("❌ Erro ao salvar credenciais. Verifique se o arquivo está correto.")
    
    # Opções de sincronização
    if sync_status["connected"]:
        st.divider()
        st.subheader("Operações de sincronização")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("🔄 Sincronizar dados agora", use_container_width=True):
                with st.spinner("Sincronizando dados..."):
                    from data import load_data, save_data
                    
                    # Carregar dados atuais (local)
                    local_data = load_data()
                    
                    # Salvar no Google Sheets
                    if save_to_sheets(local_data):
                        st.success("✅ Dados sincronizados com sucesso!")
                    else:
                        st.error("❌ Erro ao sincronizar dados.")
        
        with col2:
            if st.button("⬇️ Carregar dados do Google Sheets", use_container_width=True):
                with st.spinner("Carregando dados..."):
                    # Carregar do Google Sheets
                    sheets_data = load_from_sheets()
                    
                    # Salvar localmente
                    from data import save_data
                    if save_data(sheets_data):
                        st.success("✅ Dados carregados com sucesso!")
                    else:
                        st.error("❌ Erro ao carregar dados.")
                    
                    # Reiniciar a aplicação para refletir os novos dados
                    st.rerun()
    
    # Modo de operação
    st.divider()
    st.subheader("Modo de operação")
    
    mode = st.radio(
        "Selecione como o sistema deve armazenar os dados:",
        ["Modo híbrido (Google Sheets + arquivo local)", "Apenas Google Sheets", "Apenas arquivo local"]
    )
    
    if st.button("Salvar modo de operação"):
        # Implementar a lógica para salvar o modo de operação
        st.success(f"Modo de operação configurado para: {mode}")
        # TODO: Salvar esta configuração


if __name__ == "__main__":
    display_sheets_settings()