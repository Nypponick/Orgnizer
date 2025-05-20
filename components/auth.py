import streamlit as st
import json
import os
import hashlib
from datetime import datetime, timedelta
import uuid

# Caminho para o arquivo de usuários
USERS_FILE = 'users.json'

def init_auth_state():
    """Inicializa o estado de autenticação na sessão"""
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    if 'user_id' not in st.session_state:
        st.session_state.user_id = None
    if 'user_role' not in st.session_state:
        st.session_state.user_role = None
    if 'user_name' not in st.session_state:
        st.session_state.user_name = None
    if 'user_email' not in st.session_state:
        st.session_state.user_email = None
    if 'client_processes' not in st.session_state:
        st.session_state.client_processes = []

def get_password_hash(password):
    """Criar hash seguro da senha"""
    # Temporário: Retorne a senha como texto puro para facilitar testes
    return password

def load_users():
    """Carregar usuários do arquivo"""
    if not os.path.exists(USERS_FILE):
        # Criar arquivo com usuário admin padrão se não existir
        admin_password = get_password_hash("admin123")
        default_users = {
            "users": [
                {
                    "id": "admin",
                    "name": "Administrador",
                    "email": "admin@jgr.com.br",
                    "password": admin_password,
                    "role": "admin",
                    "created_at": datetime.now().isoformat()
                }
            ]
        }
        with open(USERS_FILE, 'w') as f:
            json.dump(default_users, f, indent=4)
        return default_users
    
    with open(USERS_FILE, 'r') as f:
        return json.load(f)

def save_users(users_data):
    """Salvar usuários no arquivo"""
    with open(USERS_FILE, 'w') as f:
        json.dump(users_data, f, indent=4)

def authenticate(username, password):
    """Autenticar usuário"""
    users_data = load_users()
    
    for user in users_data.get('users', []):
        if (user['email'] == username or user['id'] == username) and user['password'] == password:
            st.session_state.authenticated = True
            st.session_state.user_id = user['id']
            st.session_state.user_role = user['role']
            st.session_state.user_name = user['name']
            st.session_state.user_email = user['email']
            
            # Se for cliente, carrega seus processos
            if user['role'] == 'client' and 'processes' in user:
                st.session_state.client_processes = user['processes']
            
            return True
    
    return False

def logout():
    """Fazer logout do usuário"""
    st.session_state.authenticated = False
    st.session_state.user_id = None
    st.session_state.user_role = None
    st.session_state.user_name = None
    st.session_state.user_email = None
    st.session_state.client_processes = []

def add_user(name, email, password, role='client', processes=None, logo_path=None):
    """Adicionar novo usuário"""
    users_data = load_users()
    
    # Verificar se email já existe
    for user in users_data.get('users', []):
        if user['email'] == email:
            return False, "Email já cadastrado"
    
    # Gerar ID único para o usuário
    user_id = str(uuid.uuid4())[:8]
    
    # Criar novo usuário
    new_user = {
        "id": user_id,
        "name": name,
        "email": email,
        "password": password,  # Em ambiente de produção, usaríamos get_password_hash(password)
        "role": role,
        "created_at": datetime.now().isoformat()
    }
    
    # Adicionar processos se for cliente
    if role == 'client' and processes:
        new_user['processes'] = processes
        
    # Adicionar logo se for cliente
    if logo_path:
        new_user['logo_path'] = logo_path
    
    # Adicionar à lista
    users_data['users'].append(new_user)
    save_users(users_data)
    
    return True, "Usuário adicionado com sucesso"

def update_user(user_id, name=None, email=None, password=None, role=None, processes=None, logo_path=None):
    """Atualizar usuário existente"""
    users_data = load_users()
    
    for i, user in enumerate(users_data.get('users', [])):
        if user['id'] == user_id:
            if name:
                users_data['users'][i]['name'] = name
            if email:
                users_data['users'][i]['email'] = email
            if password:
                users_data['users'][i]['password'] = password  # Em produção: get_password_hash(password)
            if role:
                users_data['users'][i]['role'] = role
            if processes is not None:  # Permitir lista vazia
                users_data['users'][i]['processes'] = processes
            if logo_path is not None:
                users_data['users'][i]['logo_path'] = logo_path
            
            users_data['users'][i]['updated_at'] = datetime.now().isoformat()
            save_users(users_data)
            return True, "Usuário atualizado com sucesso"
    
    return False, "Usuário não encontrado"

