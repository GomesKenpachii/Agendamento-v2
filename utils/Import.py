import pandas as pd
from collections import defaultdict

def import_csv(file_path):
    disponibilidade_pessoas = defaultdict(lambda: defaultdict(list))
    nomes_unicos = set()
    bd = pd.read_csv(file_path, sep=';', encoding='utf-8')  # Ajuste o delimitador para ponto e vírgula
    
    # Extrair os horários do cabeçalho
    horarios = bd.columns[1:]  # Ignorar a primeira coluna "Nome Completo:"
    
    for index, row in bd.iterrows():
        pessoa = row[0]
        nomes_unicos.add(pessoa)
        disponibilidade = row[1:]
        for i, horarios_disponiveis in enumerate(disponibilidade):
            if pd.notna(horarios_disponiveis):
                horarios_list = horarios_disponiveis.split(', ')
                for horario in horarios_list:
                    disponibilidade_pessoas[horarios[i].strip()][horario.strip()].append(pessoa)
                    segundas_chaves = set()
                    for sub_dict in disponibilidade_pessoas.values():
                        segundas_chaves.update(sub_dict.keys()) 
                    segundas_chaves = sorted(segundas_chaves, key=lambda x: int(x.split('h')[0]))
    
    return disponibilidade_pessoas, list(nomes_unicos),segundas_chaves