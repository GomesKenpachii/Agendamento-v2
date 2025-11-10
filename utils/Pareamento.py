from collections import defaultdict
import pandas as pd
from utils.Import import extrair_hora

def criar_turmas(disponibilidade_pessoas, max_pessoas_por_turma, max_turmas_por_horario, min_pessoas_por_turma, max_pareamentos_por_pessoa, max_pareamentos_individual=None, preferencia_turno=None, preferencia_frequencia=None, tipo_usuario=None, per_slot_max=None):
    """
    Cria turmas a partir da disponibilidade, garantindo:
      - Cada turma tem pelo menos 3 Mentores e 1 Jovem-Semente Veterano/Time Administrativo Semear.
      - Cada pessoa não excede o limite de pareamentos.
      - Se definido, respeita a preferência de turno e frequência.

    per_slot_max: dict opcional com chaves "Dia - Horario" -> int (limite de turmas para esse slot).
    Se per_slot_max for None ou não contiver a chave, usa max_turmas_por_horario (global).
    """
    turmas = defaultdict(list)
    alocacoes = defaultdict(int)  # Número de pareamentos de cada pessoa
    nao_alocados = set()
    pessoas_disponiveis_global = set()
    
    # Para cada dia e horário, processa os participantes disponíveis
    for dia, horarios in disponibilidade_pessoas.items():
        for horario, pessoas in horarios.items():
            chave = f"{dia} - {horario}"
            pessoas_disponiveis_global.update(pessoas)
            
            # Determina limite de turmas para este slot (usa per_slot_max se fornecido)
            slot_limite = None
            if per_slot_max and chave in per_slot_max:
                # permitir 0 para indicar "nenhuma turma" nesse slot
                try:
                    slot_limite = int(per_slot_max.get(chave, max_turmas_por_horario))
                except Exception:
                    slot_limite = max_turmas_por_horario
            else:
                slot_limite = max_turmas_por_horario

            # Filtrar os participantes que ainda não atingiram seu limite de pareamentos
            pessoas_filtradas = []
            for p in pessoas:
                limite_individual = max_pareamentos_por_pessoa if max_pareamentos_por_pessoa != 0 else (max_pareamentos_individual.get(p, 0) if max_pareamentos_individual else 0)
                if alocacoes[p] < limite_individual:
                    # Se houver pref de turno, considerar apenas se o horário contém a string da preferência
                    if preferencia_turno:
                        pref = preferencia_turno.get(p)
                        if not pref or pref in horario:
                            pessoas_filtradas.append(p)
                    else:
                        pessoas_filtradas.append(p)
            
            if tipo_usuario:
                # Separar os participantes filtrados por tipo
                mentores = [p for p in pessoas_filtradas if tipo_usuario.get(p) == "Mentor(a)"]
                veteranos = [p for p in pessoas_filtradas if tipo_usuario.get(p) in ["Jovem-Semente Veterano", "Time Administrativo Semear"]]
                outros = [p for p in pessoas_filtradas if tipo_usuario.get(p) not in ["Mentor(a)", "Jovem-Semente Veterano", "Time Administrativo Semear"]]
                
                # Ordenar cada grupo priorizando os com menos alocações
                mentores.sort(key=lambda p: alocacoes[p])
                veteranos.sort(key=lambda p: alocacoes[p])
                outros.sort(key=lambda p: alocacoes[p])
                
                # Enquanto for possível formar uma turma e não exceder o limite de turmas para o horário (slot_limite),
                # forma um grupo garantindo os critérios mínimos
                while len(mentores) >= 3 and len(veteranos) >= 1 and len(turmas[chave]) < slot_limite:
                    grupo = []
                    # Retira 3 mentores (sempre verificando o limite de pessoas)
                    for _ in range(3):
                        if len(grupo) < max_pessoas_por_turma and mentores:
                            grupo.append(mentores.pop(0))
                    
                    # Retira 1 veterano, se houver espaço
                    if len(grupo) < max_pessoas_por_turma and veteranos:
                        grupo.append(veteranos.pop(0))
                    
                    # Preenche a turma até o limite máximo, priorizando: mentores, veteranos e, por fim, outros
                    while len(grupo) < max_pessoas_por_turma:
                        if outros:   
                            grupo.append(outros.pop(0))
                        elif veteranos:
                            grupo.append(veteranos.pop(0))
                        elif mentores:
                            grupo.append(mentores.pop(0))
                        else:
                            break
                    
                    # Se a turma atingir o tamanho mínimo exigido, a adiciona e atualiza as alocações
                    if len(grupo) >= min_pessoas_por_turma:
                        turmas[chave].append(grupo)
                        for p in grupo:
                            alocacoes[p] += 1
                    else:
                        # Caso não seja possível formar uma turma com o mínimo exigido, interrompe tentativas para este horário
                        break
            else:
                # Se não usar tipo_usuario, apenas forma turmas com base na disponibilidade e limites
                while len(pessoas_filtradas) >= min_pessoas_por_turma and len(turmas[chave]) < slot_limite:
                    grupo = pessoas_filtradas[:max_pessoas_por_turma]
                    pessoas_filtradas = pessoas_filtradas[max_pessoas_por_turma:]
                    turmas[chave].append(grupo)
                    for p in grupo:
                        alocacoes[p] += 1

    # Alocação para "Duas dinâmicas seguidas no mesmo dia"
    if preferencia_frequencia:
        for dia, horarios in disponibilidade_pessoas.items():
            # Ordena os horários do dia (supondo formato "HH:MM")
            horarios_ordenados = sorted(horarios.keys(), key=extrair_hora)
            for idx, horario in enumerate(horarios_ordenados):
                proximo_horario = horarios_ordenados[idx + 1] if idx + 1 < len(horarios_ordenados) else None
                if not proximo_horario:
                    continue
                chave_proximo = f"{dia} - {proximo_horario}"
                # Para cada pessoa com preferência por duas dinâmicas seguidas,
                # tenta alocá-la no próximo horário se ela estiver disponível
                for pessoa in horarios[horario]:
                    if preferencia_frequencia.get(pessoa) == "Duas dinâmicas seguidas no mesmo dia" and alocacoes[pessoa] > 0:
                        if pessoa in disponibilidade_pessoas[dia].get(proximo_horario, []):
                            # Tenta adicionar à última turma do próximo horário, se não estiver cheia
                            if turmas[chave_proximo]:
                                ultima_turma = turmas[chave_proximo][-1]
                                if len(ultima_turma) < (per_slot_max.get(chave_proximo, max_turmas_por_horario) if per_slot_max else max_turmas_por_horario):
                                    if len(ultima_turma) < max_pessoas_por_turma:
                                        ultima_turma.append(pessoa)
                                        alocacoes[pessoa] += 1
                                        continue
                            # Caso não haja turma ou a última esteja cheia, cria uma nova turma, se houver espaço
                            if len(turmas[chave_proximo]) < (per_slot_max.get(chave_proximo, max_turmas_por_horario) if per_slot_max else max_turmas_por_horario):
                                turmas[chave_proximo].append([pessoa])
                                alocacoes[pessoa] += 1

    # Identificar participantes que não foram alocados em nenhuma turma
    for pessoa in pessoas_disponiveis_global:
        if alocacoes[pessoa] == 0:
            nao_alocados.add(pessoa)
    
    return turmas, list(nao_alocados), list(pessoas_disponiveis_global)

