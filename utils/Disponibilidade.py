import pandas as pd
import streamlit as st

def disponibilidade(dias_da_semana):
    horarios = [f'{hora:02d}h - {hora+1:02d}h' for hora in range(8, 20)]
    
    disponibilidade_dict = {dia: horarios for dia in dias_da_semana}
    
    disponibilidade_df = pd.DataFrame.from_dict(disponibilidade_dict, orient='index').transpose()
    
    return disponibilidade_df

def selecionar_horarios(disponibilidade_df):
    selected_times = {}

    # Criar a matriz de checkboxes
    st.write("Horários disponíveis:")
    cols = st.columns(len(disponibilidade_df.columns) + 1)

    # Primeira linha com os dias da semana
    cols[0].write("Horários")
    for i, dia in enumerate(disponibilidade_df.columns):
        cols[i + 1].write(dia)

    # Preencher a matriz com checkboxes
    for i, horario in enumerate(disponibilidade_df.iloc[:, 0].dropna()):
        cols[0].write(horario)
        for j, dia in enumerate(disponibilidade_df.columns):
            if dia not in selected_times:
                selected_times[dia] = []
            if cols[j + 1].checkbox("", key=f"{dia}-{horario}"):
                selected_times[dia].append(horario)

    return selected_times