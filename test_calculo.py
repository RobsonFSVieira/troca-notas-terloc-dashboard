import pandas as pd

# Carregar dados da aba correta
df = pd.read_excel('PLANILHA TROCA DE NOTA TERLOC.xlsx', sheet_name='PLANILHA ÚNICA')
print(f'Dados carregados: {len(df):,} registros')

# Verificar se as colunas existem
cols = ['DATA  TICKET', 'HORA TICKET', 'HORARIO SENHA ', 'HORA GATE ']
for col in cols:
    exists = col in df.columns
    print(f"Coluna '{col}': {'✅' if exists else '❌'}")

# Teste básico de cálculo com dados válidos
if all(col in df.columns for col in cols):
    # Filtrar dados válidos (não nulos)
    mask = (
        df['DATA  TICKET'].notna() & 
        df['HORA TICKET'].notna() & 
        df['HORARIO SENHA '].notna() &
        (df['DATA  TICKET'] != '') &
        (df['HORA TICKET'] != '') &
        (df['HORARIO SENHA '] != '')
    )
    
    df_valido = df[mask]
    print(f'Registros válidos para cálculo (TICKET→SENHA): {len(df_valido):,}')
    
    if len(df_valido) > 0:
        primeira_linha = df_valido.iloc[0]
        print(f'\n📋 EXEMPLO DE DADOS VÁLIDOS:')
        print(f'Data: {primeira_linha["DATA  TICKET"]}')
        print(f'Hora Ticket: {primeira_linha["HORA TICKET"]}')
        print(f'Hora Senha: {primeira_linha["HORARIO SENHA "]}')
        
        # Teste de conversão para datetime
        try:
            data_str = str(primeira_linha["DATA  TICKET"]).split(' ')[0]  # Apenas a data
            hora_ticket = str(primeira_linha["HORA TICKET"])
            hora_senha = str(primeira_linha["HORARIO SENHA "])
            
            dt1 = pd.to_datetime(f'{data_str} {hora_ticket}')
            dt2 = pd.to_datetime(f'{data_str} {hora_senha}')
            
            diferenca = (dt2 - dt1).total_seconds()
            horas = int(diferenca // 3600)
            minutos = int((diferenca % 3600) // 60)
            segundos = int(diferenca % 60)
            
            print(f'\n🕐 CÁLCULO DE EXEMPLO:')
            print(f'DateTime 1: {dt1}')
            print(f'DateTime 2: {dt2}')
            print(f'Diferença: {diferenca} segundos')
            print(f'Formatado: {horas}:{minutos:02d}:{segundos:02d}')
            
        except Exception as e:
            print(f'Erro no cálculo: {e}')
    else:
        print('❌ Nenhum registro válido encontrado')
else:
    print('❌ Algumas colunas necessárias não foram encontradas')