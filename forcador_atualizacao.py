"""
🔄 FORÇAR ATUALIZAÇÃO COMPLETA DO DASHBOARD
==========================================
Limpa TODOS os caches e força recarregamento completo dos dados
"""

import streamlit as st
import os
import shutil
from pathlib import Path

def limpar_todos_os_caches():
    """Limpa todos os tipos de cache possíveis"""
    
    caches_limpos = 0
    
    # 1. Cache do sistema híbrido
    cache_hibrido = Path("cache_terloc_hibrido")
    if cache_hibrido.exists():
        try:
            shutil.rmtree(cache_hibrido)
            print("✅ Cache do sistema híbrido removido")
            caches_limpos += 1
        except Exception as e:
            print(f"❌ Erro ao remover cache híbrido: {e}")
    
    # 2. Cache do Python (__pycache__)
    pycache_dirs = list(Path(".").glob("**/__pycache__"))
    for pycache in pycache_dirs:
        try:
            shutil.rmtree(pycache)
            print(f"✅ Cache Python removido: {pycache}")
            caches_limpos += 1
        except Exception as e:
            print(f"❌ Erro ao remover {pycache}: {e}")
    
    # 3. Arquivos .pyc
    pyc_files = list(Path(".").glob("**/*.pyc"))
    for pyc_file in pyc_files:
        try:
            pyc_file.unlink()
            print(f"✅ Arquivo .pyc removido: {pyc_file}")
            caches_limpos += 1
        except Exception as e:
            print(f"❌ Erro ao remover {pyc_file}: {e}")
    
    # 4. Cache do Streamlit (se existir)
    streamlit_cache_dirs = [
        Path.home() / ".streamlit",
        Path(".streamlit"),
        Path("streamlit-cache")
    ]
    
    for cache_dir in streamlit_cache_dirs:
        if cache_dir.exists():
            try:
                # Não remover configuração, só cache
                for item in cache_dir.iterdir():
                    if 'cache' in item.name.lower():
                        if item.is_dir():
                            shutil.rmtree(item)
                        else:
                            item.unlink()
                        print(f"✅ Cache Streamlit removido: {item}")
                        caches_limpos += 1
            except Exception as e:
                print(f"❌ Erro ao limpar cache Streamlit em {cache_dir}: {e}")
    
    # 5. Forçar limpeza do cache do módulo Python
    modules_to_clear = [
        'sistema_hibrido_terloc',
        'dashboard_gaps_terloc'
    ]
    
    import sys
    for module_name in modules_to_clear:
        if module_name in sys.modules:
            del sys.modules[module_name]
            print(f"✅ Módulo Python removido do cache: {module_name}")
            caches_limpos += 1
    
    return caches_limpos

def main():
    print("🔄 FORÇAR ATUALIZAÇÃO COMPLETA DO DASHBOARD")
    print("=" * 50)
    
    caches_limpos = limpar_todos_os_caches()
    
    print(f"\n🎯 LIMPEZA CONCLUÍDA!")
    print(f"📊 Total de caches limpos: {caches_limpos}")
    
    print(f"\n🚀 PRÓXIMOS PASSOS:")
    print("1. Execute: streamlit run dashboard_gaps_terloc.py --server.port 8504")
    print("2. No dashboard, clique no botão '🔄 Atualizar Dados' na sidebar")
    print("3. Aguarde o recarregamento completo dos dados")
    print("4. Verifique se os filtros da sidebar mostram nomes normalizados")
    
    print(f"\n⚠️  IMPORTANTE:")
    print("- A primeira execução pode demorar mais (reprocessamento completo)")
    print("- Os dados serão recarregados com normalização aplicada")
    print("- O cache será recriado automaticamente")

if __name__ == "__main__":
    main()