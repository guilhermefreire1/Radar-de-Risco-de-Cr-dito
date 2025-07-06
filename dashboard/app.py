import os
import sqlite3
import pandas as pd
import streamlit as st
import plotly.express as px
from datetime import datetime

# Caminhos
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
db_path = os.path.join(base_dir, 'db', 'indicators.db')
log_path = os.path.join(base_dir, 'logs', 'alertas.txt')

st.set_page_config(page_title="Radar de Risco de Crédito", layout="wide")
st.title("📊 Radar de Risco de Crédito")

# Conecta ao banco e obtém indicadores disponíveis
conn = sqlite3.connect(db_path)
df_indicadores = pd.read_sql("SELECT DISTINCT indicador FROM indicadores", conn)
indicadores = df_indicadores['indicador'].sort_values().tolist()

# Sidebar para seleção de indicador e período
st.sidebar.header("Filtros")
descricoes = {
    'selic': "Taxa básica de juros da economia brasileira.",
    'ipca': "Índice Nacional de Preços ao Consumidor Amplo (inflação).",
    'dolar': "Cotação do dólar comercial.",
    'cdi': "Certificado de Depósito Interbancário.",
}
indicador = st.sidebar.selectbox("Escolha o indicador", indicadores)
st.sidebar.caption(descricoes.get(indicador, ""))

# Consulta datas disponíveis
df_datas = pd.read_sql(f"SELECT MIN(data) as min_data, MAX(data) as max_data FROM indicadores WHERE indicador = ?", conn, params=(indicador,))
data_min = df_datas['min_data'][0]
data_max = df_datas['max_data'][0]

periodo = st.sidebar.date_input(
    "Período",
    value=(datetime.strptime(data_min, '%Y-%m-%d'), datetime.strptime(data_max, '%Y-%m-%d')),
    min_value=datetime.strptime(data_min, '%Y-%m-%d'),
    max_value=datetime.strptime(data_max, '%Y-%m-%d')
)

# Consulta dados filtrados
df = pd.read_sql(
    """
    SELECT data, valor FROM indicadores
    WHERE indicador = ? AND data BETWEEN ? AND ?
    ORDER BY data
    """,
    conn,
    params=(indicador, periodo[0].strftime('%Y-%m-%d'), periodo[1].strftime('%Y-%m-%d'))
)
conn.close()

# Plota gráfico
st.subheader(f"Série temporal: {indicador.upper()}")
if not df.empty:
    fig = px.line(df, x='data', y='valor', title=f"{indicador.upper()} ao longo do tempo")
    st.plotly_chart(fig, use_container_width=True)
    # Métricas abaixo do gráfico
    col1, col2, col3 = st.columns(3)
    col1.metric("Valor Mínimo", f"{df['valor'].min():.2f}")
    col2.metric("Valor Máximo", f"{df['valor'].max():.2f}")
    col3.metric("Média", f"{df['valor'].mean():.2f}")
    # Botão de download
    st.download_button(
        label="Baixar dados filtrados",
        data=df.to_csv(index=False).encode('utf-8-sig'),
        file_name=f"{indicador}_filtrado.csv",
        mime='text/csv'
    )
else:
    st.warning("Não há dados para o período selecionado.")

# Exibe alertas recentes
st.subheader("Alertas Recentes")
if os.path.exists(log_path):
    with open(log_path, 'r', encoding='utf-8') as f:
        alertas = f.readlines()
    if alertas:
        for alerta in reversed(alertas[-10:]):
            st.info(alerta.strip())
    else:
        st.write("Nenhum alerta registrado.")
else:
    st.write("Arquivo de alertas não encontrado.")
