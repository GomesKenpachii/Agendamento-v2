from collections import defaultdict
import pandas as pd

def criar_turmas(disponibilidade_pessoas, max_pessoas_por_turma, max_turmas_por_horario, min_pessoas_por_turma):
    turmas = defaultdict(list)
    jovens_alocados = set()
    jovens_nao_alocados = set()
    
    for horario, dias in disponibilidade_pessoas.items():
        for dia, pessoas in dias.items():
            pessoas_disponiveis = [pessoa for pessoa in pessoas if pessoa not in jovens_alocados]
            for i in range(0, len(pessoas_disponiveis), max_pessoas_por_turma):
                if len(turmas[f"{dia} - {horario}"]) >= max_turmas_por_horario:
                    break
                turma = pessoas_disponiveis[i:i + max_pessoas_por_turma]
                if len(turma) >= min_pessoas_por_turma:
                    turmas[f"{dia} - {horario}"].append(turma)
                    jovens_alocados.update(turma)
    
    # Identificar jovens não alocados
    for dias in disponibilidade_pessoas.values():
        for pessoas in dias.values():
            for pessoa in pessoas:
                if pessoa not in jovens_alocados:
                    jovens_nao_alocados.add(pessoa)
    
    return turmas, list(jovens_nao_alocados)

def montar_dataframe_agendamentos(turmas, jovens_nao_alocados):
    # Criar um DataFrame com os agendamentos
    agendamentos_dict = defaultdict(list)
    
    for horario_dia, lista_turmas in turmas.items():
        for turma in lista_turmas:
            agendamentos_dict[horario_dia].extend(turma)
    
    # Encontrar o comprimento máximo das colunas
    max_len = max(len(col) for col in agendamentos_dict.values())
    max_len = max(max_len, len(jovens_nao_alocados))
    
    # Preencher as colunas com None para garantir que todas tenham o mesmo comprimento
    for k in agendamentos_dict.keys():
        agendamentos_dict[k].extend([None] * (max_len - len(agendamentos_dict[k])))
    
    df_agendamentos = pd.DataFrame(agendamentos_dict)
    
    # Adicionar a coluna de jovens não alocados
    df_agendamentos['Não Alocados'] = pd.Series(jovens_nao_alocados + [None] * (max_len - len(jovens_nao_alocados)))
    
    return df_agendamentos