# 🚀 Sistema Híbrido de Carregamento - Quick Start

> Sistema otimizado de carregamento de dados desenvolvido no projeto **Troca de Notas Terloc**

## ⚡ Benefícios
- **Performance**: Carregamento ~90% mais rápido após primeira execução
- **Otimização**: Remove colunas vazias automaticamente  
- **Normalização**: Padroniza dados inconsistentes
- **Cache Inteligente**: Detecta mudanças no arquivo automaticamente

## 📁 Arquivos para Copiar

### 1. **TEMPLATE_sistema_hibrido_carregamento.py**
Sistema principal - copie e renomeie para seu projeto

### 2. **EXEMPLO_dashboard_com_sistema_hibrido.py** 
Template de dashboard Streamlit já integrado

### 3. **IMPLEMENTACAO_SISTEMA_HIBRIDO_CARREGAMENTO.md**
Documentação completa com todos os detalhes

## 🚀 Implementação Rápida (5 minutos)

### Passo 1: Copiar Arquivo Template
```bash
# Copie TEMPLATE_sistema_hibrido_carregamento.py para seu projeto
# Renomeie para: sistema_hibrido_SEU_PROJETO.py
```

### Passo 2: Configurar
```python
# Altere estas linhas no arquivo:
nome_projeto = "seu_projeto"           # Linha 32
arquivo_excel = "SEU_ARQUIVO.xlsx"    # Linha 306
```

### Passo 3: Testar
```bash
python sistema_hibrido_SEU_PROJETO.py
```

### Passo 4: Integrar ao Dashboard
```python
from sistema_hibrido_SEU_PROJETO import carregar_dados_streamlit

# No seu dashboard:
dados = carregar_dados_streamlit("arquivo.xlsx")
```

## 📊 Exemplo de Uso

```python
import streamlit as st
from sistema_hibrido_meu_projeto import carregar_dados_streamlit

def main():
    st.title("Meu Dashboard")
    
    # Carregamento ultra-rápido!
    dados = carregar_dados_streamlit("meus_dados.xlsx")
    
    st.dataframe(dados)

if __name__ == "__main__":
    main()
```

## 🔧 Personalização

### Normalização de Dados
Edite a função `normalizar_nome_cliente()` para suas regras:

```python
def normalizar_nome_cliente(self, nome):
    nome_limpo = str(nome).strip().upper()
    
    # Suas regras aqui:
    if 'EMPRESA1' in nome_limpo:
        return 'EMPRESA1 PADRÃO'
    
    return nome_limpo
```

### Cache por Período
```python
@st.cache_data(ttl=3600)  # 1 hora
# ou
@st.cache_data(ttl=86400)  # 24 horas
```

## 📈 Resultados Esperados

| Métrica | Antes | Depois | Melhoria |
|---------|-------|--------|----------|
| **Tempo de carregamento** | 30-60s | 2-5s | ~90% ⬇️ |
| **Colunas no exemplo** | 180 | 23 | 87% ⬇️ |
| **Uso de memória** | Alto | Baixo | ~70% ⬇️ |
| **Travamentos** | Frequentes | Zero | 100% ⬇️ |

## 🛠️ Dependências

```bash
pip install pandas numpy pyarrow streamlit openpyxl plotly
```

## 📞 Suporte

Para dúvidas, consulte:
- **Documentação completa**: `IMPLEMENTACAO_SISTEMA_HIBRIDO_CARREGAMENTO.md`
- **Exemplo funcionando**: Projeto "Troca de Notas Terloc"

---

**Desenvolvido com sucesso no projeto Troca de Notas Terloc (2025)** 🎯