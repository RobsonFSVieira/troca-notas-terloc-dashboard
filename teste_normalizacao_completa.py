"""
🧪 TESTE COMPLETO DA NORMALIZAÇÃO
================================
Teste do sistema de normalização usando o arquivo de mapeamento
"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

from sistema_hibrido_terloc import SistemaHibridoTerloc

def main():
    print("🧪 TESTE DA NORMALIZAÇÃO COMPLETA")
    print("=" * 50)
    
    # Instanciar sistema
    sistema = SistemaHibridoTerloc()
    
    # Testar alguns nomes de clientes
    print("\n📋 TESTANDO CLIENTES:")
    nomes_clientes_teste = [
        "ADUFERTIL JUNDIAI",
        "ADUFERIL JUNDIAI", 
        "ADULFERTIL JUNDIAI SP",
        "ELEKEIROZ/VARZEA-SP",
        "ELEIKEIROZ/ VARZEA-SP",
        "MOSAIC CUBATAO",
        "MOSAIC CUBATÃO 0099-60/SP",
        "CSRD CUBATÃO/SP"
    ]
    
    for nome in nomes_clientes_teste:
        resultado = sistema.normalizar_nome_cliente(nome)
        print(f"   {nome:<30} → {resultado}")
    
    # Testar alguns nomes de clientes de venda
    print("\n📋 TESTANDO CLIENTES DE VENDA:")
    nomes_venda_teste = [
        "ADUBOS ARAG. ANAPOLIS/GO",
        "ADUBOS ARAG - CATALAO/GO", 
        "ADUFERTIL ALFENAS/MG",
        "COFCO - SEBASTIANOPOLIS/SP",
        "FASS - NOVA INDEPENDENCIA",
        "FASS SERTAOZINHO/SP",
        "ICL JACAREI/SP - 0013/56",
        "SAFRA IND. FERT/ALFENAS"
    ]
    
    for nome in nomes_venda_teste:
        resultado = sistema.normalizar_cliente_venda(nome)
        print(f"   {nome:<30} → {resultado}")
    
    print("\n✅ TESTE CONCLUÍDO!")

if __name__ == "__main__":
    main()