import streamlit as st
import pandas as pd
from datetime import datetime
from queue import PriorityQueue
import heapq

st.set_page_config(page_title="Sistema de Fila Médica", layout="wide")

# Inicializar fila com prioridade
if 'fila_pacientes' not in st.session_state:
    st.session_state.fila_pacientes = PriorityQueue()
if 'contador' not in st.session_state:
    st.session_state.contador = 0  # Para manter ordem de chegada
if 'historico' not in st.session_state:
    st.session_state.historico = []

def adicionar_paciente(nome, tipo):
    """Adiciona paciente à fila com prioridade"""
    
    # Prioridade: 0 = Prioritária, 1 = Normal
    prioridade = 0 if tipo == "Prioritária" else 1
    
    # Incrementa contador para manter ordem de chegada dentro da mesma prioridade
    st.session_state.contador += 1
    
    paciente = {
        "nome": nome,
        "chegada": datetime.now().strftime("%H:%M:%S"),
        "tipo": tipo
    }
    
    # Adiciona à fila: (prioridade, contador, paciente)
    st.session_state.fila_pacientes.put((prioridade, st.session_state.contador, paciente))
    
    st.success(f"Paciente {nome} adicionado à fila {tipo}!")

def chamar_proximo():
    """Remove e retorna o próximo paciente da fila"""
    
    if st.session_state.fila_pacientes.empty():
        st.warning("Não há pacientes na fila!")
        return None
    
    # Remove o primeiro da fila (automaticamente ordenado por prioridade)
    prioridade, contador, paciente = st.session_state.fila_pacientes.get()
    
    paciente['atendimento'] = datetime.now().strftime("%H:%M:%S")
    st.session_state.historico.insert(0, paciente)
    return paciente

def obter_lista_fila():
    """Converte PriorityQueue em lista para exibição"""
    # Cria uma cópia da fila sem removê-la
    items = []
    temp_queue = PriorityQueue()
    
    while not st.session_state.fila_pacientes.empty():
        item = st.session_state.fila_pacientes.get()
        items.append(item[2])  # Extrai o paciente (índice 2)
        temp_queue.put(item)
    
    # Restaura a fila original
    while not temp_queue.empty():
        st.session_state.fila_pacientes.put(temp_queue.get())
    
    return items

# Interface
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
    tab1, tab2, tab3 = st.tabs(["📋 Filas Atuais", "✅ Histórico", "📊 Estatísticas"])
    
    with tab1:
        lista_fila = obter_lista_fila()
        
        # Separa por tipo para exibição
        prio = [p for p in lista_fila if p['tipo'] == 'Prioritária']
        normal = [p for p in lista_fila if p['tipo'] == 'Normal']
        
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("### 🔴 Fila Prioritária")
            if prio:
                st.table(pd.DataFrame(prio))
            else:
                st.write("Fila vazia.")
        
        with c2:
            st.markdown("### 🔵 Fila Normal")
            if normal:
                st.table(pd.DataFrame(normal))
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
        lista_fila = obter_lista_fila()
        
        total_prio = len([p for p in lista_fila if p['tipo'] == 'Prioritária']) + \
                     sum(1 for x in st.session_state.historico if x['tipo'] == 'Prioritária')
        total_norm = len([p for p in lista_fila if p['tipo'] == 'Normal']) + \
                     sum(1 for x in st.session_state.historico if x['tipo'] == 'Normal')
        
        m1, m2, m3 = st.columns(3)
        m1.metric("Total Prioritário", total_prio)
        m2.metric("Total Normal", total_norm)
        m3.metric("Aguardando", len(lista_fila))

st.sidebar.markdown("---")
st.sidebar.info("""
**Regra de Negócio:**
A fila prioritária tem precedência total sobre a fila normal.
""")
