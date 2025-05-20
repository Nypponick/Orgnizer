import streamlit as st
import os
import json
import time
from data import load_data, save_data

# Arquivo para armazenar os status personalizados
STATUS_FILE = "status_config.json"

# Função para obter os status disponíveis por tipo de processo
def get_status_options(process_type=None):
    """
    Retorna a lista de status disponíveis para o tipo de processo especificado.
    
    Args:
        process_type: "importacao", "exportacao" ou None (para todos)
        
    Returns:
        list: Lista de nomes de status
    """
    # Verificar se já temos os status na sessão
    if process_type == "importacao" and "status_options_import" in st.session_state:
        return st.session_state.status_options_import
    
    if process_type == "exportacao" and "status_options_export" in st.session_state:
        return st.session_state.status_options_export
    
    if process_type is None and "status_options" in st.session_state:
        return st.session_state.status_options
    
    # Se não temos em cache, carregar do arquivo
    status_config = load_status_config()
    
    # No novo formato, os status estão em status_config
    if "status_config" in status_config:
        status_items = status_config["status_config"]
        
        if process_type is None:
            # Retornar todos os status (nomes únicos)
            status_names = [item["name"] for item in status_items]
            st.session_state.status_options = status_names
            return status_names
        
        elif process_type == "importacao":
            # Filtrar por importação
            import_status = [item["name"] for item in status_items 
                            if "importacao" in item.get("process_types", [])]
            st.session_state.status_options_import = import_status
            return import_status
        
        elif process_type == "exportacao":
            # Filtrar por exportação
            export_status = [item["name"] for item in status_items 
                            if "exportacao" in item.get("process_types", [])]
            st.session_state.status_options_export = export_status
            return export_status
    
    # Formato antigo ou configuração vazia
    else:
        default_status = ["Novo Processo", "Em andamento", "Pendente", "Concluído"]
        if process_type == "importacao":
            default_status.append("Navio em Santos")
        if process_type == "exportacao":
            default_status.append("Booking confirmado")
        
        return default_status

def load_status_config():
    """Carrega a configuração de status do arquivo"""
    if os.path.exists(STATUS_FILE):
        try:
            with open(STATUS_FILE, 'r', encoding='utf-8') as f:
                config = json.load(f)
                
                # Verificar se o arquivo tem o formato antigo (apenas lista de status)
                if "status_list" in config and isinstance(config["status_list"], list) and not "status_config" in config:
                    # Converter formato antigo para o novo formato
                    status_list = config["status_list"]
                    status_config = []
                    
                    for status in status_list:
                        status_config.append({
                            "name": status,
                            "process_types": ["importacao", "exportacao"]  # Por padrão, disponível para ambos
                        })
                    
                    # Retornar no novo formato
                    return {"status_config": status_config}
                
                return config
                
        except Exception as e:
            st.error(f"Erro ao carregar status: {e}")
            return create_default_status_config()
    else:
        # Status padrão se o arquivo não existir
        return create_default_status_config()

def create_default_status_config():
    """Cria a configuração padrão de status"""
    default_status = [
        {"name": "Novo Processo", "process_types": ["importacao", "exportacao"]},
        {"name": "Em andamento", "process_types": ["importacao", "exportacao"]},
        {"name": "Pendente", "process_types": ["importacao", "exportacao"]},
        {"name": "Concluído", "process_types": ["importacao", "exportacao"]},
        {"name": "Navio em Santos", "process_types": ["importacao"]},
        {"name": "Booking confirmado", "process_types": ["exportacao"]},
    ]
    
    return {"status_config": default_status}
        
def save_status_config(status_config):
    """Salva a configuração de status no arquivo"""
    try:
        with open(STATUS_FILE, 'w', encoding='utf-8') as f:
            json.dump(status_config, f, indent=4)
        return True
    except Exception as e:
        st.error(f"Erro ao salvar status: {e}")
        return False

