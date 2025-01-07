from utils.Import import import_csv
from utils.Pareamento import criar_turmas, montar_dataframe_agendamentos
import streamlit as st

file_path = st.file_uploader("Selecione o arquivo CSV", type="csv")

if file_path is not None:
    disponibilidade_pessoas, nomes_unicos = import_csv(file_path)

    st.title("Configuração do agendamento")

    # Definir o número máximo de pessoas por turma
    max_pessoas_por_turma = st.number_input("Número máximo de pessoas por turma", min_value=1, value=20)

    # Definir o número máximo de turmas por horário
    max_turmas_por_horario = st.number_input("Número máximo de turmas por horário", min_value=1, value=1)

    # Definir a quantidade mínima de pessoas por turma
    min_pessoas_por_turma = st.number_input("Quantidade mínima de pessoas por turma", min_value=1, value=15)

    # Criar turmas
    turmas, jovens_nao_alocados = criar_turmas(disponibilidade_pessoas, max_pessoas_por_turma, max_turmas_por_horario, min_pessoas_por_turma)

    # Montar DataFrame com os agendamentos
    df_agendamentos = montar_dataframe_agendamentos(turmas, jovens_nao_alocados)
    
    # Calcular totais
    total_jovens = len(nomes_unicos)
    total_jovens_alocados = total_jovens - len(jovens_nao_alocados)
    total_jovens_nao_alocados = len(jovens_nao_alocados)

    st.title("Turmas Criadas")

    # Exibir o DataFrame de agendamentos
    st.write(df_agendamentos)

    # Exibir totais
    st.write(f"Total de jovens: {total_jovens}")
    st.write(f"Total de jovens alocados: {total_jovens_alocados}")
    st.write(f"Total de jovens não alocados: {total_jovens_nao_alocados}")
else:
    st.write("Aguardando seleção do arquivo")