def montar_dataframe_agendamentos(turmas, nao_alocados):
    """
    Retorna um DataFrame 'long' com colunas:
      - Nome
      - Dia
      - Horario

    Cada linha representa uma alocação (uma pessoa em um dia/horário).
    Pessoas não alocadas aparecem com Dia e Horario = None.
    """
    rows = []
    for chave, lista_turmas in turmas.items():
        # chave esperada no formato "Dia - Horario"
        if ' - ' in chave:
            dia, horario = chave.split(' - ', 1)
            dia = dia.strip()
            horario = horario.strip()
        else:
            # fallback caso o formato seja diferente
            dia = chave
            horario = None

        for turma in lista_turmas:
            for pessoa in turma:
                rows.append({'Nome': pessoa, 'Dia': dia, 'Horario': horario})

    # adicionar não alocados como linhas com Dia/Horario vazios
    for pessoa in nao_alocados:
        rows.append({'Nome': pessoa, 'Dia': None, 'Horario': None})

    df = pd.DataFrame(rows, columns=['Nome', 'Dia', 'Horario'])

    # opcional: ordenar por Dia, Horario, Nome (descomentar se quiser)
    # df = df.sort_values(by=['Dia', 'Horario', 'Nome'], na_position='last').reset_index(drop=True)

    return df