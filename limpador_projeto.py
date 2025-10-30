"""
🧹 LIMPADOR DE ARQUIVOS DESNECESSÁRIOS
=====================================
Remove arquivos que não são mais necessários para manter o projeto limpo
"""

import os
from pathlib import Path

def limpar_arquivos_desnecessarios():
    """Remove arquivos que não são mais usados no projeto"""
    
    arquivos_para_remover = [
        # Arquivos de desenvolvimento/teste que não são mais necessários
        "aplicar_sistema_monitor.py",
        "carregador_onedrive_terloc.py", 
        "configurar_onedrive_permissoes.py",
        "corretor_indentacao.py",
        "corretor_onedrive.py",
        "dashboard_gaps_terloc_backup_limpeza.py",
        "executar_dashboard.bat",
        "executar_dashboard_rapido.bat",
        "guia_atualizacao_deploy.py",
        "implementador_final.py",
        "instalador_otimizacoes.py",
        "limpador_codigo_orfao.py",
        "limpador_terloc.py",
        "migrador_terloc.py",
        "monitor_arquivo_terloc.py",
        "teste_normalizacao.py",
        "teste_onedrive.py",
        
        # Arquivos de documentação desnecessários
        "FOCO_METRICAS_NEGOCIO.md",
        "INSTRUCOES_SUBSTITUICAO.md",
        "MELHORIAS_IMPLEMENTADAS.md",
        "MIGRACAO_TERLOC_GUIA.md",
        "TABELA_LIMPA_DOCUMENTACAO.md",
        "info.txt"
    ]
    
    pastas_para_remover = [
        "BACKUP_LIMPEZA_20251028_133321",
        "backup_sistema_antigo",
        "cache_terloc_rapido",
        ".history"
    ]
    
    print("🧹 LIMPANDO ARQUIVOS DESNECESSÁRIOS...")
    print("=" * 50)
    
    removidos = 0
    
    # Remover arquivos
    for arquivo in arquivos_para_remover:
        if os.path.exists(arquivo):
            try:
                os.remove(arquivo)
                print(f"✅ Removido: {arquivo}")
                removidos += 1
            except Exception as e:
                print(f"❌ Erro ao remover {arquivo}: {e}")
        else:
            print(f"➡️  Não encontrado: {arquivo}")
    
    # Remover pastas
    for pasta in pastas_para_remover:
        if os.path.exists(pasta):
            try:
                import shutil
                shutil.rmtree(pasta)
                print(f"✅ Pasta removida: {pasta}")
                removidos += 1
            except Exception as e:
                print(f"❌ Erro ao remover pasta {pasta}: {e}")
        else:
            print(f"➡️  Pasta não encontrada: {pasta}")
    
    print(f"\n🎯 LIMPEZA CONCLUÍDA! {removidos} itens removidos.")
    
    # Mostrar arquivos que restaram (essenciais)
    print(f"\n📁 ARQUIVOS ESSENCIAIS MANTIDOS:")
    arquivos_essenciais = [
        "dashboard_gaps_terloc.py",           # Dashboard principal
        "sistema_hibrido_terloc.py",         # Sistema de carregamento híbrido
        "PLANILHA TROCA DE NOTA TERLOC.xlsx", # Dados padrão
        "requirements.txt",                   # Dependências
        "README.md",                          # Documentação
        ".gitignore",                         # Git
        "cache_terloc_hibrido/",             # Cache do sistema híbrido
        "__pycache__/",                      # Cache Python
        ".git/",                             # Repositório Git
        ".venv/"                             # Ambiente virtual
    ]
    
    for item in arquivos_essenciais:
        if os.path.exists(item):
            print(f"✅ {item}")
        else:
            print(f"⚠️  {item} (não encontrado)")

if __name__ == "__main__":
    limpar_arquivos_desnecessarios()