def display_status_manager():
    """Interface para gerenciar os status disponíveis no sistema"""
    # Verificar se temos status na sessão
    if 'temp_status_config' not in st.session_state:
        # Carregar status
        status_config = load_status_config()
        st.session_state.temp_status_config = status_config["status_config"].copy()
    
    # Título e instruções
    st.markdown("### Gerenciamento de Status")
    st.write("Adicione, edite ou remova os status disponíveis no sistema. Especifique se o status é para processos de Importação, Exportação ou ambos.")
    
    # Exibir status atuais
    st.markdown("#### Status Atuais")
    
    # Lista para controlar status que devem ser removidos
    if 'status_to_remove' not in st.session_state:
        st.session_state.status_to_remove = []
    
    # Exibir status existentes com opção de edição
    for i, status_item in enumerate(st.session_state.temp_status_config):
        st.markdown(f"##### Status {i+1}")
        col1, col2, col3 = st.columns([3, 3, 1])
        
        with col1:
            # Nome do status
            status_name = st.text_input(
                "Nome do Status", 
                value=status_item.get("name", ""), 
                key=f"status_name_{i}"
            )
            st.session_state.temp_status_config[i]["name"] = status_name
            
        with col2:
            # Multi-select para tipos de processo
            process_types = status_item.get("process_types", ["importacao", "exportacao"])
            process_types_options = {
                "importacao": "Importação",
                "exportacao": "Exportação"
            }
            
            # Criar valores padrão para a seleção
            default_types = []
            if "importacao" in process_types:
                default_types.append("importacao")
            if "exportacao" in process_types:
                default_types.append("exportacao")
            
            selected_types = st.multiselect(
                "Tipos de Processo",
                options=list(process_types_options.keys()),
                default=default_types,
                format_func=lambda x: process_types_options[x],
                key=f"process_types_{i}"
            )
            
            # Garantir que pelo menos um tipo está selecionado
            if not selected_types:
                st.warning("Selecione pelo menos um tipo de processo")
                # Usar importação como padrão se nada for selecionado
                selected_types = ["importacao"]
                
            st.session_state.temp_status_config[i]["process_types"] = selected_types
            
        with col3:
            if st.button("Remover", key=f"remove_{i}"):
                st.session_state.status_to_remove.append(i)
                st.rerun()
        
        st.divider()
    
    # Remover status marcados para remoção (em ordem reversa para não afetar os índices)
    if st.session_state.status_to_remove:
        for i in sorted(st.session_state.status_to_remove, reverse=True):
            if i < len(st.session_state.temp_status_config):
                del st.session_state.temp_status_config[i]
        # Limpar a lista de remoção
        st.session_state.status_to_remove = []
    
    # Adicionar novo status
    st.markdown("#### Adicionar Novo Status")
    
    if 'new_status_name' not in st.session_state:
        st.session_state.new_status_name = ""
    
    if 'new_status_types' not in st.session_state:
        st.session_state.new_status_types = ["importacao", "exportacao"]
    
    col1, col2 = st.columns(2)
    
    with col1:
        new_status_name = st.text_input(
            "Nome do Novo Status", 
            value=st.session_state.new_status_name,
            key="new_status_name_input"
        )
        st.session_state.new_status_name = new_status_name
    
    with col2:
        process_types_options = {
            "importacao": "Importação",
            "exportacao": "Exportação"
        }
        
        new_status_types = st.multiselect(
            "Tipos de Processo",
            options=list(process_types_options.keys()),
            default=st.session_state.new_status_types,
            format_func=lambda x: process_types_options[x],
            key="new_status_types_input"
        )
        
        if not new_status_types:
            st.warning("Selecione pelo menos um tipo de processo")
            # Usar ambos como padrão se nada for selecionado
            new_status_types = ["importacao", "exportacao"]
            
        st.session_state.new_status_types = new_status_types
    
    if st.button("Adicionar Status") and new_status_name:
        # Verificar se o status já existe
        status_names = [item["name"] for item in st.session_state.temp_status_config]
        
        if new_status_name not in status_names:
            # Adicionar novo status
            new_status_item = {
                "name": new_status_name,
                "process_types": new_status_types
            }
            st.session_state.temp_status_config.append(new_status_item)
            
            st.success(f"Status '{new_status_name}' adicionado com sucesso!")
            
            # Limpar os campos após adicionar
            st.session_state.new_status_name = ""
            st.session_state.new_status_types = ["importacao", "exportacao"]
            
            st.rerun()
        else:
            st.warning(f"Status '{new_status_name}' já existe!")
    
    # Botões de ação
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("Salvar Alterações", use_container_width=True):
            # Criar nova configuração com a lista temporária
            status_config = {"status_config": st.session_state.temp_status_config}
            if save_status_config(status_config):
                # Remover as listas de status da sessão para forçar recarregamento
                if 'status_options' in st.session_state:
                    del st.session_state['status_options']
                if 'status_options_import' in st.session_state:
                    del st.session_state['status_options_import']
                if 'status_options_export' in st.session_state:
                    del st.session_state['status_options_export']
                    
                st.success("Status atualizados com sucesso! As alterações estarão disponíveis ao adicionar um novo processo.")
                
                # Mostrar os status que foram salvos
                status_import = []
                status_export = []
                
                st.write("Status atualizados:")
                for status_item in st.session_state.temp_status_config:
                    name = status_item["name"]
                    types = status_item["process_types"]
                    
                    types_str = []
                    if "importacao" in types:
                        types_str.append("Importação")
                        status_import.append(name)
                    if "exportacao" in types:
                        types_str.append("Exportação")
                        status_export.append(name)
                        
                    st.write(f"- {name} ({', '.join(types_str)})")
                
                st.write("---")
                st.write(f"Total: {len(st.session_state.temp_status_config)} status")
                st.write(f"Status para Importação: {len(status_import)}")
                st.write(f"Status para Exportação: {len(status_export)}")
                
                # Limpar flag para forçar recarregamento na próxima vez
                if 'reload_status' in st.session_state:
                    del st.session_state['reload_status']
                
                # Aguardar um momento para garantir que a mensagem seja vista
                time.sleep(1)
                
                # Forçar recarregamento completo da página
                st.rerun()
            else:
                st.error("Erro ao salvar os status!")
    
    with col2:
        if st.button("Fechar", use_container_width=True):
            st.session_state.show_status_manager = False
            st.rerun()

