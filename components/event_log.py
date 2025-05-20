import streamlit as st
import pandas as pd
from data import edit_event, delete_event

def display_event_log(process):
    """Display the event log for a process"""
    st.subheader("Histórico de Eventos")
    
    events = process.get("events", [])
    
    if not events:
        st.info("Nenhum evento registrado para este processo.")
        return
    
    # Convert events to dataframe for display
    events_df = pd.DataFrame(events)
    
    # Make sure columns exist
    if "date" not in events_df.columns:
        events_df["date"] = ""
    if "description" not in events_df.columns:
        events_df["description"] = ""
    if "user" not in events_df.columns:
        events_df["user"] = ""
    if "id" not in events_df.columns:
        events_df["id"] = ""
    
    # Filter events for client view - remover eventos de atribuição de cliente
    if 'user_role' in st.session_state and st.session_state.user_role == 'client':
        filtered_events = []
        for _, event in events_df.iterrows():
            # Excluir eventos relacionados à atribuição de processos
            desc = event['description'].lower() if isinstance(event['description'], str) else ""
            if "processo atribuído ao cliente" not in desc and "processo removido do cliente" not in desc:
                filtered_events.append(event)
        if filtered_events:
            events_df = pd.DataFrame(filtered_events)
        else:
            st.info("Nenhum evento registrado para este processo.")
            return
    
    # Sort events by date (most recent first)
    events_df = events_df.sort_values(by="date", ascending=False)
    
    # Inicializar estados para edição
    if 'editing_event' not in st.session_state:
        st.session_state.editing_event = None
    
    # Display events in a timeline format
    for i, event in events_df.iterrows():
        # Garantir que event_id nunca seja None/NaN/vazio
        if pd.isna(event.get('id')) or event.get('id', '') == '':
            event_id = f"event_{i}"  # Usar o índice como identificador único
        else:
            event_id = event.get('id', '')
            
        # Registrar IDs para debug
        print(f"Evento {i}: ID = '{event_id}'")
        
        with st.container():
            # Se o usuário for administrador e estiver no modo de edição para este evento
            if 'user_role' in st.session_state and st.session_state.user_role == 'admin' and st.session_state.editing_event == event_id:
                col1, col2, col3 = st.columns([1, 3, 1])
                
                with col1:
                    st.markdown(f"**{event['date']}**")
                    st.caption(f"Usuário: {event['user']}")
                
                with col2:
                    new_description = st.text_area(
                        "Editar descrição", 
                        value=event['description'],
                        key=f"edit_{event_id}"
                    )
                
                with col3:
                    if st.button("Salvar", key=f"save_{event_id}"):
                        if edit_event(process['id'], event_id, new_description):
                            st.success("Evento atualizado com sucesso!")
                            st.session_state.editing_event = None
                            st.rerun()
                        else:
                            st.error("Erro ao atualizar evento.")
                    
                    if st.button("Cancelar", key=f"cancel_{event_id}"):
                        st.session_state.editing_event = None
                        st.rerun()
            else:
                col1, col2, col3 = st.columns([1, 3, 1])
                
                with col1:
                    st.markdown(f"**{event['date']}**")
                    # Ocultar informações de usuário para cliente
                    if 'user_role' not in st.session_state or st.session_state.user_role == 'admin':
                        st.caption(f"Usuário: {event['user']}")
                
                with col2:
                    st.markdown(f"{event['description']}")
                
                # Mostrar opções de edição apenas para administradores
                if 'user_role' in st.session_state and st.session_state.user_role == 'admin':
                    with col3:
                        col3_1, col3_2 = st.columns(2)
                        
                        with col3_1:
                            if st.button("✏️", key=f"edit_btn_{event_id}"):
                                st.session_state.editing_event = event_id
                                st.rerun()
                        
                        with col3_2:
                            if st.button("🗑️", key=f"delete_btn_{event_id}"):
                                if delete_event(process['id'], event_id):
                                    st.success("Evento excluído com sucesso!")
                                    st.rerun()
                                else:
                                    st.error("Erro ao excluir evento.")
            
        st.divider()
