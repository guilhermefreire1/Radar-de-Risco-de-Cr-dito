import os
import pandas as pd
from glob import glob

# Caminho para os arquivos CSV brutos e processados
dir_raw = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data', 'raw')
dir_processed = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data', 'processed')
os.makedirs(dir_processed, exist_ok=True)

# Para cada arquivo CSV em data/raw
for csv_path in glob(os.path.join(dir_raw, '*.csv')):
    # Tenta ler o CSV com separador ; e encoding utf-8
    try:
        df = pd.read_csv(csv_path, sep=';', encoding='utf-8')
    except Exception as e:
        print(f"Erro ao ler {csv_path}: {e}")
        continue
    # Padroniza o nome das colunas
    df.columns = [col.strip().lower() for col in df.columns]
    # Validação de colunas esperadas
    if not {'data', 'valor'}.issubset(df.columns):
        print(f"Aviso: {csv_path} não contém colunas esperadas. Pulando arquivo.")
        continue
    # Padroniza o formato da data
    df['data'] = pd.to_datetime(df['data'], dayfirst=True, errors='coerce').dt.strftime('%Y-%m-%d')
    # Converte o valor para float, trocando vírgula por ponto se necessário
    df['valor'] = df['valor'].astype(str).str.replace(',', '.', regex=False)
    df['valor'] = pd.to_numeric(df['valor'], errors='coerce')
    # Ordena por data
    df = df.sort_values('data')
    # Salva o arquivo processado com UTF-8 com BOM
    nome = os.path.basename(csv_path)
    df.to_csv(os.path.join(dir_processed, nome), index=False, encoding='utf-8-sig')
    print(f"Processado: {nome}")
