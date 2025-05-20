import pandas as pd
import streamlit as st
from datetime import datetime
import io
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os

# Importação condicional do Twilio para evitar erros de dependência
try:
    from twilio.rest import Client
    TWILIO_AVAILABLE = True
except ImportError:
    TWILIO_AVAILABLE = False

def format_date(date_str):
    """Format date string to DD/MM/YYYY"""
    if pd.isna(date_str) or date_str == "":
        return ""
    try:
        date_obj = pd.to_datetime(date_str, dayfirst=True)
        return date_obj.strftime("%d/%m/%Y")
    except:
        return date_str

def calculate_free_time_expiry(eta_date, free_time_days):
    """Calculate free time expiry date based on ETA and free time days"""
    if pd.isna(eta_date) or eta_date == "" or not free_time_days:
        return ""
    try:
        eta_obj = pd.to_datetime(eta_date, dayfirst=True)
        days = int(free_time_days)
        expiry_date = eta_obj + pd.Timedelta(days=days)
        return expiry_date.strftime("%d/%m/%Y")
    except:
        return ""

def calculate_period_expiry(start_date, days_per_period):
    """Calculate period expiry date based on start date and days per period"""
    if pd.isna(start_date) or start_date == "" or not days_per_period:
        return ""
    try:
        start_obj = pd.to_datetime(start_date, dayfirst=True)
        days = int(days_per_period)
        expiry_date = start_obj + pd.Timedelta(days=days)
        return expiry_date.strftime("%d/%m/%Y")
    except:
        return ""

def calculate_storage_days(entry_date):
    """Calculate storage days from entry date to today"""
    if pd.isna(entry_date) or entry_date == "":
        return 0  # Retorna número inteiro
    try:
        entry_obj = pd.to_datetime(entry_date, dayfirst=True)
        today = pd.to_datetime(datetime.now().date())
        days = (today - entry_obj).days
        return max(0, days)  # Retorna número inteiro, não string
    except:
        return 0  # Retorna número inteiro

def check_period_expiry(process):
    """
    Verifica se o período atual de armazenagem expirou e precisa ser atualizado.
    Lida com múltiplos períodos expirados, atualizando até a data mais recente.
    
    Args:
        process: Dicionário com informações do processo
        
    Returns:
        tuple: (precisa_atualizar, novo_inicio, novo_vencimento)
    """
    # Verificar se temos as datas necessárias
    period_expiry = process.get("current_period_expiry", "")
    period_start = process.get("current_period_start", "")
    
    if pd.isna(period_expiry) or period_expiry == "":
        return False, None, None
    
    try:
        # Converter para objetos datetime
        expiry_date = pd.to_datetime(period_expiry, dayfirst=True)
        today = pd.to_datetime(datetime.now().date())
        
        # Determinar os dias por período (padrão: 30 dias)
        days_per_period = 30  # Valor padrão
        
        try:
            # Tentar obter o valor configurado
            from streamlit import session_state
            if "data" in session_state and "config" in session_state.data:
                days_per_period = session_state.data["config"].get("storage_days_per_period", 30)
        except:
            pass
        
        # Verificar se a data de vencimento já passou
        if expiry_date < today:
            # Se já passou, precisamos verificar quantos períodos passaram
            # para calcular a data atual correta
            
            # Número máximo de períodos a avançar para evitar loop infinito
            max_periods = 24  # Limite para 2 anos
            current_expiry = expiry_date
            current_start = pd.to_datetime(period_start, dayfirst=True) if period_start else None
            
            # Avançar períodos até chegar à data atual
            for _ in range(max_periods):
                # O novo início do período é o dia seguinte ao vencimento anterior
                new_start_date = current_expiry + pd.Timedelta(days=1)
                
                # Calcular o novo vencimento
                new_expiry_date = new_start_date + pd.Timedelta(days=days_per_period-1)
                
                # Se o novo vencimento ainda é passado, continuar avançando
                if new_expiry_date < today:
                    current_start = new_start_date
                    current_expiry = new_expiry_date
                    continue
                
                # Encontramos o período atual
                return True, new_start_date.strftime("%d/%m/%Y"), new_expiry_date.strftime("%d/%m/%Y")
            
            # Se chegarmos aqui, significa que atingimos o limite de períodos
            # Usaremos o último período calculado
            return True, current_start.strftime("%d/%m/%Y"), current_expiry.strftime("%d/%m/%Y")
        
        # Se não passou, não precisamos atualizar
        return False, None, None
    except Exception as e:
        print(f"Erro ao verificar vencimento do período: {e}")
        return False, None, None

def update_period_dates(process):
    """
    Atualiza as datas de início e vencimento do período atual se necessário.
    
    Args:
        process: Dicionário com informações do processo
        
    Returns:
        bool: True se houve atualização, False caso contrário
    """
    # Verificar se o período expirou
    needs_update, new_start, new_expiry = check_period_expiry(process)
    
    if needs_update and new_start and new_expiry:
        # Atualizar as datas no processo
        process["current_period_start"] = new_start
        process["current_period_expiry"] = new_expiry
        
        # Adicionar evento registrando a atualização
        event_description = f"Período atualizado automaticamente: início {new_start}, vencimento {new_expiry}"
        
        try:
            from data import add_event
            add_event(process["id"], event_description)
        except Exception as e:
            print(f"Erro ao adicionar evento de atualização de período: {e}")
        
        return True
    
    return False

