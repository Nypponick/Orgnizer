import streamlit as st
import pandas as pd
from datetime import datetime
import os
import sys
import urllib.parse

# Configurar o ambiente para encontrar módulos locais
current_path = os.path.dirname(os.path.abspath(__file__))
if current_path not in sys.path:
    sys.path.insert(0, current_path)
    print(f"Adicionado ao path: {current_path}")

# Agora tentar importar os módulos
try:
    # Importar os módulos necessários
    from components.home import display_home
    from components.add_edit import display_add_edit_form
    from components.view_details import display_detail_view
    from components.client_view import display_client_view
    from components.share import display_share_interface, validate_share_token
    from components.settings import display_settings
    from components.auth import display_login, display_user_management, init_auth_state, logout
    from components.archived import display_archived_processes
    from data import load_data, save_data
    from assets.stock_photos import get_random_image
    import sheets_to_html
except ImportError as e:
    st.error(f"""
    ## Erro de Importação
    
    A aplicação não conseguiu importar um ou mais módulos necessários: `{str(e)}`
    
    ### Verificando ambiente:
    - Diretório atual: `{os.getcwd()}`
    - Arquivos disponíveis: `{os.listdir()}`
    - Python path: `{sys.path}`
    """)
    # Se o problema for específico do módulo data, tente carregá-lo manualmente
    if "data" in str(e):
        st.info("Tentando carregar o módulo 'data' manualmente...")
        try:
            # Código para verificar se data.py existe e mostrar seu conteúdo
            if os.path.exists("data.py"):
                with open("data.py", "r") as f:
                    st.code(f.read()[:500] + "... (conteúdo truncado)")
            else:
                st.error("O arquivo 'data.py' não foi encontrado.")
                st.write("Arquivos disponíveis:", os.listdir())
        except Exception as inner_e:
            st.error(f"Erro ao verificar manualmente: {str(inner_e)}")
    st.stop()