def display_settings():
    """Display settings page for configuring email and SMS"""
    st.header("Configurações")
    
    # Create tabs for different settings
    tab1, tab2, tab3 = st.tabs(["Email", "SMS", "Configurações Gerais"])
    
    # Tab 1: Email Settings
    with tab1:
        st.subheader("Configurações de Email")
        st.info("Configure as informações do servidor SMTP para envio de emails.")
        
        # Get existing values from session state
        smtp_server = st.session_state.get('smtp_server', os.environ.get('SMTP_SERVER', ''))
        smtp_port = st.session_state.get('smtp_port', os.environ.get('SMTP_PORT', 587))
        smtp_username = st.session_state.get('smtp_username', os.environ.get('SMTP_USERNAME', ''))
        smtp_password = st.session_state.get('smtp_password', os.environ.get('SMTP_PASSWORD', ''))
        from_email = st.session_state.get('from_email', os.environ.get('FROM_EMAIL', ''))
        
        with st.form("email_settings"):
            col1, col2 = st.columns(2)
            
            with col1:
                new_smtp_server = st.text_input("Servidor SMTP", value=smtp_server)
                new_smtp_username = st.text_input("Usuário SMTP", value=smtp_username)
                new_from_email = st.text_input("Email de Envio", value=from_email or smtp_username)
            
            with col2:
                new_smtp_port = st.number_input("Porta SMTP", value=int(smtp_port), min_value=1, max_value=65535)
                new_smtp_password = st.text_input("Senha SMTP", value=smtp_password, type="password")
            
            submit = st.form_submit_button("Salvar Configurações de Email")
            
            if submit:
                # Store in session state
                st.session_state.smtp_server = new_smtp_server
                st.session_state.smtp_port = new_smtp_port
                st.session_state.smtp_username = new_smtp_username
                st.session_state.smtp_password = new_smtp_password
                st.session_state.from_email = new_from_email
                
                # Save to environment variables for current session
                os.environ['SMTP_SERVER'] = new_smtp_server
                os.environ['SMTP_PORT'] = str(new_smtp_port)
                os.environ['SMTP_USERNAME'] = new_smtp_username
                os.environ['SMTP_PASSWORD'] = new_smtp_password
                os.environ['FROM_EMAIL'] = new_from_email
                
                st.success("Configurações de email salvas com sucesso!")
        
        # Test email
        st.subheader("Testar Configurações de Email")
        with st.form("test_email"):
            test_email = st.text_input("Email para teste")
            test_submit = st.form_submit_button("Enviar Email de Teste")
            
            if test_submit and test_email:
                from utils import send_email
                result = send_email(
                    test_email, 
                    "Teste de Configuração de Email", 
                    "Este é um email de teste do Sistema de Acompanhamento de Importação."
                )
                
                if result:
                    st.success("Email de teste enviado com sucesso!")
                else:
                    st.error("Falha ao enviar email de teste. Verifique as configurações.")
    
    # Tab 2: SMS Settings
    with tab2:
        st.subheader("Configurações de SMS (Twilio)")
        st.info("Configure as credenciais do Twilio para envio de SMS.")
        
        # Get existing values
        account_sid = os.environ.get('TWILIO_ACCOUNT_SID', '')
        auth_token = os.environ.get('TWILIO_AUTH_TOKEN', '')
        phone_number = os.environ.get('TWILIO_PHONE_NUMBER', '')
        
        with st.form("sms_settings"):
            new_account_sid = st.text_input("Twilio Account SID", value=account_sid)
            new_auth_token = st.text_input("Twilio Auth Token", value=auth_token, type="password")
            new_phone_number = st.text_input("Número de Telefone Twilio", value=phone_number, 
                                         help="Formato: +553140025000")
            
            submit = st.form_submit_button("Salvar Configurações de SMS")
            
            if submit:
                # Save to environment variables
                os.environ['TWILIO_ACCOUNT_SID'] = new_account_sid
                os.environ['TWILIO_AUTH_TOKEN'] = new_auth_token
                os.environ['TWILIO_PHONE_NUMBER'] = new_phone_number
                
                st.success("Configurações de SMS salvas com sucesso!")
        
        # Test SMS
        st.subheader("Testar Configurações de SMS")
        with st.form("test_sms"):
            test_phone = st.text_input("Número de telefone para teste (com código do país)", 
                                   help="Exemplo: +5511912345678")
            test_submit = st.form_submit_button("Enviar SMS de Teste")
            
            if test_submit and test_phone:
                from utils import send_sms
                result = send_sms(
                    test_phone, 
                    "Teste do Sistema de Acompanhamento de Importação."
                )
                
                if result:
                    st.success("SMS de teste enviado com sucesso!")
                else:
                    st.error("Falha ao enviar SMS de teste. Verifique as configurações.")
    
    # Tab 3: General Settings
    with tab3:
        st.subheader("Configurações Gerais")
        
        # Company information
        st.info("Informações da Empresa (exibidas nos relatórios e emails)")
        
        with st.form("company_info"):
            company_name = st.text_input("Nome da Empresa", 
                                    value=st.session_state.get('company_name', ''))
            company_logo_url = st.text_input("URL do Logo da Empresa", 
                                        value=st.session_state.get('company_logo_url', ''))
            company_contact = st.text_input("Contato da Empresa", 
                                       value=st.session_state.get('company_contact', ''))
            
            submit = st.form_submit_button("Salvar Informações da Empresa")
            
            if submit:
                st.session_state.company_name = company_name
                st.session_state.company_logo_url = company_logo_url
                st.session_state.company_contact = company_contact
                
                st.success("Informações da empresa salvas com sucesso!")
        
        # Status Management
        st.subheader("Gerenciamento de Status")
        st.info("Crie, edite ou exclua os status disponíveis no sistema")
        
        # Função para gerenciar os status do sistema
        if st.button("Gerenciar Status", use_container_width=True):
            st.session_state.show_status_manager = True
            
        # Mostrar gerenciador de status se o botão foi clicado
        if st.session_state.get("show_status_manager", False):
            display_status_manager()
        
        # Backup and Restore
        st.subheader("Backup e Restauração")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("Fazer Backup dos Dados", use_container_width=True):
                import json
                import base64
                from datetime import datetime
                
                # Get data
                data = load_data()
                
                # Convert to JSON string
                json_str = json.dumps(data, indent=4)
                
                # Create download link
                b64 = base64.b64encode(json_str.encode()).decode()
                date_str = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"backup_importacao_{date_str}.json"
                
                href = f'<a href="data:application/json;base64,{b64}" download="{filename}">Clique para baixar o arquivo de backup</a>'
                st.markdown(href, unsafe_allow_html=True)
                
                st.success("Backup gerado com sucesso!")
        
        with col2:
            uploaded_file = st.file_uploader("Restaurar a partir de Backup", type=["json"])
            
            if uploaded_file is not None:
                try:
                    import json
                    content = uploaded_file.read().decode()
                    data = json.loads(content)
                    
                    if st.button("Confirmar Restauração"):
                        # Validate data structure
                        if "processes" in data:
                            # Save the data
                            save_data(data)
                            st.session_state.data = data
                            st.success("Dados restaurados com sucesso!")
                            st.rerun()
                        else:
                            st.error("Arquivo de backup inválido!")
                except Exception as e:
                    st.error(f"Erro ao processar arquivo: {e}")