def get_status_color(status):
    """Get color for status indicator"""
    status_colors = {
        # Status básicos
        "Em andamento": "orange",
        "Concluído": "green",
        "Atrasado": "red",
        "Pendente": "blue",
        "Cancelado": "gray",
        
        # Status de importação adicionais
        "Novo Processo": "#6a0dad",  # Roxo
        "Navio em Santos": "#4169e1",  # Azul royal
        "Chegando no porto de Santos": "#2e8b57",  # Verde mar
        "Chegada do navio alterada": "#ff4500",  # Laranja avermelhado
        "Trânsito Aduaneiro": "#8b4513",  # Marrom
        "Em rota de trânsito aduaneiro": "#8b4513",  # Marrom
        "Presença de carga em Bauru": "#20b2aa",  # Verde azulado
        "Entrega programada": "#228b22"  # Verde floresta
    }
    return status_colors.get(status, "orange")

def export_to_excel(df):
    """Export dataframe to Excel"""
    output = io.BytesIO()
    
    # This avoids the LSP error by explicitly specifying the engine
    writer = pd.ExcelWriter(output, engine='xlsxwriter')
    
    df.to_excel(writer, index=False, sheet_name='Processos')
    
    # Get the xlsxwriter workbook and worksheet objects
    workbook = writer.book
    worksheet = writer.sheets['Processos']
    
    # Add some formatting
    header_format = workbook.add_format({
        'bold': True,
        'text_wrap': True,
        'valign': 'top',
        'fg_color': '#D7E4BC',
        'border': 1
    })
    
    # Write the column headers with the defined format
    for col_num, value in enumerate(df.columns.values):
        worksheet.write(0, col_num, value, header_format)
        
    # Set column widths
    for i, col in enumerate(df.columns):
        worksheet.set_column(i, i, 15)
    
    writer.close()
    return output.getvalue()

def export_to_csv(df):
    """Export dataframe to CSV"""
    return df.to_csv(index=False).encode('utf-8')

def get_status_from_dates(date_str, expected_date_str):
    """Determine status based on dates"""
    if pd.isna(date_str) or date_str == "":
        return "Pendente"
    
    try:
        date = pd.to_datetime(date_str)
        today = pd.to_datetime(datetime.now().date())
        
        if date < today:
            return "Concluído"
        
        if expected_date_str and pd.to_datetime(expected_date_str) < today:
            return "Atrasado"
            
        return "Em andamento"
    except:
        return "Pendente"

def send_email(to_email, subject, message):
    """Send an email using SMTP"""
    # Note: For this to work, you need to set SMTP configuration
    # For Gmail, you might need an app-specific password
    try:
        # Try to get configurations from session state or environment variables
        smtp_server = st.session_state.get('smtp_server', os.environ.get('SMTP_SERVER', ''))
        smtp_port = int(st.session_state.get('smtp_port', os.environ.get('SMTP_PORT', 587)))
        smtp_username = st.session_state.get('smtp_username', os.environ.get('SMTP_USERNAME', ''))
        smtp_password = st.session_state.get('smtp_password', os.environ.get('SMTP_PASSWORD', ''))
        from_email = st.session_state.get('from_email', os.environ.get('FROM_EMAIL', smtp_username))
        
        # If configuration is incomplete, show a configuration form
        if not smtp_server or not smtp_username or not smtp_password:
            st.warning("Configuração de email incompleta. Configure nas configurações.")
            return False
        
        # Create message
        msg = MIMEMultipart()
        msg['From'] = from_email
        msg['To'] = to_email
        msg['Subject'] = subject
        msg.attach(MIMEText(message, 'plain'))
        
        # Connect to server and send
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(smtp_username, smtp_password)
        server.send_message(msg)
        server.quit()
        
        return True
    except Exception as e:
        st.error(f"Erro ao enviar email: {e}")
        return False

def send_sms(to_phone, message):
    """Send SMS via Twilio"""
    if not TWILIO_AVAILABLE:
        st.warning("Twilio não está disponível. A funcionalidade de SMS está desativada.")
        return False
        
    try:
        # Get Twilio credentials
        account_sid = os.environ.get('TWILIO_ACCOUNT_SID')
        auth_token = os.environ.get('TWILIO_AUTH_TOKEN')
        from_phone = os.environ.get('TWILIO_PHONE_NUMBER')
        
        # Check if credentials are available
        if not account_sid or not auth_token or not from_phone:
            st.warning("Configuração do Twilio incompleta. Configure nas configurações.")
            return False
        
        # Initialize Twilio client
        client = Client(account_sid, auth_token)
        
        # Send message
        message = client.messages.create(
            body=message,
            from_=from_phone,
            to=to_phone
        )
        
        return True
    except Exception as e:
        st.error(f"Erro ao enviar SMS: {e}")
        return False
