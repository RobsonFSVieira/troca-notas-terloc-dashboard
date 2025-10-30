"""
🔍 DIAGNÓSTICO DO SISTEMA DE CARREGAMENTO
=======================================
Verifica qual sistema está sendo usado pelo dashboard
"""

import sys
import os

# Adicionar caminho atual
sys.path.append('.')

def diagnosticar_sistema():
    print("🔍 DIAGNÓSTICO DO SISTEMA DE CARREGAMENTO")
    print("=" * 50)
    
    # Verificar importação do sistema híbrido
    try:
        from sistema_hibrido_terloc import carregar_dados_streamlit, interface_upload_streamlit
        print("✅ Sistema híbrido importado com sucesso")
        
        # Testar se funciona
        try:
            df = carregar_dados_streamlit(100)  # Apenas 100 registros para teste
            print(f"✅ Sistema híbrido funcionando - {len(df)} registros carregados")
            print(f"📊 Colunas: {list(df.columns)}")
            
            # Verificar se tem normalização
            if 'CLIENTE' in df.columns:
                clientes_unicos = df['CLIENTE'].unique()[:5]
                print(f"🎯 Primeiros 5 clientes: {clientes_unicos}")
                
                # Verificar se parece normalizado
                adufertil_count = len([c for c in clientes_unicos if 'ADUFERTIL' in str(c)])
                if adufertil_count > 0:
                    print(f"🔍 Clientes ADUFERTIL encontrados: {adufertil_count}")
                
        except Exception as e:
            print(f"❌ Erro ao testar sistema híbrido: {e}")
            
    except ImportError as e:
        print(f"❌ Sistema híbrido não pode ser importado: {e}")
        print("⚠️  Dashboard irá usar sistema fallback (antigo)")
        return False
    
    # Verificar cache
    cache_dir = "cache_terloc_hibrido"
    if os.path.exists(cache_dir):
        arquivos_cache = os.listdir(cache_dir)
        print(f"\n📁 Cache do sistema híbrido:")
        for arquivo in arquivos_cache:
            print(f"   - {arquivo}")
    else:
        print("\n⚠️  Diretório de cache do sistema híbrido não existe")
    
    return True

def verificar_planilha_original():
    print(f"\n📋 VERIFICANDO PLANILHA ORIGINAL:")
    
    import pandas as pd
    
    planilha = "PLANILHA TROCA DE NOTA TERLOC.xlsx"
    if os.path.exists(planilha):
        print(f"✅ Planilha encontrada: {planilha}")
        
        try:
            # Ler apenas algumas linhas para verificar
            df_original = pd.read_excel(planilha, sheet_name='PLANILHA ÚNICA', nrows=5)
            
            if 'CLIENTE' in df_original.columns:
                clientes_orig = df_original['CLIENTE'].tolist()
                print(f"🎯 Primeiros clientes na planilha original:")
                for i, cliente in enumerate(clientes_orig, 1):
                    print(f"   {i}. {cliente}")
            
        except Exception as e:
            print(f"❌ Erro ao ler planilha: {e}")
    else:
        print(f"❌ Planilha não encontrada: {planilha}")

if __name__ == "__main__":
    diagnosticar_sistema()
    verificar_planilha_original()
    print(f"\n🎯 DIAGNÓSTICO CONCLUÍDO!")
    