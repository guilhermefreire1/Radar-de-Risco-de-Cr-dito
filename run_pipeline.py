import subprocess

indicadores = ['selic', 'ipca', 'dolar', 'cdi']

# 1. Baixar dados brutos
for ind in indicadores:
    print(f"Baixando {ind}...")
    subprocess.run(["python", "scripts/fetch_bcb.py", ind], check=True)

# 2. Transformar dados
print("Transformando dados...")
subprocess.run(["python", "scripts/transform.py"], check=True)

# 3. Carregar no banco
print("Carregando no banco...")
subprocess.run(["python", "scripts/load_to_db.py"], check=True)

print("Pipeline finalizado!")
