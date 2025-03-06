from collections import defaultdict
import pandas as pd
from utils.Import import extrair_hora

def criar_turmas(disponibilidade_pessoas, max_pessoas_por_turma, max_turmas_por_horario, min_pessoas_por_turma, max_pareamentos_por_pessoa, max_pareamentos_individual, preferencia_turno, preferencia_frequencia, tipo_usuario):
    """
    Cria turmas a partir da disponibilidade, garantindo:
      - Cada turma tem pelo menos 3 Mentores e 1 Jovem-Semente Veterano/Time Administrativo Semear.
      - Cada pessoa não excede o limite de pareamentos.
      - Se definido, respeita a preferência de turno e frequência.
    """
    turmas = defaultdict(list)
    alocacoes = defaultdict(int)  # Número de pareamentos de cada pessoa
    nao_alocados = set()
    pessoas_disponiveis_global = set()
    
    print("Iniciando a criação de turmas...")

    # Para cada dia e horário, processa os participantes disponíveis
    for dia, horarios in disponibilidade_pessoas.items():
        for horario, pessoas in horarios.items():
            chave = f"{dia} - {horario}"
            pessoas_disponiveis_global.update(pessoas)
            
            # Filtrar os participantes que ainda não atingiram seu limite de pareamentos
            # e, se houver, que atendam à preferência de turno
            pessoas_filtradas = []
            for p in pessoas:
                limite = max_pareamentos_por_pessoa if max_pareamentos_por_pessoa != 0 else max_pareamentos_individual[p]
                if alocacoes[p] < limite:
                    if preferencia_turno:
                        # Considera o turno apenas se o preferido estiver presente no horário
                        if preferencia_turno.get(p) and preferencia_turno[p] in horario:
                            pessoas_filtradas.append(p)
                    else:
                        pessoas_filtradas.append(p)
            
            if tipo_usuario:
                # Separar os participantes filtrados por tipo
                mentores = [p for p in pessoas_filtradas if tipo_usuario[p] == "Mentor(a)"]
                veteranos = [p for p in pessoas_filtradas if tipo_usuario[p] in ["Jovem-Semente Veterano", "Time Administrativo Semear"]]
                outros = [p for p in pessoas_filtradas if tipo_usuario[p] not in ["Mentor(a)", "Jovem-Semente Veterano", "Time Administrativo Semear"]]
                
                # Ordenar cada grupo priorizando os com menos alocações
                mentores.sort(key=lambda p: alocacoes[p])
                veteranos.sort(key=lambda p: alocacoes[p])
                outros.sort(key=lambda p: alocacoes[p])
                
                # Enquanto for possível formar uma turma e não exceder o limite de turmas para o horário,
                # forma um grupo garantindo os critérios mínimos
                while len(mentores) >= 3 and len(veteranos) >= 1 and len(turmas[chave]) < max_turmas_por_horario:
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
                            print(f"Alocando {p} em {chave}")
                    else:
                        # Caso não seja possível formar uma turma com o mínimo exigido, interrompe tentativas para este horário
                        break
            else:
                # Se não usar tipo_usuario, apenas forma turmas com base na disponibilidade e limites
                while len(pessoas_filtradas) >= min_pessoas_por_turma and len(turmas[chave]) < max_turmas_por_horario:
                    grupo = pessoas_filtradas[:max_pessoas_por_turma]
                    pessoas_filtradas = pessoas_filtradas[max_pessoas_por_turma:]
                    turmas[chave].append(grupo)
                    for p in grupo:
                        alocacoes[p] += 1
                        print(f"Alocando {p} em {chave}")

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
                                if len(ultima_turma) < max_pessoas_por_turma:
                                    ultima_turma.append(pessoa)
                                    alocacoes[pessoa] += 1
                                    print(f"Adicionando {pessoa} à turma existente em {chave_proximo} para duas dinâmicas seguidas")
                                    continue
                            # Caso não haja turma ou a última esteja cheia, cria uma nova turma, se houver espaço
                            if len(turmas[chave_proximo]) < max_turmas_por_horario:
                                turmas[chave_proximo].append([pessoa])
                                alocacoes[pessoa] += 1
                                print(f"Criando nova turma para {pessoa} em {chave_proximo} para duas dinâmicas seguidas")
    
    # Identificar participantes que não foram alocados em nenhuma turma
    for pessoa in pessoas_disponiveis_global:
        if alocacoes[pessoa] == 0:
            nao_alocados.add(pessoa)
    
    print(f"Turmas formadas: {dict(turmas)}")
    print(f"Pessoas não alocadas: {nao_alocados}")
    
    return turmas, list(nao_alocados), list(pessoas_disponiveis_global)

def montar_dataframe_agendamentos(turmas, nao_alocados):
    """
    Cria um DataFrame dos agendamentos, organizando as turmas por horário/dia e listando os não alocados.
    """
    agendamentos_dict = defaultdict(list)
    for chave, lista_turmas in turmas.items():
        for turma in lista_turmas:
            agendamentos_dict[chave].extend(turma)
    
    # Define o comprimento máximo para alinhar as colunas
    max_len = max([len(val) for val in agendamentos_dict.values()] + [len(nao_alocados)])
    
    # Preenche cada coluna com None para que todas tenham o mesmo tamanho
    for chave in agendamentos_dict:
        agendamentos_dict[chave].extend([None] * (max_len - len(agendamentos_dict[chave])))
    
    df_agendamentos = pd.DataFrame({col: agendamentos_dict[col] for col in agendamentos_dict})
    df_agendamentos['Não Alocados'] = pd.Series(nao_alocados + [None] * (max_len - len(nao_alocados)))
    
    return df_agendamentos