# Page configuration
st.set_page_config(
    page_title="Sistema de Acompanhamento de Importação",
    page_icon="🚢",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load custom CSS
def load_css():
    st.markdown("""
    <style>
        .main .block-container {
            padding-top: 2rem;
            padding-bottom: 2rem;
        }
        .status-badge {
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
        }
        .close-btn {
            position: absolute;
            top: 10px;
            right: 10px;
            font-size: 16px;
            cursor: pointer;
            background: #f0f0f0;
            border: none;
            border-radius: 50%;
            width: 30px;
            height: 30px;
            display: flex;
            align-items: center;
            justify-content: center;
            transition: all 0.2s;
        }
        .close-btn:hover {
            background: #e0e0e0;
        }
        .detail-card {
            position: relative;
            padding: 20px;
            background: white;
            border-radius: 5px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
            margin-bottom: 20px;
        }
        .process-type-badge {
            display: inline-block;
            padding: 3px 8px;
            border-radius: 4px;
            font-size: 0.75em;
            font-weight: bold;
            margin-right: 5px;
        }
        .import-badge {
            background-color: #e3f2fd;
            color: #1976d2;
            border: 1px solid #bbdefb;
        }
        .export-badge {
            background-color: #f9fbe7;
            color: #827717;
            border: 1px solid #f0f4c3;
        }
        .st-emotion-cache-10oheav {
            padding-left: 5px !important;
            padding-right: 5px !important;
        }
        .highlight-input {
            background-color: rgba(255, 255, 0, 0.1);
        }
        div[data-testid="stDateInput"] > div:first-child {
            background-color: rgba(239, 245, 255, 0.4);
            border-radius: 6px;
            padding: 0px 5px;
        }
        div[data-testid="stTextInput"] > div:first-child {
            background-color: rgba(242, 246, 250, 0.4);
            border-radius: 6px;
            padding: 0px 5px;
        }
        div[data-testid="stNumberInput"] > div:first-child {
            background-color: rgba(242, 246, 250, 0.4);
            border-radius: 6px;
            padding: 0px 5px;
        }
        div[data-testid="stSelectbox"] > div:first-child {
            background-color: rgba(242, 246, 250, 0.4);
            border-radius: 6px;
            padding: 0px 5px;
        }
        .process-actions {
            display: flex;
            gap: 5px;
            justify-content: flex-end;
        }
        .auth-container {
            max-width: 450px;
            margin: 0 auto;
            padding: 30px;
            background: white;
            border-radius: 8px;
            box-shadow: 0 4px 10px rgba(0,0,0,0.15);
        }
        div[data-testid="stForm"] > div:nth-child(1) {
            background-color: rgba(250, 250, 250, 0.8);
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 1px 2px rgba(0,0,0,0.05);
        }
        .centered-spinner {
            text-align: center;
            margin-top: 50px;
        }
        .process-row {
            cursor: pointer;
        }
        .process-row:hover {
            background-color: #f5f8ff;
        }
        div[data-testid="stDataFrameResizable"] {
            border-radius: 8px;
            border: 1px solid #eaebec;
            overflow: hidden;
        }
    </style>
    """, unsafe_allow_html=True)

# User navigation function
def navigate_to(page, process_id=None):
    st.session_state.page = page
    if process_id is not None:
        st.session_state.process_id = process_id

# Initialize session state for navigation
if 'page' not in st.session_state:
    st.session_state.page = 'home'

if 'process_id' not in st.session_state:
    st.session_state.process_id = None

load_css()
init_auth_state()

# Authentication check
if not st.session_state.get('authenticated', False):
    display_login(navigate_to)
else:
    # Sidebar for navigation
    with st.sidebar:
        st.title("JGR Broker")
        
        if st.session_state.user_type == 'admin':
            st.subheader("Administração")
            if st.button("Página Inicial", use_container_width=True):
                navigate_to('home')
            if st.button("Adicionar Processo", use_container_width=True):
                navigate_to('add')
            if st.button("Processos Arquivados", use_container_width=True):
                navigate_to('archived')
            if st.button("Gerenciar Usuários", use_container_width=True):
                navigate_to('users')
            if st.button("Importar da Planilha", use_container_width=True):
                navigate_to('import_sheet')
            
            st.write("---")
        
        st.subheader("Sua Conta")
        st.write(f"Logado como: **{st.session_state.username}**")
        st.write(f"Tipo: **{st.session_state.user_type.capitalize()}**")
        
        if st.button("Sair", use_container_width=True):
            logout(navigate_to)

    # Main content based on navigation
    if st.session_state.page == 'home':
        display_home(navigate_to)
        
    elif st.session_state.page == 'add':
        if st.session_state.user_type == 'admin':
            display_add_edit_form(navigate_to)
        else:
            st.error("Acesso negado. Apenas administradores podem adicionar processos.")
            
    elif st.session_state.page == 'edit':
        if st.session_state.user_type == 'admin':
            display_add_edit_form(navigate_to, st.session_state.process_id)
        else:
            st.error("Acesso negado. Apenas administradores podem editar processos.")
            
    elif st.session_state.page == 'view':
        display_detail_view(navigate_to, st.session_state.process_id)
        
    elif st.session_state.page == 'client':
        display_client_view(navigate_to)
        
    elif st.session_state.page == 'users':
        if st.session_state.user_type == 'admin':
            display_user_management(navigate_to)
        else:
            st.error("Acesso negado. Apenas administradores podem gerenciar usuários.")
        
    elif st.session_state.page == 'share':
        if st.session_state.user_type == 'admin':
            display_share_interface(navigate_to, st.session_state.process_id)
        else:
            st.error("Acesso negado. Apenas administradores podem compartilhar processos.")
            
    elif st.session_state.page == 'settings':
        display_settings(navigate_to)
        
    elif st.session_state.page == 'archived':
        if st.session_state.user_type == 'admin':
            display_archived_processes(navigate_to)
        else:
            st.error("Acesso negado. Apenas administradores podem acessar processos arquivados.")
            
    elif st.session_state.page == 'import_sheet':
        if st.session_state.user_type == 'admin':
            sheets_to_html.convert_sheet_to_html()
        else:
            st.error("Acesso negado. Apenas administradores podem importar dados.")