"""
📊 EXEMPLO DE DASHBOARD COM SISTEMA HÍBRIDO
===========================================
Template de dashboard Streamlit usando o sistema híbrido de carregamento

INSTRUÇÕES:
1. Copie este arquivo para seu projeto
2. Renomeie para: dashboard_[SEU_PROJETO].py
3. Altere as configurações marcadas com "# ALTERAR"
4. Execute: streamlit run dashboard_[SEU_PROJETO].py
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta

# ALTERAR: Importar seu sistema híbrido
# from TEMPLATE_sistema_hibrido_carregamento import carregar_dados_streamlit
# Para funcionar, descomente a linha acima e comente a de baixo:
from sistema_hibrido_terloc import carregar_dados_streamlit  # TEMPORÁRIO PARA EXEMPLO

def configurar_pagina():
    """Configuração da página Streamlit"""
    st.set_page_config(
        page_title="Dashboard do Projeto",  # ALTERAR: Título do seu projeto
        page_icon="📊",
        layout="wide",
        initial_sidebar_state="expanded"
    )

def carregar_dados_projeto():
    """Carrega dados usando o sistema híbrido"""
    # ALTERAR: Caminho do seu arquivo
    arquivo_excel = "PLANILHA TROCA DE NOTA TERLOC.xlsx"  # ALTERAR AQUI
    
    try:
        # Carregar dados com cache inteligente
        dados = carregar_dados_streamlit(arquivo_excel, limite_registros=50000)
        
        if dados.empty:
            st.error("❌ Nenhum dado foi carregado!")
            return None
        
        return dados
    
    except Exception as e:
        st.error(f"❌ Erro ao carregar dados: {e}")
        return None

def criar_metricas_principais(dados):
    """Cria métricas principais do dashboard"""
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_registros = len(dados)
        st.metric("📊 Total de Registros", f"{total_registros:,}")
    
    with col2:
        # ALTERAR: Adaptar para suas colunas
        if 'CLIENTE' in dados.columns:
            clientes_unicos = dados['CLIENTE'].nunique()
            st.metric("👥 Clientes Únicos", f"{clientes_unicos:,}")
        else:
            st.metric("👥 Clientes Únicos", "N/A")
    
    with col3:
        # ALTERAR: Adaptar para suas colunas
        colunas_valor = [col for col in dados.columns if 'VALOR' in col.upper()]
        if colunas_valor:
            valor_total = dados[colunas_valor[0]].sum()
            st.metric("💰 Valor Total", f"R$ {valor_total:,.2f}")
        else:
            st.metric("💰 Valor Total", "N/A")
    
    with col4:
        colunas_disponiveis = len(dados.columns)
        st.metric("📋 Colunas", f"{colunas_disponiveis}")

def criar_filtros_sidebar(dados):
    """Cria filtros na sidebar"""
    st.sidebar.header("🔍 Filtros")
    
    filtros = {}
    
    # ALTERAR: Adaptar filtros para suas colunas
    
    # Filtro de data (busca automática por colunas de data)
    colunas_data = [col for col in dados.columns if 'DATA' in col.upper()]
    if colunas_data:
        col_data = colunas_data[0]  # Primeira coluna de data encontrada
        
        if dados[col_data].dtype == 'datetime64[ns]':
            data_min = dados[col_data].min().date()
            data_max = dados[col_data].max().date()
            
            filtros['data_inicio'] = st.sidebar.date_input(
                "📅 Data Início",
                value=data_min,
                min_value=data_min,
                max_value=data_max
            )
            
            filtros['data_fim'] = st.sidebar.date_input(
                "📅 Data Fim",
                value=data_max,
                min_value=data_min,
                max_value=data_max
            )
    
    # Filtro de cliente
    if 'CLIENTE' in dados.columns:
        clientes_unicos = sorted(dados['CLIENTE'].dropna().unique())
        filtros['clientes'] = st.sidebar.multiselect(
            "👥 Clientes",
            options=clientes_unicos,
            default=[]
        )
    
    # ALTERAR: Adicionar mais filtros conforme necessário
    # Exemplo:
    # if 'STATUS' in dados.columns:
    #     status_unicos = sorted(dados['STATUS'].dropna().unique())
    #     filtros['status'] = st.sidebar.multiselect(
    #         "📋 Status",
    #         options=status_unicos,
    #         default=[]
    #     )
    
    return filtros

def aplicar_filtros(dados, filtros):
    """Aplica filtros aos dados"""
    dados_filtrados = dados.copy()
    
    # Aplicar filtro de data
    if 'data_inicio' in filtros and 'data_fim' in filtros:
        colunas_data = [col for col in dados.columns if 'DATA' in col.upper()]
        if colunas_data:
            col_data = colunas_data[0]
            if dados[col_data].dtype == 'datetime64[ns]':
                dados_filtrados = dados_filtrados[
                    (dados_filtrados[col_data].dt.date >= filtros['data_inicio']) &
                    (dados_filtrados[col_data].dt.date <= filtros['data_fim'])
                ]
    
    # Aplicar filtro de clientes
    if 'clientes' in filtros and filtros['clientes']:
        dados_filtrados = dados_filtrados[
            dados_filtrados['CLIENTE'].isin(filtros['clientes'])
        ]
    
    # ALTERAR: Aplicar outros filtros
    
    return dados_filtrados

def criar_graficos(dados):
    """Cria gráficos principais"""
    
    # ALTERAR: Adaptar gráficos para seus dados
    
    # Gráfico 1: Top 10 Clientes (se existir coluna CLIENTE)
    if 'CLIENTE' in dados.columns:
        st.subheader("📊 Top 10 Clientes")
        
        # Contar registros por cliente
        top_clientes = dados['CLIENTE'].value_counts().head(10)
        
        fig_clientes = px.bar(
            x=top_clientes.values,
            y=top_clientes.index,
            orientation='h',
            title="Número de Registros por Cliente",
            labels={'x': 'Quantidade', 'y': 'Cliente'}
        )
        fig_clientes.update_layout(height=400)
        st.plotly_chart(fig_clientes, use_container_width=True)
    
    # Gráfico 2: Evolução temporal (se existir coluna de data)
    colunas_data = [col for col in dados.columns if 'DATA' in col.upper()]
    if colunas_data:
        col_data = colunas_data[0]
        
        if dados[col_data].dtype == 'datetime64[ns]':
            st.subheader("📈 Evolução Temporal")
            
            # Agrupar por mês
            dados_tempo = dados.copy()
            dados_tempo['Mês'] = dados_tempo[col_data].dt.to_period('M')
            evolucao = dados_tempo.groupby('Mês').size()
            
            fig_tempo = px.line(
                x=evolucao.index.astype(str),
                y=evolucao.values,
                title="Registros por Mês",
                labels={'x': 'Mês', 'y': 'Quantidade'}
            )
            st.plotly_chart(fig_tempo, use_container_width=True)
    
    # ALTERAR: Adicionar mais gráficos conforme necessário

def criar_tabela_dados(dados):
    """Cria tabela com os dados"""
    st.subheader("📋 Dados Detalhados")
    
    # Opções de visualização
    col1, col2 = st.columns([1, 1])
    
    with col1:
        num_registros = st.selectbox(
            "Número de registros a exibir:",
            options=[10, 25, 50, 100, 500],
            index=1
        )
    
    with col2:
        # ALTERAR: Adaptar colunas para seu projeto
        colunas_disponiveis = list(dados.columns)
        colunas_selecionadas = st.multiselect(
            "Colunas a exibir:",
            options=colunas_disponiveis,
            default=colunas_disponiveis[:5]  # Primeiras 5 colunas
        )
    
    if colunas_selecionadas:
        st.dataframe(
            dados[colunas_selecionadas].head(num_registros),
            use_container_width=True
        )
        
        # Botão para download
        csv = dados[colunas_selecionadas].to_csv(index=False)
        st.download_button(
            label="📥 Download CSV",
            data=csv,
            file_name=f"dados_projeto_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv"
        )

def main():
    """Função principal do dashboard"""
    configurar_pagina()
    
    # Título
    st.title("📊 Dashboard do Projeto")  # ALTERAR: Seu título
    st.markdown("---")
    
    # Carregar dados
    with st.spinner("🔄 Carregando dados..."):
        dados = carregar_dados_projeto()
    
    if dados is None:
        st.stop()
    
    # Mostrar status do carregamento
    st.success(f"✅ Dados carregados: {len(dados):,} registros, {len(dados.columns)} colunas")
    
    # Métricas principais
    criar_metricas_principais(dados)
    st.markdown("---")
    
    # Filtros
    filtros = criar_filtros_sidebar(dados)
    dados_filtrados = aplicar_filtros(dados, filtros)
    
    # Mostrar dados filtrados
    if len(dados_filtrados) != len(dados):
        st.info(f"🔍 Dados filtrados: {len(dados_filtrados):,} de {len(dados):,} registros")
    
    # Gráficos
    if len(dados_filtrados) > 0:
        criar_graficos(dados_filtrados)
        st.markdown("---")
        
        # Tabela de dados
        criar_tabela_dados(dados_filtrados)
    else:
        st.warning("⚠️ Nenhum registro encontrado com os filtros selecionados.")
    
    # Rodapé
    st.markdown("---")
    st.markdown(f"*Dashboard atualizado em: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}*")

if __name__ == "__main__":
    main()