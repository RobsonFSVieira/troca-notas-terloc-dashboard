import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from datetime import datetime
import re

# Configuração da página
st.set_page_config(
    page_title="Dashboard Troca de Notas TERLOC",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personalizado
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
        font-weight: bold;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
    }
    .info-box {
        background-color: #e8f4fd;
        padding: 1rem;
        border-radius: 0.5rem;
        border: 1px solid #1f77b4;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_data
def carregar_dados():
    """Carrega e processa os dados da planilha"""
    try:
        dados = pd.read_excel("PLANILHA TROCA DE NOTA TERLOC.xlsx")
        
        # Limpar dados
        dados_limpos = dados[['TERLOC', 'E-MAIL']].copy()
        dados_limpos = dados_limpos.dropna(subset=['TERLOC'])
        
        # Adicionar informações derivadas
        dados_limpos['TEM_EMAIL'] = dados_limpos['E-MAIL'].notna()
        dados_limpos['DOMINIO_EMAIL'] = dados_limpos['E-MAIL'].str.extract(r'@(.+)')
        
        # Categorizar TERLOCs
        def categorizar_terloc(nome):
            if pd.isna(nome):
                return 'Sem categoria'
            nome = str(nome).upper()
            if 'EXP' in nome or 'EXPEDI' in nome:
                return 'Expedição'
            elif any(word in nome for word in ['COMPRAS', 'COMPRA']):
                return 'Compras'
            elif any(word in nome for word in ['VENDAS', 'VENDA']):
                return 'Vendas'
            elif any(word in nome for word in ['ADMIN', 'ADMINISTRA']):
                return 'Administrativo'
            else:
                return 'Operacional'
        
        dados_limpos['CATEGORIA'] = dados_limpos['TERLOC'].apply(categorizar_terloc)
        
        return dados_limpos
    except Exception as e:
        st.error(f"Erro ao carregar dados: {str(e)}")
        return pd.DataFrame()

def exibir_metricas_principais(dados):
    """Exibe as métricas principais em cards"""
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="📋 Total de TERLOCs",
            value=len(dados),
            delta=None
        )
    
    with col2:
        emails_preenchidos = dados['TEM_EMAIL'].sum()
        st.metric(
            label="📧 E-mails Cadastrados",
            value=emails_preenchidos,
            delta=f"{emails_preenchidos/len(dados)*100:.1f}% do total"
        )
    
    with col3:
        emails_faltando = len(dados) - emails_preenchidos
        st.metric(
            label="⚠️ E-mails Faltando",
            value=emails_faltando,
            delta=f"{emails_faltando/len(dados)*100:.1f}% do total"
        )
    
    with col4:
        dominios_unicos = dados['DOMINIO_EMAIL'].nunique()
        st.metric(
            label="🌐 Domínios Únicos",
            value=dominios_unicos,
            delta=None
        )

def criar_grafico_categorias(dados):
    """Cria gráfico de distribuição por categorias"""
    dist_categorias = dados['CATEGORIA'].value_counts()
    
    fig = px.pie(
        values=dist_categorias.values,
        names=dist_categorias.index,
        title="Distribuição de TERLOCs por Categoria",
        color_discrete_sequence=px.colors.qualitative.Set3
    )
    
    fig.update_traces(textposition='inside', textinfo='percent+label')
    fig.update_layout(height=400)
    
    return fig

def criar_grafico_emails(dados):
    """Cria gráfico de status dos e-mails"""
    status_email = dados['TEM_EMAIL'].value_counts()
    labels = ['E-mail Cadastrado', 'E-mail Faltando']
    colors = ['#2ecc71', '#e74c3c']
    
    fig = go.Figure(data=[go.Bar(
        x=labels,
        y=[status_email.get(True, 0), status_email.get(False, 0)],
        marker_color=colors,
        text=[status_email.get(True, 0), status_email.get(False, 0)],
        textposition='auto',
    )])
    
    fig.update_layout(
        title="Status dos E-mails Cadastrados",
        xaxis_title="Status",
        yaxis_title="Quantidade",
        height=400
    )
    
    return fig

def criar_tabela_detalhada(dados, filtro_categoria=None, filtro_email=None):
    """Cria tabela detalhada com filtros"""
    dados_filtrados = dados.copy()
    
    if filtro_categoria and filtro_categoria != 'Todas':
        dados_filtrados = dados_filtrados[dados_filtrados['CATEGORIA'] == filtro_categoria]
    
    if filtro_email == 'Com E-mail':
        dados_filtrados = dados_filtrados[dados_filtrados['TEM_EMAIL'] == True]
    elif filtro_email == 'Sem E-mail':
        dados_filtrados = dados_filtrados[dados_filtrados['TEM_EMAIL'] == False]
    
    # Preparar dados para exibição
    tabela_exibicao = dados_filtrados[['TERLOC', 'E-MAIL', 'CATEGORIA']].copy()
    tabela_exibicao['STATUS_EMAIL'] = tabela_exibicao['E-MAIL'].apply(
        lambda x: '✅ Cadastrado' if pd.notna(x) else '❌ Faltando'
    )
    
    return tabela_exibicao

