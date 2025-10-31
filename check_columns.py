import pandas as pd

try:
    # LER APENAS A ABA "PLANILHA ÚNICA"
    df = pd.read_excel('PLANILHA TROCA DE NOTA TERLOC.xlsx', sheet_name='PLANILHA ÚNICA')
    print("ABA: PLANILHA ÚNICA")
    print("TOTAL DE COLUNAS:", len(df.columns))
    print("TOTAL DE REGISTROS:", len(df))
    
    print("\nTODAS AS COLUNAS:")
    for i, col in enumerate(df.columns):
        print(f"{i+1:2d}. '{col}'")
    
    print(f"\nCOLUNAS RELACIONADAS A HORÁRIOS:")
    keywords = ['HORA', 'DATA', 'TICKET', 'SENHA', 'GATE', 'RECEBIMENTO', 'LIBERAÇÃO']
    colunas_relevantes = []
    
    for col in df.columns:
        col_str = str(col).upper()
        for keyword in keywords:
            if keyword in col_str:
                colunas_relevantes.append(col)
                break
    
    for i, col in enumerate(sorted(colunas_relevantes)):
        print(f"  {i+1:2d}. '{col}'")
    
    print(f"\nPrimeiros valores das colunas de horário:")
    if len(df) > 0:
        primeira_linha = df.iloc[0]
        for col in colunas_relevantes[:8]:  # Primeiras 8 colunas relevantes
            valor = primeira_linha[col] if col in df.columns else "N/A"
            print(f"  {col}: {valor}")
            
except Exception as e:
    print(f"Erro ao ler aba PLANILHA ÚNICA: {e}")
    
    # Tentar listar abas disponíveis
    try:
        xl_file = pd.ExcelFile('PLANILHA TROCA DE NOTA TERLOC.xlsx')
        print(f"\nAbas disponíveis no arquivo:")
        for i, aba in enumerate(xl_file.sheet_names):
            print(f"  {i+1}. '{aba}'")
    except Exception as e2:
        print(f"Erro ao listar abas: {e2}")