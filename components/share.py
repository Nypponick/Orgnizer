import streamlit as st
import pandas as pd
import uuid
import json
import os
from datetime import datetime, timedelta
import base64

from data import get_process_by_id, get_processes_df, save_data
from utils import send_email, send_sms

# Path to store share links
SHARE_FILE = "shared_links.json"

def load_shared_links():
    """Load shared links from file"""
    if os.path.exists(SHARE_FILE):
        try:
            with open(SHARE_FILE, "r") as f:
                return json.load(f)
        except:
            return {"links": []}
    return {"links": []}

def save_shared_links(links_data):
    """Save shared links to file"""
    with open(SHARE_FILE, "w") as f:
        json.dump(links_data, f, indent=4)

def generate_share_link(process_id, expiry_days=30):
    """Generate a unique share link for a process"""
    # Create a unique token
    token = str(uuid.uuid4())
    
    # Calculate expiry date
    expiry_date = (datetime.now() + timedelta(days=expiry_days)).strftime("%Y-%m-%d")
    
    # Load existing links
    links_data = load_shared_links()
    
    # Add new link
    links_data["links"].append({
        "token": token,
        "process_id": process_id,
        "created_date": datetime.now().strftime("%Y-%m-%d"),
        "expiry_date": expiry_date,
        "is_active": True
    })
    
    # Save links
    save_shared_links(links_data)
    
    # Return the token
    return token

def validate_share_token(token):
    """Validate a share token and return the process ID if valid"""
    links_data = load_shared_links()
    
    for link in links_data["links"]:
        if link["token"] == token and link["is_active"]:
            # Check if expired
            expiry_date = datetime.strptime(link["expiry_date"], "%Y-%m-%d")
            if expiry_date >= datetime.now():
                return link["process_id"]
    
    return None

def revoke_share_link(token):
    """Revoke a share link"""
    links_data = load_shared_links()
    
    for link in links_data["links"]:
        if link["token"] == token:
            link["is_active"] = False
            save_shared_links(links_data)
            return True
    
    return False

def get_active_links():
    """Get all active share links"""
    links_data = load_shared_links()
    active_links = [link for link in links_data["links"] if link["is_active"]]
    
    # Add process information
    for link in active_links:
        process = get_process_by_id(link["process_id"])
        if process:
            link["process_ref"] = process.get("ref", "")
            link["process_invoice"] = process.get("invoice", "")
    
    return active_links

def display_share_interface():
    """Display the interface for sharing processes"""
    st.header("Compartilhar Processos com Clientes")
    
    # Get processes
    df = get_processes_df()
    if df.empty:
        st.info("Nenhum processo disponível para compartilhar.")
        return
    
    # Show existing shares
    active_links = get_active_links()
    
    if active_links:
        st.subheader("Links Ativos")
        
        # Create a dataframe of active links
        links_df = pd.DataFrame(active_links)
        links_df = links_df.rename(columns={
            "token": "Token",
            "process_id": "ID do Processo",
            "process_ref": "Referência",
            "process_invoice": "Invoice",
            "created_date": "Data de Criação",
            "expiry_date": "Data de Expiração"
        })
        
        if "is_active" in links_df.columns:
            links_df = links_df.drop(columns=["is_active"])
        
        st.dataframe(links_df)
        
        # Revoke link option
        revoke_token = st.selectbox("Selecione um token para revogar", 
                                 options=[link["token"] for link in active_links])
        
        if st.button("Revogar Link"):
            if revoke_share_link(revoke_token):
                st.success("Link revogado com sucesso!")
                st.rerun()
            else:
                st.error("Erro ao revogar link!")
    
    # Create new share links
    st.subheader("Criar Novo Link de Compartilhamento")
    
    col1, col2 = st.columns(2)
    
    with col1:
        process_id = st.selectbox("Selecione um processo para compartilhar", 
                               options=df["id"].tolist())
    
    with col2:
        expiry_days = st.number_input("Número de dias de validade", 
                                   min_value=1, max_value=365, value=30)
    
    if st.button("Gerar Link de Compartilhamento"):
        token = generate_share_link(process_id, expiry_days)
        
        # Create shareable URL
        base_url = st.text_input("URL da aplicação (com https://)", value="https://meu-sistema-importacao.replit.app")
        share_url = f"{base_url}/client?token={token}"
        
        st.success("Link gerado com sucesso!")
        st.code(share_url, language="text")
        
        # Options to share via email or SMS
        st.subheader("Enviar Link para Cliente")
        
        tab1, tab2 = st.tabs(["Email", "SMS"])
        
        with tab1:
            email = st.text_input("Email do cliente")
            subject = st.text_input("Assunto", value=f"Atualização sobre seu processo de importação {process_id}")
            
            process = get_process_by_id(process_id)
            default_message = f"""
Prezado Cliente,

Atualizamos as informações do seu processo de importação {process_id}.
Você pode acompanhar o status do seu processo no link abaixo:

{share_url}

Este link é válido por {expiry_days} dias.

Atenciosamente,
Equipe de Importação
            """
            
            message = st.text_area("Mensagem", value=default_message, height=200)
            
            if st.button("Enviar por Email"):
                if email and subject and message:
                    result = send_email(email, subject, message)
                    if result:
                        st.success("Email enviado com sucesso!")
                    else:
                        st.error("Falha ao enviar email. Verifique as configurações.")
                else:
                    st.warning("Preencha todos os campos obrigatórios.")
        
        with tab2:
            phone = st.text_input("Número de telefone do cliente (com código do país, ex: +5511912345678)")
            
            default_sms = f"Processo de importação {process_id} atualizado. Acesse: {share_url}"
            sms_message = st.text_area("Mensagem SMS (máx. 160 caracteres)", 
                                    value=default_sms, 
                                    max_chars=160, 
                                    height=100)
            
            if st.button("Enviar por SMS"):
                if phone and sms_message:
                    result = send_sms(phone, sms_message)
                    if result:
                        st.success("SMS enviado com sucesso!")
                    else:
                        st.error("Falha ao enviar SMS. Verifique as configurações e se o serviço Twilio está configurado.")
                else:
                    st.warning("Preencha todos os campos obrigatórios.")