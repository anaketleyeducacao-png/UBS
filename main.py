import streamlit as st
import pandas as pd
from datetime import datetime

# Configuração da página
st.set_page_config(page_title="Sistema de Fila Médica", layout="wide")

# Inicialização do estado da sessão para armazenar as filas
if 'prioritaria' not in st.session_state:
    st.session_state.prioritaria = []
if 'normal' not in st.session_state:
    st.session_state.normal = []
if 'historico' not in st.session_state:
    st.session_state.historico = []

def adicionar_paciente(nome, tipo):
    paciente = {
        "nome": nome,
        "chegada": datetime.now().strftime("%H:%M:%S"),
        "tipo": tipo
    }
    if tipo == "Prioritária":
        st.session_state.prioritaria.append(paciente)
    else:
        st.session_state.normal.append(paciente)
    st.success(f"Paciente {nome} adicionado à fila {tipo}!")

def chamar_proximo():
    if st.session_state.prioritaria:
        paciente = st.session_state.prioritaria.pop(0)
    elif st.session_state.normal:
        paciente = st.session_state.normal.pop(0)
    else:
        st.warning("Não há pacientes na fila!")
        return None
    
    paciente['atendimento'] = datetime.now().strftime("%H:%M:%S")
    st.session_state.historico.insert(0, paciente)
    return paciente

# Interface do Usuário
st.title("🏥 Sistema de Gestão de Fila Médica")

col1, col2 = st.columns([1, 2])

with col1:
    st.subheader("Registrar Novo Paciente")
    with st.form("registro_paciente", clear_on_submit=True):
        nome = st.text_input("Nome do Paciente")
        tipo = st.selectbox("Tipo de Atendimento", ["Normal", "Prioritária"])
        submit = st.form_submit_button("Adicionar à Fila")
        
        if submit and nome:
            adicionar_paciente(nome, tipo)
        elif submit and not nome:
            st.error("Por favor, insira o nome do paciente.")

    st.divider()
    st.subheader("Painel de Controle")
    if st.button("🔔 CHAMAR PRÓXIMO PACIENTE", use_container_width=True, type="primary"):
        proximo = chamar_proximo()
        if proximo:
            st.balloons()
            st.info(f"Chamando agora: **{proximo['nome']}** ({proximo['tipo']})")

with col2:
    tab1, tab2, tab3 = st.tabs(["📋 Filas Atuais", "✅ Histórico de Atendimento", "📊 Estatísticas"])
    
    with tab1:
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("### 🔴 Fila Prioritária")
            if st.session_state.prioritaria:
                df_prio = pd.DataFrame(st.session_state.prioritaria)
                st.table(df_prio)
            else:
                st.write("Fila vazia.")
        
        with c2:
            st.markdown("### 🔵 Fila Normal")
            if st.session_state.normal:
                df_norm = pd.DataFrame(st.session_state.normal)
                st.table(df_norm)
            else:
                st.write("Fila vazia.")

    with tab2:
        st.subheader("Últimos Atendimentos")
        if st.session_state.historico:
            st.table(pd.DataFrame(st.session_state.historico))
        else:
            st.write("Nenhum atendimento realizado ainda.")

    with tab3:
        st.subheader("Resumo do Dia")
        total_prio = len(st.session_state.prioritaria) + sum(1 for x in st.session_state.historico if x['tipo'] == 'Prioritária')
        total_norm = len(st.session_state.normal) + sum(1 for x in st.session_state.historico if x['tipo'] == 'Normal')
        
        m1, m2, m3 = st.columns(3)
        m1.metric("Total Prioritário", total_prio)
        m2.metric("Total Normal", total_norm)
        m3.metric("Aguardando", len(st.session_state.prioritaria) + len(st.session_state.normal))

st.sidebar.markdown("---")
st.sidebar.info("""
**Regra de Negócio:**
A fila prioritária tem precedência total sobre a fila normal. 
O sistema sempre chamará todos os prioritários antes de passar para a fila normal.
""")
