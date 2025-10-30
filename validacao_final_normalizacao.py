"""
🔍 VALIDAÇÃO FINAL DA NORMALIZAÇÃO NO DASHBOARD
==============================================
Script para testar o sistema híbrido carregando dados reais
"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

from sistema_hibrido_terloc import sistema_hibrido

def main():
    print("🔍 VALIDAÇÃO FINAL DA NORMALIZAÇÃO")
    print("=" * 50)
    
    # Carregar dados usando o sistema híbrido
    print("📊 Carregando dados do sistema híbrido...")
    df = sistema_hibrido.carregar_dados_inteligente(limite_registros=1000)
    
    if df.empty:
        print("❌ Nenhum dado carregado!")
        return
    
    print(f"✅ Dados carregados: {len(df):,} registros")
    print(f"📋 Colunas disponíveis: {list(df.columns)}")
    
    # Verificar normalização de clientes
    if 'CLIENTE' in df.columns:
        print("\n🎯 CLIENTES ÚNICOS (após normalização):")
        clientes_unicos = sorted(df['CLIENTE'].unique())
        for i, cliente in enumerate(clientes_unicos[:10], 1):  # Primeiros 10
            print(f"   {i:2d}. {cliente}")
        if len(clientes_unicos) > 10:
            print(f"   ... e mais {len(clientes_unicos) - 10} clientes")
        print(f"\n📊 Total de clientes únicos: {len(clientes_unicos)}")
    
    # Verificar normalização de clientes de venda
    if 'CLIENTE DE VENDA' in df.columns:
        print("\n🎯 CLIENTES DE VENDA ÚNICOS (após normalização):")
        clientes_venda_unicos = sorted(df['CLIENTE DE VENDA'].unique())
        for i, cliente in enumerate(clientes_venda_unicos[:10], 1):  # Primeiros 10
            print(f"   {i:2d}. {cliente}")
        if len(clientes_venda_unicos) > 10:
            print(f"   ... e mais {len(clientes_venda_unicos) - 10} clientes")
        print(f"\n📊 Total de clientes de venda únicos: {len(clientes_venda_unicos)}")
    
    # Verificar exemplos específicos
    print("\n🔍 VERIFICAÇÃO DE EXEMPLOS ESPECÍFICOS:")
    
    # Buscar ADUFERTIL
    if 'CLIENTE' in df.columns:
        adufertil_count = df[df['CLIENTE'].str.contains('ADUFERTIL', na=False)]['CLIENTE'].value_counts()
        if not adufertil_count.empty:
            print("   📋 ADUFERTIL encontrado:")
            for nome, count in adufertil_count.items():
                print(f"      {nome}: {count} registros")
        else:
            print("   ❌ ADUFERTIL não encontrado")
    
    # Buscar ELEKEIROZ
    if 'CLIENTE' in df.columns:
        elekeiroz_count = df[df['CLIENTE'].str.contains('ELEKEIROZ', na=False)]['CLIENTE'].value_counts()
        if not elekeiroz_count.empty:
            print("   📋 ELEKEIROZ encontrado:")
            for nome, count in elekeiroz_count.items():
                print(f"      {nome}: {count} registros")
        else:
            print("   ❌ ELEKEIROZ não encontrado")
    
    print("\n✅ VALIDAÇÃO CONCLUÍDA!")
    print("🚀 Dashboard disponível em: http://localhost:8504")

if __name__ == "__main__":
    main()