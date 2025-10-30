"""
Teste final: Verificar se MOSAIC e SAFRA estão sendo normalizados corretamente nos dados
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sistema_hibrido_terloc import carregar_dados_streamlit
import pandas as pd

def teste_final_dados_reais():
    print("🔍 TESTE FINAL COM DADOS REAIS")
    print("=" * 50)
    
    try:
        print("📊 Carregando dados...")
        dados = carregar_dados_streamlit()
        
        print(f"✅ Dados carregados: {len(dados)} registros")
        
        # Verificar clientes únicos que contêm MOSAIC ou SAFRA
        clientes_mosaic = dados[dados['CLIENTE'].str.contains('MOSAIC', na=False)]['CLIENTE'].unique()
        clientes_safra = dados[dados['CLIENTE'].str.contains('SAFRA', na=False)]['CLIENTE'].unique()
        
        print(f"\n📋 CLIENTES COM 'MOSAIC': {len(clientes_mosaic)}")
        for cliente in sorted(clientes_mosaic):
            print(f"   • {cliente}")
        
        print(f"\n📋 CLIENTES COM 'SAFRA': {len(clientes_safra)}")
        for cliente in sorted(clientes_safra):
            print(f"   • {cliente}")
        
        # Verificar se existe apenas MOSAIC CUBATÃO e SAFRA ALFENAS (sem genéricos)
        tem_mosaic_generico = 'MOSAIC' in clientes_mosaic
        tem_safra_generico = 'SAFRA' in clientes_safra
        
        print(f"\n✅ VERIFICAÇÕES:")
        print(f"   ❌ Existe 'MOSAIC' genérico: {'SIM' if tem_mosaic_generico else 'NÃO'}")
        print(f"   ❌ Existe 'SAFRA' genérico: {'SIM' if tem_safra_generico else 'NÃO'}")
        
        if not tem_mosaic_generico and not tem_safra_generico:
            print("\n🎉 SUCESSO! Todos os nomes foram normalizados corretamente!")
        else:
            print("\n⚠️  ATENÇÃO! Ainda existem nomes genéricos.")
        
        # Contar registros por cliente
        if clientes_mosaic.size > 0:
            print(f"\n📊 CONTAGEM MOSAIC:")
            mosaic_counts = dados[dados['CLIENTE'].str.contains('MOSAIC', na=False)]['CLIENTE'].value_counts()
            for cliente, count in mosaic_counts.items():
                print(f"   • {cliente}: {count} registros")
        
        if clientes_safra.size > 0:
            print(f"\n📊 CONTAGEM SAFRA:")
            safra_counts = dados[dados['CLIENTE'].str.contains('SAFRA', na=False)]['CLIENTE'].value_counts()
            for cliente, count in safra_counts.items():
                print(f"   • {cliente}: {count} registros")
        
    except Exception as e:
        print(f"❌ Erro ao carregar dados: {e}")

if __name__ == "__main__":
    teste_final_dados_reais()