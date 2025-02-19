import pandas as pd
from collections import defaultdict

def extrair_hora(chave):
    """
    Extrai a hora inicial de um intervalo no formato '9h - 12h'.
    Retorna 0 se não conseguir converter.
    """
    if not chave.strip():
        return 0
    try:
        # Divide a string na letra 'h' e pega a primeira parte
        hora_str = chave.split('h')[0].strip()
        return int(hora_str) if hora_str.isdigit() else 0
    except Exception:
        return 0

def import_csv(file_path):
    disponibilidade_pessoas = defaultdict(lambda: defaultdict(list))
    nomes_unicos = set()
    max_pareamentos_individual = {}
    bd = pd.read_csv(file_path, sep=',', encoding='utf-8')
    
    # Considerando que os horários começam a partir da 5ª coluna
    horarios = bd.columns[4:]
    
    for index, row in bd.iterrows():
        pessoa = row[0]
        nomes_unicos.add(pessoa)
        max_pareamentos_individual[pessoa] = int(row[1])  # Extrair o valor da coluna específica
        disponibilidade = row[4:]
        for i, horarios_disponiveis in enumerate(disponibilidade):
            if pd.notna(horarios_disponiveis) and horarios_disponiveis.strip():
                # Separa os intervalos de tempo (removendo espaços extras)
                horarios_list = [h.strip() for h in horarios_disponiveis.split(',')]
                for horario in horarios_list:
                    if horario:  # Apenas processa se não estiver vazio
                        disponibilidade_pessoas[horarios[i].strip()][horario].append(pessoa)
    
    # Gerar o conjunto de todas as chaves dos subdicionários
    segundas_chaves = set()
    for sub_dict in disponibilidade_pessoas.values():
        segundas_chaves.update(sub_dict.keys())
    
    # Ordena as chaves filtrando as vazias e usando a função auxiliar
    segundas_chaves = sorted(
        [chave for chave in segundas_chaves if chave],
        key=extrair_hora
    )
    
    return disponibilidade_pessoas, list(nomes_unicos), segundas_chaves, max_pareamentos_individual