def delete_user(user_id):
    """Excluir usuário"""
    users_data = load_users()
    
    for i, user in enumerate(users_data.get('users', [])):
        if user['id'] == user_id:
            # Não permitir excluir o último admin
            if user['role'] == 'admin' and sum(1 for u in users_data.get('users', []) if u['role'] == 'admin') <= 1:
                return False, "Não é possível excluir o último administrador"
            
            users_data['users'].pop(i)
            save_users(users_data)
            return True, "Usuário excluído com sucesso"
    
    return False, "Usuário não encontrado"

def get_users():
    """Obter lista de usuários"""
    users_data = load_users()
    return users_data.get('users', [])

def assign_processes_to_client(user_id, process_ids):
    """Atribuir processos a um cliente"""
    users_data = load_users()
    
    for i, user in enumerate(users_data.get('users', [])):
        if user['id'] == user_id and user['role'] == 'client':
            users_data['users'][i]['processes'] = process_ids
            save_users(users_data)
            
            # Atualizar a sessão se for o usuário atual
            if st.session_state.user_id == user_id:
                st.session_state.client_processes = process_ids
                
            return True, "Processos atribuídos com sucesso"
    
    return False, "Usuário não encontrado ou não é cliente"

def get_client_for_process(process_id):
    """Obter cliente associado a um processo"""
    users_data = load_users()
    
    for user in users_data.get('users', []):
        if user['role'] == 'client' and 'processes' in user and process_id in user['processes']:
            return user
    
    return None

def display_login():
    """Exibir página de login"""
    st.header("Login")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        try:
            st.image("assets/images/jgr_logo.png", width=200)
        except:
            st.write("**JGR BROKER**")
    
    with col2:
        with st.form("login_form"):
            username = st.text_input("Email ou Usuário")
            password = st.text_input("Senha", type="password")
            submit = st.form_submit_button("Entrar", use_container_width=True)
            
            if submit:
                if authenticate(username, password):
                    st.success(f"Bem-vindo, {st.session_state.user_name}!")
                    st.rerun()
                else:
                    st.error("Usuário ou senha incorretos")

