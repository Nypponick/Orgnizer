"""
Versão modificada para deploy no Streamlit Cloud
"""
import streamlit as st
import pandas as pd
from datetime import datetime
import os
import sys
import json

# Adicionar diretório atual ao PYTHONPATH
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

# Criar pasta components se não existir
if not os.path.exists("components"):
    os.makedirs("components")

# Verificar e criar pastas necessárias
for path in ["html_exports", "backups", "updates_export", "assets/client_logos"]:
    if not os.path.exists(path):
        os.makedirs(path, exist_ok=True)

# Importar módulos básicos
from data import load_data, save_data
from components.home import display_home
from components.add_edit import display_add_edit_form
from components.view_details import display_detail_view
from components.auth import display_login, display_user_management, init_auth_state, logout

# Configuração da página
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
    
with col3:
    # Exibir informações do usuário
    st.write(f"Olá, **{st.session_state.user_name}**")
    
    # Mostrar o papel do usuário apropriado
    role_display = "Administrador"
    if st.session_state.user_role == "manager":
        role_display = "Gestor FUP"
    elif st.session_state.user_role == "client":
        role_display = "Cliente"
        
    st.caption(f"Perfil: {role_display}")
    if st.button("🚪 Sair", use_container_width=True):
        logout()
        st.rerun()

# Navigation bar - Mostra os botões apropriados para cada perfil
if st.session_state.user_role == "admin":
    # Admin tem acesso completo
    nav_cols = st.columns(6)
    with nav_cols[0]:
        if st.button("📋 Painel", use_container_width=True):
            navigate_to("home")
    with nav_cols[1]:
        if st.button("➕ Novo Processo", use_container_width=True):
            st.session_state.edit_mode = False
            navigate_to("add_edit")
    with nav_cols[2]:
        if st.button("📦 Arquivados", use_container_width=True):
            navigate_to("archived")
    with nav_cols[3]:
        if st.button("💾 Backup", use_container_width=True):
            st.info("Função de backup disponível apenas na versão local.")
    with nav_cols[4]:
        if st.button("⚙️ Configurações", use_container_width=True):
            navigate_to("settings")
    with nav_cols[5]:
        if st.button("👥 Usuários", use_container_width=True):
            navigate_to("users")

elif st.session_state.user_role == "manager":
    # Gestor vê um conjunto limitado de opções
    nav_cols = st.columns(3)
    with nav_cols[0]:
        if st.button("📋 Painel", use_container_width=True):
            navigate_to("home")
    with nav_cols[1]:
        if st.button("➕ Novo Processo", use_container_width=True):
            st.session_state.edit_mode = False
            navigate_to("add_edit")
    with nav_cols[2]:
        if st.button("💾 Backup", use_container_width=True):
            st.info("Função de backup disponível apenas na versão local.")

else:
    # Cliente vê apenas o painel
    if st.button("📋 Painel", use_container_width=True):
        navigate_to("home")

st.divider()

# Mostrar aviso específico para Streamlit Cloud
st.warning("Esta é a versão para Streamlit Cloud. Algumas funcionalidades como backup e sincronização estão disponíveis apenas na versão local.")

# Display the current page
if st.session_state.current_page == "home":
    # Cliente só vê seus processos
    if st.session_state.user_role == 'client':
        display_home(navigate_to, filter_ids=st.session_state.client_processes)
    else:
        display_home(navigate_to)
elif st.session_state.current_page == "add_edit":
    # Somente admin e gestor podem adicionar/editar
    if st.session_state.user_role in ['admin', 'manager']:
        # Recarregar a lista de status do arquivo de configuração
        from components.settings import load_status_config, get_status_options
        status_config = load_status_config()
        # Carregar todos os status disponíveis
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
elif st.session_state.current_page == "settings":
    # Somente admin pode acessar configurações
    if st.session_state.user_role == 'admin':
        from components.settings import display_settings
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
        from components.archived import display_archived_processes
        display_archived_processes(navigate_to)
    else:
        st.error("Você não tem permissão para acessar esta página.")
        navigate_to("home")

# Footer
st.divider()
current_year = datetime.now().year
st.caption(f"© {current_year} JGR BROKER - Todos os direitos reservados")