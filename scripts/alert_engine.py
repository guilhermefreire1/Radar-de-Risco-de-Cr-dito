import os
import sqlite3
import pandas as pd
from datetime import datetime

# Caminhos
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
db_path = os.path.join(base_dir, 'db', 'indicators.db')
log_dir = os.path.join(base_dir, 'logs')
os.makedirs(log_dir, exist_ok=True)
log_path = os.path.join(log_dir, 'alertas.txt')

# Parâmetros
INDICADOR = 'selic'
N = 3  # Número de registros para a regra

# Conecta ao banco e consulta os últimos N+1 valores do indicador
conn = sqlite3.connect(db_path)
query = f"""
    SELECT data, valor FROM indicadores
    WHERE indicador = ?
    ORDER BY data DESC
    LIMIT ?
"""
df = pd.read_sql(query, conn, params=(INDICADOR, N+1))
conn.close()

# Garante ordem cronológica
df = df.sort_values('data')

# Regra: SELIC subiu 3 vezes seguidas
alerta = False
if len(df) >= N+1:
    subidas = all(df['valor'].iloc[i] < df['valor'].iloc[i+1] for i in range(N))
    if subidas:
        alerta = True

# Mensagem de alerta
if alerta:
    msg = f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] ALERTA: SELIC subiu {N} vezes seguidas! Últimos valores: {df['valor'].tolist()}"
    print(msg)
    with open(log_path, 'a', encoding='utf-8') as f:
        f.write(msg + '\n')
else:
    print("Nenhum alerta gerado.")
