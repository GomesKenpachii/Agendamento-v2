from collections import defaultdict
import pandas as pd

def processar_disponibilidade(data):
    disponibilidade_pessoas = defaultdict(lambda: defaultdict(list))
    linhas = data.strip().split('\n')
    dias = linhas[0].split('\t')[1:]
    
    for linha in linhas[1:]:
        partes = linha.split('\t')
        nome = partes[0]
        horarios = partes[1:]
        
        for dia, horario in zip(dias, horarios):
            if horario:
                for h in horario.split(', '):
                    disponibilidade_pessoas[dia][h].append(nome)
    
    return disponibilidade_pessoas

def criar_turmas(disponibilidade_pessoas, max_pessoas_por_turma, max_turmas_por_horario, min_pessoas_por_turma, max_pareamentos_por_pessoa):
    turmas = defaultdict(list)
    jovens_alocados = defaultdict(int)  # Track the number of times each person is allocated
    jovens_nao_alocados = set()
    
    # Ordenar pessoas por disponibilidade (menos disponíveis primeiro)
    disponibilidade_ordenada = sorted(disponibilidade_pessoas.items(), key=lambda x: len(x[1]))
    
    for horario, dias in disponibilidade_ordenada:
        for dia, pessoas in dias.items():
            pessoas_disponiveis = [pessoa for pessoa in pessoas if jovens_alocados[pessoa] < max_pareamentos_por_pessoa]
            for i in range(0, len(pessoas_disponiveis), max_pessoas_por_turma):
                if len(turmas[f"{dia} - {horario}"]) >= max_turmas_por_horario:
                    break
                turma = pessoas_disponiveis[i:i + max_pessoas_por_turma]
                if len(turma) >= min_pessoas_por_turma:
                    turmas[f"{dia} - {horario}"].append(turma)
                    for pessoa in turma:
                        jovens_alocados[pessoa] += 1
    
    # Identificar jovens não alocados
    for dias in disponibilidade_pessoas.values():
        for pessoas in dias.values():
            for pessoa in pessoas:
                if jovens_alocados[pessoa] == 0:
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
    
   
    df_agendamentos = pd.DataFrame({col: agendamentos_dict[col] for col in agendamentos_dict})
    
    # Adicionar a coluna de jovens não alocados
    df_agendamentos['Não Alocados'] = pd.Series(jovens_nao_alocados + [None] * (max_len - len(jovens_nao_alocados)))
    
    return df_agendamentos
