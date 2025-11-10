from utils.Import import import_csv
from utils.Disponibilidade import disponibilidade
from utils.Pareamento import criar_turmas, montar_dataframe_agendamentos
import streamlit as st

file_path = st.file_uploader("Selecione o arquivo CSV", type="csv")

if file_path is not None:
    disponibilidade_pessoas, nomes_unicos, segundas_chaves, max_pareamentos_individual, preferencia_turno, preferencia_frequencia, tipo_usuario = import_csv(file_path)

    st.title("Configuração do agendamento")

    # Obter os horários selecionados (checkboxes) — elas agora significam "BLOQUEAR este slot"
    datas_disponiveis = list(disponibilidade_pessoas.keys())
    horarios_selecionados = disponibilidade(datas_disponiveis, segundas_chaves)

    if horarios_selecionados is not None:
        # Definir o número máximo de pessoas por turma
        max_pessoas_por_turma = st.number_input("Número máximo de pessoas por turma", min_value=1, value=20)

        # Definir o número máximo de turmas por horário (global)
        max_turmas_por_horario = st.number_input("Número máximo de turmas por horário (global)", min_value=1, value=1)

        # Escolher modo de limite: Global ou Por horário
        modo_limite = st.radio("Modo de limite de turmas:", ("Global", "Por horário"))

        # -- NOVO: preparar cópia dos horários iniciais para permitir definir per-slot sempre --
        # Faz uma cópia dos slots existentes (antes de aplicar bloqueios)
        all_slots = {dia: list(horarios.keys()) for dia, horarios in disponibilidade_pessoas.items()}

        # Se modo "Por horário", permitir definir número de turmas por cada dia-horário (usa all_slots)
        per_slot_max = None
        if modo_limite == "Por horário":
            per_slot_max = {}
            st.markdown("Defina o número máximo de turmas por cada dia/horário:")
            for dia, horarios in all_slots.items():
                with st.expander(dia, expanded=False):
                    for horario in horarios:
                        key_name = f"slot_{dia}_{horario}"
                        per_slot_max[f"{dia} - {horario}"] = st.number_input(
                            f"{horario}", min_value=0, value=int(max_turmas_por_horario), key=key_name
                        )

        # Definir a quantidade mínima de pessoas por turma
        min_pessoas_por_turma = st.number_input("Quantidade mínima de pessoas por turma", min_value=1, value=15)

        # Definir o número máximo de vezes que uma pessoa pode ser pareada em uma turma
        max_pareamentos_por_pessoa = st.number_input("Defina o número máximo de vezes que uma pessoa pode ser pareada: (Se definido como 0, será usada a quantidade de disponibilidades informadas pela pessoa; caso contrário, será utilizado o valor especificado abaixo.)", min_value=0, value=1)

        # Checkbox para usar preferencia_turno
        usar_preferencia_turno = st.checkbox("Usar preferência de turno")

        # Checkbox para usar preferencia_frequencia
        usar_preferencia_frequencia = st.checkbox("Usar preferência de frequência")

        # Checkbox para usar tipo_usuario
        usar_tipo_usuario = st.checkbox("Usar tipo de usuário")

        # --- Aplicar BLOQUEIO: checboxes significam "não permitir agendamento" ---
        # horarios_selecionados agora é o mapeamento dia -> [horarios marcados] que serão bloqueados.
        bloqueados = horarios_selecionados  # nome semântico

        # Remover (bloquear) somente os slots marcados nas checkboxes
        for dia in list(disponibilidade_pessoas.keys()):
            # se dia tem bloqueios, aplica; caso contrário, mantém todos os horários
            bloqueios_do_dia = set(bloqueados.get(dia, []))
            if bloqueios_do_dia:
                for horario in list(disponibilidade_pessoas[dia].keys()):
                    if horario in bloqueios_do_dia:
                        del disponibilidade_pessoas[dia][horario]
                # Se o dia não tiver mais horários após o bloqueio, remover o dia
                if not disponibilidade_pessoas.get(dia):
                    del disponibilidade_pessoas[dia]

        # Criar turmas (passa per_slot_max; pode ser None)
        turmas, jovens_nao_alocados, pessoas_disponiveis = criar_turmas(
            disponibilidade_pessoas, 
            max_pessoas_por_turma, 
            max_turmas_por_horario, 
            min_pessoas_por_turma, 
            max_pareamentos_por_pessoa, 
            max_pareamentos_individual, 
            preferencia_turno if usar_preferencia_turno else None, 
            preferencia_frequencia if usar_preferencia_frequencia else None,
            tipo_usuario if usar_tipo_usuario else None,
            per_slot_max  # <-- novo argumento (pode ser None)
        )

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
        st.write(f"Total de turmas agendadas: {turmas.__len__()}")
        
    else:
        st.write("Nenhum horário selecionado.")
else:
    st.write("Aguardando seleção do arquivo")