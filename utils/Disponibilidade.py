import pandas as pd
import streamlit as st

def disponibilidade(datas_disponiveis, horarios):
    selected_times = {data: [] for data in datas_disponiveis}  # Inicializa com listas vazias
    dias = datas_disponiveis
    dias_selecionados = st.multiselect("Selecione os dias disponíveis:", dias, default=dias)
    
    if not dias_selecionados:
        st.warning("Selecione pelo menos um dia.")
        return None

    # Criar a matriz de checkboxes
    st.write("Horários disponíveis:")

    # Ajuste para usar toda a largura disponível
    cols = st.columns(len(dias_selecionados) + 1, gap="small")

    # Primeira linha com as datas
    cols[0].write("horas")
    for i, data in enumerate(dias_selecionados):
        cols[i + 1].write(data)

    # Preencher a matriz com checkboxes
    for i, horario in enumerate(horarios):
        # Exibir apenas a primeira hora para o usuário
        primeira_hora = horario.split(' - ')[0]
        cols[0].write(primeira_hora)
        for j, data in enumerate(dias_selecionados):
            if cols[j + 1].checkbox("", key=f"{data}-{horario}"):
                selected_times[data].append(horario)

    return selected_times