import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

# Configuração da página
st.set_page_config(
    page_title="Dashboard Gaps TERLOC",
    page_icon="📊", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# Função para carregar dados - SIMPLIFICADA
@st.cache_data(ttl=600)
def carregar_dados(limite_registros=10000):
    """Carrega dados da planilha TERLOC"""
    try:
        arquivo_excel = 'PLANILHA TROCA DE NOTA TERLOC.xlsx'
        
        st.info(f"⚡ Carregando {limite_registros:,} registros...")
        
        df = pd.read_excel(
            arquivo_excel, 
            sheet_name='PLANILHA ÚNICA', 
            nrows=limite_registros
        )
        
        # Identificar processos completos (simplificado)
        colunas_tempo = [col for col in df.columns if any(termo in col.upper() for termo in ['HORA', 'DATA', 'TICKET', 'LIBERAÇÃO'])]
        
        # Contar campos preenchidos
        df['campos_preenchidos'] = df[colunas_tempo].notna().sum(axis=1)
        df['processo_completo'] = df['campos_preenchidos'] >= len(colunas_tempo) * 0.6  # 60% preenchido
        
        return df
        
    except Exception as e:
        st.error(f"Erro ao carregar dados: {e}")
        return None

def main():
    st.title("📊 Dashboard Gaps TERLOC - FOCO NOS TEMPOS")
    st.markdown("### ⏱️ Análise de Tempos Entre Etapas do Processo")
    
    # Sidebar com filtros ESSENCIAIS
    st.sidebar.title("🔧 Filtros")
    
    # Volume de dados
    limite_registros = st.sidebar.selectbox(
        "Registros para análise:",
        [10000, 25000, 50000, 100000],
        index=0
    )
    
    # Carregar dados
    df = carregar_dados(limite_registros)
    if df is None:
        st.error("❌ Não foi possível carregar os dados")
        return
    
    # Filtros por período
    st.sidebar.markdown("### 📅 Período")
    if 'DATA' in df.columns:
        df['data_convertida'] = pd.to_datetime(df['DATA'], errors='coerce')
        datas_validas = df['data_convertida'].dropna()
        
        if len(datas_validas) > 0:
            data_min = datas_validas.min().date()
            data_max = datas_validas.max().date()
            
            col1, col2 = st.sidebar.columns(2)
            with col1:
                data_inicio = st.date_input("De:", value=data_min)
            with col2:
                data_fim = st.date_input("Até:", value=data_max)
            
            # Aplicar filtro
            mask_periodo = (df['data_convertida'].dt.date >= data_inicio) & (df['data_convertida'].dt.date <= data_fim)
            df = df[mask_periodo]
    
    # Filtro por cliente
    st.sidebar.markdown("### 👥 Cliente")
    if 'CLIENTE' in df.columns:
        clientes = sorted(df['CLIENTE'].dropna().unique())
        cliente_selecionado = st.sidebar.selectbox(
            "Selecionar:",
            ["Todos"] + clientes
        )
        
        if cliente_selecionado != "Todos":
            df = df[df['CLIENTE'] == cliente_selecionado]
    
    # ANÁLISE PRINCIPAL - GAPS ENTRE ETAPAS
    st.markdown("## 🎯 **GAPS ENTRE ETAPAS - APENAS PROCESSOS COMPLETOS**")
    
    # Usar apenas processos completos
    df_completos = df[df['processo_completo'] == True].copy()
    
    st.info(f"📊 Analisando {len(df_completos):,} processos COMPLETOS de {len(df):,} totais")
    
    if len(df_completos) == 0:
        st.error("❌ **Nenhum processo completo encontrado!**")
        st.info("💡 **Dicas:**")
        st.text("• Aumente o número de registros")
        st.text("• Verifique os filtros aplicados")
        st.text("• Revise os dados de entrada")
        return
    
    # Identificar colunas de tempo disponíveis
    colunas = list(df_completos.columns)
    
    # Buscar colunas específicas
    hora_ticket = None
    hora_nf_venda = None
    hora_liberacao = None
    
    for col in colunas:
        col_upper = col.upper()
        if 'TICKET' in col_upper and 'HORA' in col_upper:
            hora_ticket = col
        elif 'RECEBIMENTO' in col_upper and 'VENDA' in col_upper and 'HORA' in col_upper:
            hora_nf_venda = col
        elif 'LIBERAÇÃO' in col_upper and 'HORA' in col_upper:
            hora_liberacao = col
    
    # Mostrar colunas identificadas
    st.markdown("### 🔍 **Colunas Identificadas Automaticamente:**")
    col_info1, col_info2, col_info3 = st.columns(3)
    
    with col_info1:
        if hora_ticket:
            st.success(f"✅ **Hora Ticket:** {hora_ticket}")
        else:
            st.error("❌ **Hora Ticket:** Não encontrada")
    
    with col_info2:
        if hora_nf_venda:
            st.success(f"✅ **Hora NF Venda:** {hora_nf_venda}")
        else:
            st.error("❌ **Hora NF Venda:** Não encontrada")
    
    with col_info3:
        if hora_liberacao:
            st.success(f"✅ **Hora Liberação:** {hora_liberacao}")
        else:
            st.error("❌ **Hora Liberação:** Não encontrada")
    
    # Calcular gaps
    gaps_calculados = {}
    
    # Gap 1: Cliente - Tempo para enviar NF
    if hora_ticket and hora_nf_venda:
        try:
            # Converter para datetime
            base_date = pd.Timestamp('2024-01-01')
            
            dt_ticket = pd.to_datetime(base_date.strftime('%Y-%m-%d') + ' ' + df_completos[hora_ticket].astype(str), errors='coerce')
            dt_nf = pd.to_datetime(base_date.strftime('%Y-%m-%d') + ' ' + df_completos[hora_nf_venda].astype(str), errors='coerce')
            
            # Calcular diferença
            diferenca = (dt_nf - dt_ticket).dt.total_seconds() / 3600
            diferenca = diferenca.where(diferenca >= 0, diferenca + 24)  # Ajustar para horários que cruzam meia-noite
            
            dados_validos = diferenca.dropna()
            
            if len(dados_validos) > 0:
                gaps_calculados['Gap Cliente (Envio NF Venda)'] = {
                    'tempo_medio': dados_validos.mean(),
                    'tempo_maximo': dados_validos.max(),
                    'tempo_minimo': dados_validos.min(),
                    'registros': len(dados_validos),
                    'dados': dados_validos
                }
        except Exception as e:
            st.warning(f"⚠️ Erro no Gap Cliente: {str(e)}")
    
    # Gap 2: Pátio - Tempo de liberação
    if hora_nf_venda and hora_liberacao:
        try:
            base_date = pd.Timestamp('2024-01-01')
            
            dt_nf = pd.to_datetime(base_date.strftime('%Y-%m-%d') + ' ' + df_completos[hora_nf_venda].astype(str), errors='coerce')
            dt_liberacao = pd.to_datetime(base_date.strftime('%Y-%m-%d') + ' ' + df_completos[hora_liberacao].astype(str), errors='coerce')
            
            diferenca = (dt_liberacao - dt_nf).dt.total_seconds() / 3600
            diferenca = diferenca.where(diferenca >= 0, diferenca + 24)
            
            dados_validos = diferenca.dropna()
            
            if len(dados_validos) > 0:
                gaps_calculados['Gap Pátio (Liberação)'] = {
                    'tempo_medio': dados_validos.mean(),
                    'tempo_maximo': dados_validos.max(), 
                    'tempo_minimo': dados_validos.min(),
                    'registros': len(dados_validos),
                    'dados': dados_validos
                }
        except Exception as e:
            st.warning(f"⚠️ Erro no Gap Pátio: {str(e)}")
    
    # EXIBIR RESULTADOS DOS GAPS
    if gaps_calculados:
        st.markdown("## 🏆 **MÉTRICAS PRINCIPAIS - GAPS CALCULADOS**")
        
        # Métricas em destaque
        cols = st.columns(len(gaps_calculados))
        
        for idx, (gap_nome, dados) in enumerate(gaps_calculados.items()):
            with cols[idx]:
                tempo_medio = dados['tempo_medio']
                tempo_max = dados['tempo_maximo']
                registros = dados['registros']
                
                # Sistema de cores
                if tempo_medio > 24:
                    cor = "🔴"
                    status = "CRÍTICO"
                elif tempo_medio > 12:
                    cor = "🟡"
                    status = "ALTO"
                else:
                    cor = "🟢"
                    status = "OK"
                
                st.metric(
                    label=f"{cor} {gap_nome}",
                    value=f"{tempo_medio:.1f}h",
                    delta=f"Máx: {tempo_max:.1f}h ({status})",
                    help=f"Baseado em {registros:,} processos completos"
                )
        
        # Gráfico comparativo
        if len(gaps_calculados) > 1:
            st.markdown("### 📊 **Comparação de Tempos**")
            
            dados_grafico = []
            for gap_nome, dados in gaps_calculados.items():
                dados_grafico.append({
                    'Etapa': gap_nome.replace('Gap ', ''),
                    'Tempo Médio (h)': dados['tempo_medio'],
                    'Registros': dados['registros']
                })
            
            df_grafico = pd.DataFrame(dados_grafico)
            
            fig = px.bar(
                df_grafico,
                x='Etapa',
                y='Tempo Médio (h)',
                title="⏱️ Tempo Médio por Etapa do Processo",
                text='Tempo Médio (h)',
                color='Tempo Médio (h)',
                color_continuous_scale='RdYlGn_r'
            )
            fig.update_traces(texttemplate='%{text:.1f}h', textposition='outside')
            st.plotly_chart(fig, use_container_width=True)
        
        # Resumo executivo
        st.markdown("### 💼 **RESUMO PARA GERÊNCIA**")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**🚨 GARGALOS IDENTIFICADOS:**")
            for gap_nome, dados in gaps_calculados.items():
                tempo = dados['tempo_medio']
                if tempo > 24:
                    st.error(f"🔴 **{gap_nome}**: {tempo:.1f}h - CRÍTICO!")
                elif tempo > 12:
                    st.warning(f"🟡 **{gap_nome}**: {tempo:.1f}h - ALTO")
                else:
                    st.success(f"🟢 **{gap_nome}**: {tempo:.1f}h - OK")
        
        with col2:
            st.markdown("**📊 MÉTRICAS CHAVE:**")
            
            tempo_total = sum(dados['tempo_medio'] for dados in gaps_calculados.values())
            st.info(f"**Tempo Total Médio:** {tempo_total:.1f} horas")
            
            maior_gargalo = max(gaps_calculados.items(), key=lambda x: x[1]['tempo_medio'])
            st.warning(f"**Maior Gargalo:** {maior_gargalo[0]} ({maior_gargalo[1]['tempo_medio']:.1f}h)")
            
            if len(gaps_calculados) > 1:
                menor_tempo = min(gaps_calculados.items(), key=lambda x: x[1]['tempo_medio'])
                st.success(f"**Processo Mais Eficiente:** {menor_tempo[0]} ({menor_tempo[1]['tempo_medio']:.1f}h)")
    
    
    # TABELA LIMPA DOS DADOS - VERSÃO SIMPLIFICADA DA PLANILHA
    st.markdown("## 📋 **Dados da Planilha TERLOC - Versão Limpa**")
    
    # Selecionar colunas mais importantes para mostrar
    colunas_importantes = []
    
    # Colunas essenciais que sempre tentamos incluir
    colunas_padrao = ['DATA', 'CLIENTE', 'EXPEDIÇÃO']
    
    for col in colunas_padrao:
        if col in df.columns:
            colunas_importantes.append(col)
    
    # Adicionar colunas de tempo identificadas
    if hora_ticket:
        colunas_importantes.append(hora_ticket)
    if hora_nf_venda:
        colunas_importantes.append(hora_nf_venda) 
    if hora_liberacao:
        colunas_importantes.append(hora_liberacao)
    
    # Buscar outras colunas relevantes
    outras_colunas_relevantes = [col for col in df.columns if any(termo in col.upper() for termo in 
                                ['NF', 'NOTA', 'DOCUMENTO', 'PROCESSO', 'STATUS', 'DESTINO'])]
    
    # Adicionar até 3 colunas relevantes adicionais
    for col in outras_colunas_relevantes[:3]:
        if col not in colunas_importantes:
            colunas_importantes.append(col)
    
    # Criar tabela limpa
    if colunas_importantes:
        # Filtrar apenas colunas que existem
        colunas_existentes = [col for col in colunas_importantes if col in df.columns]
        
        # Pegar uma amostra dos dados para exibição
        df_exibir = df[colunas_existentes].copy()
        
        # Limpar e formatar os dados
        for col in df_exibir.columns:
            # Substituir valores nulos por texto mais limpo
            df_exibir[col] = df_exibir[col].fillna('-')
            
            # Limitar texto muito longo
            if df_exibir[col].dtype == 'object':
                df_exibir[col] = df_exibir[col].astype(str).str[:50]
        
        # Controles da tabela
        col1, col2, col3 = st.columns(3)
        
        with col1:
            mostrar_apenas_completos = st.checkbox("📋 Apenas processos completos", value=False)
        
        with col2:
            linhas_exibir = st.selectbox("Linhas a exibir:", [20, 50, 100, 200], index=1)
        
        with col3:
            ordenar_por = st.selectbox("Ordenar por:", ['Ordem original'] + colunas_existentes)
        
        # Aplicar filtros
        df_final = df_exibir.copy()
        
        if mostrar_apenas_completos and 'processo_completo' in df.columns:
            mask_completos = df['processo_completo'] == True
            df_final = df_final[mask_completos]
        
        # Ordenar se solicitado
        if ordenar_por != 'Ordem original' and ordenar_por in df_final.columns:
            df_final = df_final.sort_values(ordenar_por)
        
        # Limitar número de linhas
        df_final = df_final.head(linhas_exibir)
        
        # Exibir informações da tabela
        st.info(f"📊 Exibindo {len(df_final):,} registros de {len(df):,} totais | Colunas: {len(colunas_existentes)}")
        
        # Exibir a tabela
        st.dataframe(
            df_final, 
            use_container_width=True,
            height=400,
            hide_index=False
        )
        
        # Estatísticas rápidas da tabela
        st.markdown("### 📊 **Estatísticas Rápidas da Tabela**")
        
        cols_stats = st.columns(len(colunas_existentes))
        
        for idx, col in enumerate(colunas_existentes):
            with cols_stats[idx]:
                valores_unicos = df[col].nunique()
                valores_preenchidos = df[col].notna().sum()
                percentual_preenchimento = (valores_preenchidos / len(df)) * 100
                
                st.metric(
                    label=col.replace('HORA', 'H.').replace('DATA', 'DT'),
                    value=f"{valores_unicos:,}",
                    delta=f"{percentual_preenchimento:.0f}% preench.",
                    help=f"Valores únicos: {valores_unicos:,}\nPreenchimento: {percentual_preenchimento:.1f}%"
                )
        
        # Download da tabela (opcional)
        if st.button("📥 Preparar Download da Tabela"):
            csv = df_final.to_csv(index=False).encode('utf-8-sig')
            st.download_button(
                label="💾 Baixar Tabela (CSV)",
                data=csv,
                file_name=f'terloc_dados_limpos_{datetime.now().strftime("%Y%m%d_%H%M")}.csv',
                mime='text/csv'
            )
    
    else:
        st.warning("⚠️ Não foi possível identificar colunas importantes para exibir")
        
        # Fallback - mostrar pelo menos algumas colunas
        st.markdown("### 📋 **Primeiras Colunas Disponíveis:**")
        primeiras_colunas = df.columns[:8].tolist()
        df_fallback = df[primeiras_colunas].head(20)
        st.dataframe(df_fallback, use_container_width=True)
    
    # Footer
    st.markdown("---")
    st.markdown("📊 **Dashboard Gaps TERLOC** - Análise Focada em Tempos Entre Etapas")

if __name__ == "__main__":
    main()