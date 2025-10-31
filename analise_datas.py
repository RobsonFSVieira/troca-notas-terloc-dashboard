import pandas as pd

df = pd.read_excel('PLANILHA TROCA DE NOTA TERLOC.xlsx', sheet_name='PLANILHA ÚNICA')

# Filtrar alguns registros com NF válida para análise
mask = (df['HORA RECEBIMENTO NF DE VENDA'].notna()) & (df['HORA GATE '].notna())
df_sample = df[mask].head(5)

print('ANÁLISE DAS DATAS EM REGISTROS COM NF:')
print('='*60)

for i, (idx, row) in enumerate(df_sample.iterrows()):
    print(f'REGISTRO {i+1}:')
    print(f'  DATA: {row["DATA"]}')
    print(f'  DATA TICKET: {row["DATA  TICKET"]}') 
    print(f'  DATA LIBERAÇÃO: {row["DATA DE LIBERAÇÃO"]}')
    print(f'  HORA GATE: {row["HORA GATE "]}')
    print(f'  HORA NF VENDA: {row["HORA RECEBIMENTO NF DE VENDA"]}')
    print()

# Verificar se DATA DE LIBERAÇÃO pode ser a data real da NF
print('\nCOMPARAÇÃO DE DATAS:')
print('='*40)
for i, (idx, row) in enumerate(df_sample.iterrows()):
    data_ticket = pd.to_datetime(row["DATA  TICKET"]).date()
    data_liberacao = pd.to_datetime(row["DATA DE LIBERAÇÃO"]).date() if pd.notna(row["DATA DE LIBERAÇÃO"]) else None
    
    print(f'REGISTRO {i+1}:')
    print(f'  Data Ticket: {data_ticket}')
    print(f'  Data Liberação: {data_liberacao}')
    if data_liberacao:
        diff_days = (data_liberacao - data_ticket).days
        print(f'  Diferença: {diff_days} dias')
    print()