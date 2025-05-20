import streamlit as st
import pandas as pd
from datetime import datetime
import os
import sys
import urllib.parse

# Adicionar diretório atual ao PYTHONPATH, se necessário
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

# Verificação do ambiente
try:
    import data
    print(f"Módulo data encontrado: {data.__file__}")
except ImportError as e:
    print(f"Erro ao importar o módulo data: {e}")
    print(f"PYTHONPATH: {sys.path}")
    print(f"Conteúdo do diretório atual: {os.listdir('.')}")
    raise

# Agora importamos os componentes
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

# Page configuration
st.set_page_config(
    page_title="Sistema de Acompanhamento de Importação",
    page_icon="🚢",
    layout="wide",
)

# Carregar estilos CSS personalizados
def load_css():
    css_file = "assets/custom.css"
    if os.path.exists(css_file):
        with open(css_file, "r") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    else:
        st.warning(f"Arquivo CSS não encontrado: {css_file}")

# Carregar os estilos CSS
load_css()

# Initialize session state
if 'data' not in st.session_state:
    st.session_state.data = load_data()
if 'current_page' not in st.session_state:
    st.session_state.current_page = "home"
if 'selected_process' not in st.session_state:
    st.session_state.selected_process = None
    
# Inicializar opções de status
if 'status_options' not in st.session_state:
    from components.settings import get_status_options
    # Carregar todos os status disponíveis (sem filtro de tipo)
    st.session_state.status_options = get_status_options()
if 'edit_mode' not in st.session_state:
    st.session_state.edit_mode = False
if 'filter_value' not in st.session_state:
    st.session_state.filter_value = ""
# Inicializa o estado de autenticação
init_auth_state()

# Check URL parameters for client view mode
query_params = st.query_params
if "token" in query_params:
    token = query_params["token"]
    process_id = validate_share_token(token)
    
    if process_id:
        # Display client view for this process
        st.image("assets/images/jgr_logo.png", width=150)
        st.title("JGR BROKER - Sistema de Acompanhamento de Importação")
        
        display_client_view(process_id)
        
        # Footer for client view
        st.divider()
        st.caption(f"© {datetime.now().year} JGR BROKER - Todos os direitos reservados")
        
        # Exit the app here to prevent showing the admin interface
        st.stop()
    else:
        st.error("Link de compartilhamento inválido ou expirado!")

# Navigation functions
def navigate_to(page, process_id=None):
    st.session_state.current_page = page
    if process_id is not None:
        st.session_state.selected_process = process_id
    st.rerun()

# Verificar autenticação para acessar o sistema
if not st.session_state.authenticated:
    display_login()
    st.stop()

# Header with logo and navigation
col1, col2, col3 = st.columns([1, 3, 1])

with col1:
    try:
        st.image("assets/images/jgr_logo.png", width=150)
    except:
        st.write("**JGR BROKER**")
    
with col2:
    st.title("Sistema de Acompanhamento de Importação")
    st.caption("JGR BROKER - Monitoramento e gestão de processos de importação")

with col3:
    # Exibir informações do usuário
    st.write(f"Olá, **{st.session_state.user_name}**")
    role_display = "Administrador" if st.session_state.user_role == "admin" else "Cliente"
    st.caption(f"Perfil: {role_display}")
    if st.button("🚪 Sair", use_container_width=True):
        logout()
        st.rerun()

# Navigation bar - Mostra todos os botões para administradores
if st.session_state.user_role == "admin":
    nav_col1, nav_col2, nav_col3, nav_col4, nav_col5, nav_col6, nav_col7 = st.columns(7)
    with nav_col1:
        if st.button("📋 Painel", use_container_width=True):
            navigate_to("home")
    with nav_col2:
        if st.button("➕ Novo Processo", use_container_width=True):
            st.session_state.edit_mode = False
            navigate_to("add_edit")
    with nav_col3:
        if st.button("📦 Arquivados", use_container_width=True):
            navigate_to("archived")
    with nav_col4:
        if st.button("🔗 Compartilhar", use_container_width=True):
            navigate_to("share")
    with nav_col5:
        if st.button("📊 Importar Planilha", use_container_width=True):
            navigate_to("reports")
    with nav_col6:
        if st.button("⚙️ Configurações", use_container_width=True):
            navigate_to("settings")
    with nav_col7:
        if st.button("👥 Usuários", use_container_width=True):
            navigate_to("users")
else:
    # Para clientes, apenas mostrar o botão de painel
    if st.button("📋 Painel", use_container_width=True):
        navigate_to("home")

st.divider()

# Display the current page
if st.session_state.current_page == "home":
    # Cliente só vê seus processos
    if st.session_state.user_role == 'client':
        display_home(navigate_to, filter_ids=st.session_state.client_processes)
    else:
        display_home(navigate_to)
elif st.session_state.current_page == "add_edit":
    # Somente admin pode adicionar/editar
    if st.session_state.user_role == 'admin':
        # Recarregar a lista de status do arquivo de configuração antes de exibir o formulário
        from components.settings import load_status_config
        status_config = load_status_config()
        from components.settings import get_status_options
        # Carregar todos os status disponíveis (sem filtro de tipo)
        st.session_state.status_options = get_status_options()
        
        display_add_edit_form(navigate_to)
    else:
        st.error("Você não tem permissão para acessar esta página.")
        navigate_to("home")
elif st.session_state.current_page == "view_details":
    # Cliente só pode ver seus processos
    if st.session_state.user_role == 'client' and st.session_state.selected_process not in st.session_state.client_processes:
        st.error("Você não tem permissão para visualizar este processo.")
        navigate_to("home")
    else:
        display_detail_view(navigate_to)
elif st.session_state.current_page == "share":
    # Somente admin pode compartilhar
    if st.session_state.user_role == 'admin':
        display_share_interface()
    else:
        st.error("Você não tem permissão para acessar esta página.")
        navigate_to("home")
elif st.session_state.current_page == "reports":
    # Somente admin pode acessar relatórios
    if st.session_state.user_role == 'admin':
        st.header("Importação de Planilha")
        
        tab1, tab2 = st.tabs(["Converter Planilha", "Baixar Modelo"])
        
        with tab1:
            sheets_to_html.convert_sheet_to_html()
        
        with tab2:
            sheets_to_html.create_template_file()
    else:
        st.error("Você não tem permissão para acessar esta página.")
        navigate_to("home")
elif st.session_state.current_page == "settings":
    # Somente admin pode acessar configurações
    if st.session_state.user_role == 'admin':
        display_settings()
    else:
        st.error("Você não tem permissão para acessar esta página.")
        navigate_to("home")
elif st.session_state.current_page == "users":
    # Somente admin pode gerenciar usuários
    if st.session_state.user_role == 'admin':
        display_user_management()
    else:
        st.error("Você não tem permissão para acessar esta página.")
        navigate_to("home")
elif st.session_state.current_page == "archived":
    # Somente admin pode ver processos arquivados
    if st.session_state.user_role == 'admin':
        display_archived_processes(navigate_to)
    else:
        st.error("Você não tem permissão para acessar esta página.")
        navigate_to("home")

# Footer
st.divider()
current_year = datetime.now().year
st.caption(f"© {current_year} JGR BROKER - Todos os direitos reservados")
