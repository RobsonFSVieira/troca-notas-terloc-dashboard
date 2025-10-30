"""
🔍 DEBUG DO ARQUIVO DE MAPEAMENTO
================================
"""

import sys
from pathlib import Path

def debug_arquivo():
    arquivo_mapeamento = Path('Mapeamento de Normalização de Nomes.txt')
    
    print("🔍 DEBUGANDO ARQUIVO DE MAPEAMENTO")
    print("=" * 50)
    
    if not arquivo_mapeamento.exists():
        print("❌ Arquivo não encontrado!")
        return
    
    with open(arquivo_mapeamento, 'r', encoding='utf-8') as f:
        conteudo = f.read()
    
    print("📄 PRIMEIRAS 500 CHARS:")
    print(repr(conteudo[:500]))
    print()
    
    # Testar processamento
    secoes = conteudo.split('2. Cliente de Venda')
    secao_clientes = secoes[0].replace('1. Clientes', '').strip()
    
    print("📋 PRIMEIRA SEÇÃO (CLIENTES):")
    print(repr(secao_clientes[:300]))
    print()
    
    # Processar primeiro bloco
    blocos = secao_clientes.split('Nome Padrão:')[1:2]  # Só o primeiro
    if blocos:
        bloco = blocos[0]
        print("🎯 PRIMEIRO BLOCO:")
        print(repr(bloco))
        print()
        
        linhas = [l.strip() for l in bloco.strip().split('\n') if l.strip()]
        print("📝 LINHAS PROCESSADAS:")
        for i, linha in enumerate(linhas):
            print(f"   {i}: {repr(linha)}")

if __name__ == "__main__":
    debug_arquivo()