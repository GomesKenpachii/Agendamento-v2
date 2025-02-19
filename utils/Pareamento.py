from collections import defaultdict
import pandas as pd

def criar_turmas(disponibilidade_pessoas, max_pessoas_por_turma, max_turmas_por_horario, min_pessoas_por_turma, max_pareamentos_por_pessoa, max_pareamentos_individual):
    turmas = defaultdict(list)
    jovens_alocados = defaultdict(int)  # Track the number of times each person is allocated
    jovens_nao_alocados = set()
    pessoas_disponiveis = set()
    
    print("Iniciando a criação de turmas...")
    
    # Ordenar pessoas por disponibilidade (menos disponíveis primeiro)
    disponibilidade_ordenada = sorted(disponibilidade_pessoas.items(), key=lambda x: len(x[1]))
    print(f"Disponibilidade ordenada: {disponibilidade_ordenada}")
    
    for dia, horarios in disponibilidade_ordenada:
        print(f"Processando dia: {dia}")
        for horario, pessoas in horarios.items():
            print(f"Processando horário: {horario} com pessoas: {pessoas}")
            # Combine the lists, prioritizing non-allocated people and then by availability
            pessoas_disponiveis.update(pessoas)
            pessoas_disponiveis_ordenadas = sorted(pessoas, key=lambda p: (jovens_alocados[p], sum(len(disponibilidade_pessoas[d][h]) for d in disponibilidade_pessoas for h in disponibilidade_pessoas[d] if p in disponibilidade_pessoas[d][h])))
            
            for i in range(0, len(pessoas_disponiveis_ordenadas), max_pessoas_por_turma):
                if len(turmas[f"{dia} - {horario}"]) >= max_turmas_por_horario:
                    break
                turma = [pessoa for pessoa in pessoas_disponiveis_ordenadas[i:i + max_pessoas_por_turma] if jovens_alocados[pessoa] < (max_pareamentos_individual[pessoa] if max_pareamentos_por_pessoa == 1000 else max_pareamentos_por_pessoa)]
                if len(turma) >= min_pessoas_por_turma:
                    turmas[f"{dia} - {horario}"].append(turma)
                    for pessoa in turma:
                        jovens_alocados[pessoa] += 1
                        print(f"Alocando {pessoa} em {dia} - {horario}")
    
    # Identificar jovens não alocados
    for pessoa in pessoas_disponiveis:
        if jovens_alocados[pessoa] == 0:
            jovens_nao_alocados.add(pessoa)
    
    print(f"Turmas: {turmas}")
    print(f"Jovens não alocados: {jovens_nao_alocados}")
    print(f"Pessoas disponíveis: {pessoas_disponiveis}")
    
    return turmas, list(jovens_nao_alocados), list(pessoas_disponiveis)

def montar_dataframe_agendamentos(turmas, jovens_nao_alocados):
    # Criar um DataFrame com os agendamentos
    agendamentos_dict = defaultdict(list)
    
    for horario_dia, lista_turmas in turmas.items():
        for turma in lista_turmas:
            agendamentos_dict[horario_dia].extend(turma)
    
    # Encontrar o comprimento máximo das colunas
    if agendamentos_dict:
        max_len = max(len(col) for col in agendamentos_dict.values())
    else:
        max_len = 0
    max_len = max(max_len, len(jovens_nao_alocados))
    
    # Preencher as colunas com None para garantir que todas tenham o mesmo comprimento
    for k in agendamentos_dict.keys():
        agendamentos_dict[k].extend([None] * (max_len - len(agendamentos_dict[k])))
    
    df_agendamentos = pd.DataFrame({col: agendamentos_dict[col] for col in agendamentos_dict})
    
    # Adicionar a coluna de jovens não alocados
    df_agendamentos['Não Alocados'] = pd.Series(jovens_nao_alocados + [None] * (max_len - len(jovens_nao_alocados)))
    
    return df_agendamentos