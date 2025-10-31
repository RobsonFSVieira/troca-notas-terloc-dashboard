import pandas as pd
import numpy as np

# Carregar dados da aba correta
df = pd.read_excel('PLANILHA TROCA DE NOTA TERLOC.xlsx', sheet_name='PLANILHA ÚNICA')
print(f'Dados carregados: {len(df):,} registros')

# Verificar as colunas específicas do intervalo 3→4
col_data = 'DATA  TICKET'
col_hora_gate = 'HORA GATE '
col_hora_nf = 'HORA RECEBIMENTO NF DE VENDA'

print(f'\n🔍 INVESTIGANDO INTERVALO 3→4 (GATE → NF VENDA):')
print(f'Coluna data: "{col_data}" - {"✅" if col_data in df.columns else "❌"}')
print(f'Coluna Gate: "{col_hora_gate}" - {"✅" if col_hora_gate in df.columns else "❌"}') 
print(f'Coluna NF Venda: "{col_hora_nf}" - {"✅" if col_hora_nf in df.columns else "❌"}')

# Filtrar dados válidos para este intervalo específico
mask_valido = (
    df[col_data].notna() & 
    df[col_hora_gate].notna() & 
    df[col_hora_nf].notna() &
    (df[col_data] != '') &
    (df[col_hora_gate] != '') &
    (df[col_hora_nf] != '')
)

df_valido = df[mask_valido].copy()
print(f'\nRegistros válidos para GATE→NF VENDA: {len(df_valido):,}')

if len(df_valido) > 0:
    print(f'\n📊 ANÁLISE DOS PRIMEIROS 10 REGISTROS:')
    
    tempos_calculados = []
    
    for i in range(min(10, len(df_valido))):
        linha = df_valido.iloc[i]
        
        try:
            data_str = str(linha[col_data]).split(' ')[0]
            hora_gate = str(linha[col_hora_gate])
            hora_nf = str(linha[col_hora_nf])
            
            dt_gate = pd.to_datetime(f'{data_str} {hora_gate}')
            dt_nf = pd.to_datetime(f'{data_str} {hora_nf}')
            
            diferenca_seg = (dt_nf - dt_gate).total_seconds()
            horas = diferenca_seg / 3600
            
            tempos_calculados.append(diferenca_seg)
            
            print(f'\nRegistro {i+1}:')
            print(f'  Data: {data_str}')
            print(f'  Hora Gate: {hora_gate}')
            print(f'  Hora NF Venda: {hora_nf}')
            print(f'  Diferença: {horas:.2f} horas ({diferenca_seg:.0f}s)')
            
            if diferenca_seg < 0:
                print(f'  ⚠️ NEGATIVO! Provavelmente passou da meia-noite')
            elif diferenca_seg > 4*3600:  # Mais de 4 horas
                print(f'  🚨 SUSPEITO! Muito tempo ({horas:.1f}h)')
            
        except Exception as e:
            print(f'Registro {i+1}: ERRO - {e}')
    
    # Estatísticas
    if tempos_calculados:
        tempos_array = np.array(tempos_calculados)
        print(f'\n📈 ESTATÍSTICAS DOS TEMPOS (em horas):')
        print(f'Mínimo: {tempos_array.min()/3600:.2f}h')
        print(f'Máximo: {tempos_array.max()/3600:.2f}h') 
        print(f'Média: {tempos_array.mean()/3600:.2f}h')
        print(f'Mediana: {np.median(tempos_array)/3600:.2f}h')
        
        # Contar tempos suspeitos
        suspeitos = (tempos_array > 4*3600).sum()
        negativos = (tempos_array < 0).sum()
        print(f'\n🚨 ANÁLISE:')
        print(f'Tempos > 4h: {suspeitos}/{len(tempos_calculados)}')
        print(f'Tempos negativos: {negativos}/{len(tempos_calculados)}')

else:
    print('❌ Nenhum registro válido encontrado para este intervalo')
    
    # Verificar o que está acontecendo com os dados
    print(f'\n🔍 DIAGNÓSTICO:')
    print(f'Total de registros: {len(df):,}')
    print(f'Com data válida: {df[col_data].notna().sum():,}')
    print(f'Com hora gate válida: {df[col_hora_gate].notna().sum():,}')
    print(f'Com hora NF válida: {df[col_hora_nf].notna().sum():,}')