def gerar_relatorio_texto(dados):
    """Gera relatório em texto"""
    total_terlocs = len(dados)
    emails_cadastrados = dados['TEM_EMAIL'].sum()
    emails_faltando = total_terlocs - emails_cadastrados
    taxa_completude = (emails_cadastrados / total_terlocs) * 100
    
    dist_categorias = dados['CATEGORIA'].value_counts()
    
    relatorio = f"""
# RELATÓRIO DE ANÁLISE - TROCA DE NOTAS TERLOC
**Data da Análise:** {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}

## RESUMO EXECUTIVO
- **Total de TERLOCs cadastrados:** {total_terlocs}
- **E-mails cadastrados:** {emails_cadastrados} ({taxa_completude:.1f}%)
- **E-mails faltando:** {emails_faltando} ({100-taxa_completude:.1f}%)

## DISTRIBUIÇÃO POR CATEGORIA
"""
    
    for categoria, quantidade in dist_categorias.items():
        percentual = (quantidade / total_terlocs) * 100
        relatorio += f"- **{categoria}:** {quantidade} TERLOCs ({percentual:.1f}%)\n"
    
    relatorio += f"""

## ANÁLISE DE COMPLETUDE
A taxa de completude dos e-mails é de **{taxa_completude:.1f}%**, indicando que:
"""
    
    if taxa_completude >= 90:
        relatorio += "- ✅ **Excelente:** A maioria dos TERLOCs possui e-mail cadastrado."
    elif taxa_completude >= 70:
        relatorio += "- ⚠️ **Bom:** A maioria dos TERLOCs possui e-mail, mas ainda há melhorias possíveis."
    else:
        relatorio += "- ❌ **Atenção:** Há uma quantidade significativa de TERLOCs sem e-mail cadastrado."
    
    relatorio += f"""

## RECOMENDAÇÕES
1. **Completar cadastros:** Priorizar o cadastro dos {emails_faltando} e-mails faltantes.
2. **Validação:** Verificar se todos os e-mails estão ativos e corretos.
3. **Padronização:** Manter o padrão @grupocesari.com.br para todos os e-mails.
4. **Atualização:** Estabelecer processo regular de atualização dos dados.
"""
    
    return relatorio

def main():
    # Cabeçalho
    st.markdown('<h1 class="main-header">📊 Dashboard Troca de Notas TERLOC</h1>', unsafe_allow_html=True)
    
    # Carregar dados
    dados = carregar_dados()
    
    if dados.empty:
        st.error("Não foi possível carregar os dados. Verifique se o arquivo Excel está no diretório correto.")
        return
    
    # Sidebar com filtros
    st.sidebar.header("🔍 Filtros e Configurações")
    
    # Filtro por categoria
    categorias = ['Todas'] + list(dados['CATEGORIA'].unique())
    filtro_categoria = st.sidebar.selectbox("Filtrar por Categoria:", categorias)
    
    # Filtro por status de e-mail
    status_opcoes = ['Todos', 'Com E-mail', 'Sem E-mail']
    filtro_email = st.sidebar.selectbox("Filtrar por Status de E-mail:", status_opcoes)
    
    # Seção de métricas principais
    st.markdown("## 📈 Métricas Principais")
    exibir_metricas_principais(dados)
    
    # Seção de gráficos
    st.markdown("## 📊 Visualizações")
    
    col1, col2 = st.columns(2)
    
    with col1:
        fig_categorias = criar_grafico_categorias(dados)
        st.plotly_chart(fig_categorias, use_container_width=True)
    
    with col2:
        fig_emails = criar_grafico_emails(dados)
        st.plotly_chart(fig_emails, use_container_width=True)
    
    # Tabela detalhada
    st.markdown("## 📋 Dados Detalhados")
    
    tabela_filtrada = criar_tabela_detalhada(dados, filtro_categoria, filtro_email)
    
    st.dataframe(
        tabela_filtrada,
        use_container_width=True,
        hide_index=True,
        column_config={
            "TERLOC": "TERLOC",
            "E-MAIL": "E-mail",
            "CATEGORIA": "Categoria",
            "STATUS_EMAIL": "Status"
        }
    )
    
    # Informações adicionais
    st.markdown("## ℹ️ Informações Adicionais")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown('<div class="info-box">', unsafe_allow_html=True)
        st.markdown("**📧 E-mails por Domínio**")
        dominios = dados['DOMINIO_EMAIL'].value_counts()
        for dominio, count in dominios.items():
            if pd.notna(dominio):
                st.write(f"• {dominio}: {count}")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="info-box">', unsafe_allow_html=True)
        st.markdown("**📊 TERLOCs sem E-mail**")
        sem_email = dados[~dados['TEM_EMAIL']]['TERLOC'].head(10).tolist()
        for terloc in sem_email:
            st.write(f"• {terloc}")
        if len(dados[~dados['TEM_EMAIL']]) > 10:
            st.write(f"... e mais {len(dados[~dados['TEM_EMAIL']]) - 10}")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col3:
        st.markdown('<div class="info-box">', unsafe_allow_html=True)
        st.markdown("**📈 Estatísticas Rápidas**")
        st.write(f"• Maior categoria: {dados['CATEGORIA'].value_counts().index[0]}")
        st.write(f"• Taxa de completude: {(dados['TEM_EMAIL'].sum()/len(dados)*100):.1f}%")
        st.write(f"• TERLOCs únicos: {dados['TERLOC'].nunique()}")
        st.write(f"• E-mails únicos: {dados['E-MAIL'].nunique()}")
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Seção de relatório
    st.markdown("## 📄 Relatório Completo")
    
    with st.expander("Ver Relatório Detalhado"):
        relatorio = gerar_relatorio_texto(dados)
        st.markdown(relatorio)
        
        # Botão para download do relatório
        st.download_button(
            label="📥 Baixar Relatório (TXT)",
            data=relatorio,
            file_name=f"relatorio_terloc_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
            mime="text/plain"
        )
    
    # Footer
    st.markdown("---")
    st.markdown("*Dashboard desenvolvido para análise da planilha Troca de Notas TERLOC*")

if __name__ == "__main__":
    main()