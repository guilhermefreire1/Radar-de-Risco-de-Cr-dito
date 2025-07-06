# Importa a biblioteca requests para fazer requisições HTTP
import requests
# Importa pandas (não é usado neste script, mas pode ser útil para manipulação futura de dados)
import pandas as pd
# Importa datetime e timedelta para manipulação de datas
from datetime import datetime, timedelta
# Importa os módulos os e sys para manipulação de arquivos e argumentos do sistema
import os
import sys

# Dicionário com os indicadores e seus códigos SGS e frequência
indicadores = {
    'selic': {'codigo': 4189, 'frequencia': 'diaria'},
    'ipca': {'codigo': 433, 'frequencia': 'mensal'},
    'dolar': {'codigo': 10813, 'frequencia': 'diaria'},  # Dólar comercial venda
    'cdi': {'codigo': 12, 'frequencia': 'diaria'},
    # inadimplencia PF virá depois via CSV
}

# Função para buscar dados do SGS do Banco Central
# Recebe o código do indicador e o período inicial e final
# Retorna o texto CSV da resposta

def fetch_bcb(codigo, data_ini, data_fim):
    # Monta a URL da API do SGS
    url = f"https://api.bcb.gov.br/dados/serie/bcdata.sgs.{codigo}/dados?formato=csv&dataInicial={data_ini}&dataFinal={data_fim}"
    # Faz a requisição GET
    response = requests.get(url)
    # Lança erro se a resposta não for 200
    response.raise_for_status()
    # Retorna o conteúdo da resposta (CSV)
    return response.text

# Função para salvar o texto CSV em um arquivo
# Cria o diretório se não existir

def save_to_csv(csv_text, filename):
    os.makedirs(os.path.dirname(filename), exist_ok=True)  # Garante que o diretório existe
    with open(filename, 'w', encoding='utf-8') as f:       # Abre o arquivo para escrita
        f.write(csv_text)                                  # Escreve o conteúdo CSV

# Função principal do script

def main():
    # Verifica se o nome do indicador foi passado como argumento
    if len(sys.argv) < 2:
        print("Uso: python fetch_bcb.py <nome_indicador>")
        sys.exit(1)
    nome = sys.argv[1]  # Pega o nome do indicador do argumento
    # Verifica se o indicador existe no dicionário
    if nome not in indicadores:
        print(f"Indicador '{nome}' não encontrado. Opções: {list(indicadores.keys())}")
        sys.exit(1)
    codigo = indicadores[nome]['codigo']  # Busca o código SGS
    hoje = datetime.today()               # Data de hoje
    data_fim = hoje.strftime('%d/%m/%Y')  # Data final no formato brasileiro
    data_ini = (hoje - timedelta(days=5*365)).strftime('%d/%m/%Y')  # Data inicial: 5 anos atrás
    print(f"Baixando dados do indicador {nome} (código {codigo}) de {data_ini} até {data_fim}...")
    csv_text = fetch_bcb(codigo, data_ini, data_fim)  # Busca os dados
    # Caminho absoluto para a pasta data/raw dentro do projeto
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    filename = os.path.join(base_dir, "data", "raw", f"{nome}.csv")
    save_to_csv(csv_text, filename)                   # Salva o CSV
    print(f"Arquivo salvo em {filename}")             # Mensagem de sucesso


# Executa a função principal se o script for chamado diretamente
if __name__ == "__main__":
    main()
