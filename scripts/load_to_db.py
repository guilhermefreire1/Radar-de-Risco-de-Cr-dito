import os
import sqlite3
import pandas as pd
from glob import glob

# Caminho para os arquivos processados e banco de dados
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
dir_processed = os.path.join(base_dir, 'data', 'processed')
db_path = os.path.join(base_dir, 'db', 'indicators.db')

# Conecta ao banco SQLite (será criado se não existir)
conn = sqlite3.connect(db_path)
c = conn.cursor()

# Cria a tabela indicadores se não existir
c.execute('''
CREATE TABLE IF NOT EXISTS indicadores (
    data TEXT,
    valor REAL,
    indicador TEXT,
    fonte TEXT
)
''')
# Cria índice único para evitar duplicidade de data+indicador
c.execute('''
CREATE UNIQUE INDEX IF NOT EXISTS idx_indicadores_unique
ON indicadores (data, indicador)
''')

# Para cada arquivo CSV processado
for csv_path in glob(os.path.join(dir_processed, '*.csv')):
    nome_indicador = os.path.splitext(os.path.basename(csv_path))[0]
    df = pd.read_csv(csv_path, encoding='utf-8-sig')
    # Validação de colunas esperadas
    if not {'data', 'valor'}.issubset(df.columns):
        print(f"Aviso: {csv_path} não contém colunas esperadas. Pulando arquivo.")
        continue
    # Adiciona coluna indicador e fonte
    df['indicador'] = nome_indicador
    df['fonte'] = 'SGS-BCB'
    # Seleciona apenas as colunas necessárias
    df = df[['data', 'valor', 'indicador', 'fonte']]
    # Insere no banco, ignorando duplicatas
    try:
        df.to_sql('indicadores', conn, if_exists='append', index=False, method='multi')
    except Exception as e:
        print(f"Aviso: Possível duplicidade ao inserir {nome_indicador}: {e}")
    print(f"Inserido: {nome_indicador}")

# Consulta para checar total de registros
try:
    df_check = pd.read_sql("SELECT COUNT(*) FROM indicadores", conn)
    print(f"Total de registros no banco: {df_check.iloc[0,0]}")
except Exception as e:
    print(f"Erro ao consultar total de registros: {e}")

conn.close()
print("Carga finalizada!")
