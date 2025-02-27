from utils.Import import import_csv
from utils.Disponibilidade import disponibilidade
from utils.Pareamento import criar_turmas, montar_dataframe_agendamentos
import streamlit as st

file_path = st.file_uploader("Selecione o arquivo CSV", type="csv")

if file_path is not None:
    disponibilidade_pessoas, nomes_unicos, segundas_chaves, max_pareamentos_individual, preferencia_turno, preferencia_frequencia, tipo_usuario = import_csv(file_path)

    st.title("Configuração do agendamento")

    # Obter os horários selecionados
    datas_disponiveis = list(disponibilidade_pessoas.keys())
    horarios_selecionados = disponibilidade(datas_disponiveis, segundas_chaves)

    if horarios_selecionados is not None:
        # Definir o número máximo de pessoas por turma
        max_pessoas_por_turma = st.number_input("Número máximo de pessoas por turma", min_value=1, value=20)

        # Definir o número máximo de turmas por horário
        max_turmas_por_horario = st.number_input("Número máximo de turmas por horário", min_value=1, value=1)

        # Definir a quantidade mínima de pessoas por turma
        min_pessoas_por_turma = st.number_input("Quantidade mínima de pessoas por turma", min_value=1, value=15)

        # Definir o número máximo de vezes que uma pessoa pode ser pareada em uma turma
        max_pareamentos_por_pessoa = st.number_input("Defina o número máximo de vezes que uma pessoa pode ser pareada: (Se definido como 0, será usada a quantidade de disponibilidades informadas pela pessoa; caso contrário, será utilizado o valor especificado abaixo.)", min_value=0, value=1)

        # Checkbox para usar preferencia_turno
        usar_preferencia_turno = st.checkbox("Usar preferência de turno")

        # Checkbox para usar preferencia_frequencia
        usar_preferencia_frequencia = st.checkbox("Usar preferência de frequência: (Não usar, ta dando um bug que não consegui arrumar a tempo)")

        for dia, horarios in horarios_selecionados.items():
            if dia in disponibilidade_pessoas:
                for horario in horarios:
                    if horario in disponibilidade_pessoas[dia]:
                        # Remove o horário do dia na disponibilidade_pessoas
                        del disponibilidade_pessoas[dia][horario]
                
                # Se o dia não tiver mais horários, pode remover o dia da disponibilidade
                if not disponibilidade_pessoas[dia]:
                    del disponibilidade_pessoas[dia]

        # Criar turmas
        print("Chamando criar_turmas...")
        turmas, jovens_nao_alocados, pessoas_disponiveis = criar_turmas(
            disponibilidade_pessoas, 
            max_pessoas_por_turma, 
            max_turmas_por_horario, 
            min_pessoas_por_turma, 
            max_pareamentos_por_pessoa, 
            max_pareamentos_individual, 
            preferencia_turno if usar_preferencia_turno else None, 
            preferencia_frequencia if usar_preferencia_frequencia else None,
            tipo_usuario
        )

        # Montar DataFrame com os agendamentos
        df_agendamentos = montar_dataframe_agendamentos(turmas, jovens_nao_alocados)
        
        # Calcular totais
        total_jovens = len(nomes_unicos)
        total_jovens_alocados = total_jovens - len(jovens_nao_alocados)
        total_jovens_nao_alocados = len(jovens_nao_alocados)
        total_turmas_agendadas = sum(len(turma) for turma in turmas.values())
        

        st.title("Turmas Criadas")

        # Exibir o DataFrame de agendamentos
        st.write(df_agendamentos)
        # Exibir totais
        st.write(f"Total de jovens: {total_jovens}")
        st.write(f"Total de jovens alocados: {total_jovens_alocados}")
        st.write(f"Total de jovens não alocados: {total_jovens_nao_alocados}")
        st.write(f"Total de turmas agendadas: {total_turmas_agendadas}")
        
    else:
        st.write("Nenhum horário selecionado.")
else:
    st.write("Aguardando seleção do arquivo")