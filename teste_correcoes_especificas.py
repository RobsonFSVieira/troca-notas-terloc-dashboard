"""
Teste específico para as correções MOSAIC e SAFRA
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sistema_hibrido_terloc import SistemaHibridoTerloc

def teste_correções_especificas():
    print("🔍 TESTE DAS CORREÇÕES ESPECÍFICAS")
    print("=" * 50)
    
    # Criar instância do sistema híbrido
    sistema = SistemaHibridoTerloc()
    
    # Casos de teste para MOSAIC
    casos_mosaic = [
        "MOSAIC",
        "MOSAIC CUBATÃO", 
        "MOSAIC CUBATAO",
        "MOSAIC UBERABA"
    ]
    
    print("\n📋 TESTES MOSAIC:")
    print("-" * 30)
    for nome in casos_mosaic:
        resultado = sistema.normalizar_nome_cliente(nome)
        print(f"'{nome}' → '{resultado}'")
    
    # Casos de teste para SAFRA
    casos_safra = [
        "SAFRA",
        "SAFRA ALFENAS",
        "SAFRA IND. ALFENAS"
    ]
    
    print("\n📋 TESTES SAFRA:")
    print("-" * 30)
    for nome in casos_safra:
        resultado = sistema.normalizar_nome_cliente(nome)
        print(f"'{nome}' → '{resultado}'")
    
    print("\n✅ VERIFICAÇÃO:")
    print("-" * 30)
    
    # Verificações específicas
    verificacoes = [
        ("MOSAIC deve virar MOSAIC CUBATÃO", "MOSAIC", "MOSAIC CUBATÃO"),
        ("SAFRA deve virar SAFRA ALFENAS", "SAFRA", "SAFRA ALFENAS"),
        ("MOSAIC CUBATÃO deve permanecer igual", "MOSAIC CUBATÃO", "MOSAIC CUBATÃO"),
        ("SAFRA ALFENAS deve permanecer igual", "SAFRA ALFENAS", "SAFRA ALFENAS")
    ]
    
    todos_ok = True
    for descricao, entrada, esperado in verificacoes:
        resultado = sistema.normalizar_nome_cliente(entrada)
        status = "✅" if resultado == esperado else "❌"
        print(f"{status} {descricao}")
        if resultado != esperado:
            print(f"   Esperado: '{esperado}' | Obtido: '{resultado}'")
            todos_ok = False
    
    if todos_ok:
        print("\n🎉 TODAS AS CORREÇÕES FUNCIONANDO!")
    else:
        print("\n⚠️  ALGUMAS CORREÇÕES PRECISAM SER AJUSTADAS")

if __name__ == "__main__":
    teste_correções_especificas()