def display_user_management():
    """Exibir gerenciamento de usuários (apenas para admin)"""
    if st.session_state.user_role != 'admin':
        st.error("Acesso não autorizado")
        return
    
    st.header("Gerenciamento de Usuários")
    
    # Exibir lista de usuários
    users = get_users()
    
    # Opção para adicionar novo usuário
    st.subheader("Adicionar Novo Usuário")
    with st.form("add_user_form"):
        name = st.text_input("Nome")
        email = st.text_input("Email")
        password = st.text_input("Senha", type="password")
        role = st.selectbox("Tipo", options=["admin", "client"], format_func=lambda x: "Administrador" if x == "admin" else "Cliente")
        
        # Se for cliente, exibir opção para vincular processos e logo
        process_ids = []
        logo_path = None
        if role == 'client':
            from data import get_processes_df
            processes_df = get_processes_df()
            if not processes_df.empty:
                available_processes = processes_df['id'].tolist()
                process_ids = st.multiselect("Processos", options=available_processes)
            
            # Upload de logo do cliente
            st.write("Logo do Cliente (opcional)")
            logo_path = None  # Inicializar logo_path como None
            uploaded_logo = st.file_uploader("Enviar logo (PNG ou JPG)", type=["png", "jpg", "jpeg"], key="logo_uploader_add")
            if uploaded_logo is not None:
                # Criar diretório de logos se não existir
                # Usar import global do topo do arquivo
                logo_dir = os.path.join("assets", "client_logos")
                if not os.path.exists(logo_dir):
                    os.makedirs(logo_dir)
                
                # Salvar a imagem no diretório de logos
                logo_filename = f"logo_{datetime.now().strftime('%Y%m%d%H%M%S')}.png"
                logo_path = os.path.join(logo_dir, logo_filename)
                
                with open(logo_path, "wb") as f:
                    f.write(uploaded_logo.getbuffer())
                
                st.success(f"Logo carregada com sucesso!")
        
        col1, col2 = st.columns(2)
        with col1:
            submit = st.form_submit_button("Adicionar", use_container_width=True)
        
        with col2:
            cancel = st.form_submit_button("Cancelar", use_container_width=True)
    
    if submit and name and email and password:
        success, message = add_user(name, email, password, role, process_ids, logo_path)
        if success:
            st.success(message)
            st.rerun()
        else:
            st.error(message)
    
    # Exibir lista de usuários
    st.subheader("Usuários Cadastrados")
    if not users:
        st.info("Nenhum usuário cadastrado")
    else:
        col1, col2, col3, col4 = st.columns([2, 3, 2, 1])
        
        with col1:
            st.markdown("**Usuário**")
        
        with col2:
            st.markdown("**Email**")
        
        with col3:
            st.markdown("**Tipo**")
        
        with col4:
            st.markdown("**Ações**")
        
        st.divider()
        
        for user in users:
            col1, col2, col3, col4 = st.columns([2, 3, 2, 1])
            
            with col1:
                st.markdown(user['name'])
            
            with col2:
                st.markdown(user['email'])
            
            with col3:
                st.markdown("Administrador" if user['role'] == 'admin' else "Cliente")
            
            with col4:
                if st.button("Editar", key=f"edit_{user['id']}"):
                    st.session_state.edit_user_id = user['id']
                    st.rerun()
    
    # Formulário de edição de usuário
    if 'edit_user_id' in st.session_state and st.session_state.edit_user_id:
        user_to_edit = next((u for u in users if u['id'] == st.session_state.edit_user_id), None)
        
        if user_to_edit:
            st.subheader(f"Editar Usuário: {user_to_edit['name']}")
            
            with st.form("edit_user_form"):
                name = st.text_input("Nome", value=user_to_edit.get('name', ''))
                email = st.text_input("Email", value=user_to_edit.get('email', ''))
                password = st.text_input("Nova Senha (deixe em branco para manter a atual)", type="password")
                role = st.selectbox("Tipo", options=["admin", "client"], 
                                      index=0 if user_to_edit.get('role') == 'admin' else 1,
                                      format_func=lambda x: "Administrador" if x == "admin" else "Cliente")
                
                # Se for cliente, exibir opção para vincular processos e logo
                process_ids = user_to_edit.get('processes', [])
                logo_path = user_to_edit.get('logo_path')
                if role == 'client':
                    from data import get_processes_df
                    processes_df = get_processes_df()
                    if not processes_df.empty:
                        available_processes = processes_df['id'].tolist()
                        # Filtrar apenas os processos que ainda existem
                        default_processes = [p for p in process_ids if p in available_processes]
                        process_ids = st.multiselect("Processos", options=available_processes, default=default_processes)
                    
                    # Upload de logo do cliente
                    st.write("Logo do Cliente (opcional)")
                    # Usar import global no topo do arquivo em vez de importação local
                    if logo_path and os.path.exists(logo_path):
                        st.image(logo_path, width=150, caption="Logo atual")
                    
                    uploaded_logo = st.file_uploader("Alterar logo (PNG ou JPG)", type=["png", "jpg", "jpeg"], key="logo_uploader_edit")
                    if uploaded_logo is not None:
                        # Criar diretório de logos se não existir
                        logo_dir = os.path.join("assets", "client_logos")
                        if not os.path.exists(logo_dir):
                            os.makedirs(logo_dir)
                        
                        # Salvar a imagem no diretório de logos
                        logo_filename = f"logo_{datetime.now().strftime('%Y%m%d%H%M%S')}.png"
                        logo_path = os.path.join(logo_dir, logo_filename)
                        
                        with open(logo_path, "wb") as f:
                            f.write(uploaded_logo.getbuffer())
                        
                        st.success(f"Logo atualizada com sucesso!")
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    update_btn = st.form_submit_button("Atualizar", use_container_width=True)
                
                with col2:
                    delete_btn = st.form_submit_button("Excluir", use_container_width=True)
                
                with col3:
                    cancel_btn = st.form_submit_button("Cancelar", use_container_width=True)
            
            if update_btn and name and email:
                success, message = update_user(
                    st.session_state.edit_user_id, 
                    name=name, 
                    email=email, 
                    password=password if password else None,
                    role=role,
                    processes=process_ids if role == 'client' else [],
                    logo_path=logo_path if role == 'client' else None
                )
                
                if success:
                    st.success(message)
                    st.session_state.edit_user_id = None
                    st.rerun()
                else:
                    st.error(message)
            
            if delete_btn:
                success, message = delete_user(st.session_state.edit_user_id)
                
                if success:
                    st.success(message)
                    st.session_state.edit_user_id = None
                    st.rerun()
                else:
                    st.error(message)
            
            if cancel_btn:
                st.session_state.edit_user_id = None
                st.rerun()