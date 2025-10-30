"""
✅ VERIFICAÇÃO FINAL DO DASHBOARD
===============================
Script para confirmar que o dashboard está funcionando
"""

import requests
import time

def verificar_dashboard():
    print("✅ VERIFICAÇÃO FINAL DO DASHBOARD")
    print("=" * 50)
    
    url = "http://localhost:8504"
    
    print(f"🔍 Verificando {url}...")
    
    try:
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            print("✅ Dashboard FUNCIONANDO!")
            print(f"   Status Code: {response.status_code}")
            print(f"   Tamanho da resposta: {len(response.content)} bytes")
            
            # Verificar se contém conteúdo Streamlit
            if "streamlit" in response.text.lower() or "st-emotion-cache" in response.text:
                print("✅ Streamlit detectado na resposta!")
            else:
                print("⚠️  Resposta não parece ser do Streamlit")
            
            return True
        else:
            print(f"❌ Dashboard retornou status: {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Não foi possível conectar ao dashboard")
        print("   Verifique se o Streamlit está rodando")
        return False
    except requests.exceptions.Timeout:
        print("⏰ Timeout - Dashboard pode estar carregando")
        return False
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False

if __name__ == "__main__":
    if verificar_dashboard():
        print("\n🎉 SUCESSO! Dashboard está funcionando!")
        print("🌐 Acesse: http://localhost:8504")
        print("\n📋 PRÓXIMOS PASSOS:")
        print("1. Abra o navegador em http://localhost:8504")
        print("2. Verifique os filtros de CLIENTE e CLIENTE DE VENDA")
        print("3. Confirme que não há mais duplicatas (ex: ADUFERTIL)")
        print("4. Teste o botão '🔄 Atualizar Dados' se necessário")
    else:
        print("\n❌ Dashboard não está funcionando corretamente")
        print("💡 Tente reiniciar o Streamlit")