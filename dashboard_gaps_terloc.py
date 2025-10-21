import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import os
import warnings
warnings.filterwarnings('ignore')

# Configuração da página
st.set_page_config(
    page_title="Troca de Notas Terloc",
    page_icon="�", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# Função para carregar dados - SIMPLIFICADA
@st.cache_data(ttl=600)
def carregar_dados(limite_registros=10000):
    """Carrega dados da planilha TERLOC"""
    try:
        # Lista de possíveis localizações do arquivo
        possiveis_arquivos = [
            'PLANILHA TROCA DE NOTA TERLOC.xlsx',
            './PLANILHA TROCA DE NOTA TERLOC.xlsx',
            'data/PLANILHA TROCA DE NOTA TERLOC.xlsx',
            os.path.join(os.path.dirname(__file__), 'PLANILHA TROCA DE NOTA TERLOC.xlsx')
        ]
        
        arquivo_excel = None
        for arquivo in possiveis_arquivos:
            if os.path.exists(arquivo):
                arquivo_excel = arquivo
                break
        
        if not arquivo_excel:
            raise FileNotFoundError("Planilha 'PLANILHA TROCA DE NOTA TERLOC.xlsx' não encontrada")
        
        st.info(f"Carregando {limite_registros:,} registros...")
        
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
        
        # Normalizar nomes de clientes
        if 'CLIENTE' in df.columns:
            df['CLIENTE'] = df['CLIENTE'].apply(normalizar_nome_cliente)
        
        return df
        
    except Exception as e:
        st.error(f"Erro ao carregar dados: {e}")
        return None

def normalizar_nome_cliente(nome):
    """
    Normaliza nomes de clientes para resolver inconsistências de digitação
    """
    if pd.isna(nome) or nome == '':
        return 'NÃO INFORMADO'
    
    # Converter para string e limpar
    nome_limpo = str(nome).strip().upper()
    
    # Remover acentos e caracteres especiais desnecessários
    nome_limpo = nome_limpo.replace('Ã', 'A').replace('Õ', 'O').replace('Ç', 'C')
    
    # Dicionário de normalização - mapeamento para nomes padrão
    mapeamento_clientes = {
        # ADUFERTIL - todas as variações
        'ADUFERTIL': 'ADUFERTIL JUNDIAI/SP',
        'ADUFERTIL JUNDIAI': 'ADUFERTIL JUNDIAI/SP',
        'ADUFERTIL JUNDIAÍ': 'ADUFERTIL JUNDIAI/SP',
        'ADUFERTIL JUNDIAI/SP': 'ADUFERTIL JUNDIAI/SP',
        'ADUFERTIL JUNDIAÍ/SP': 'ADUFERTIL JUNDIAI/SP',
        'ADUFERTIL JUNDIAI SP': 'ADUFERTIL JUNDIAI/SP',
        'ADULFERTIL JUNDIAI SP': 'ADUFERTIL JUNDIAI/SP',  # Correção de digitação
        
        # MOSAIC CUBATÃO - todas as variações
        'MOSAIC': 'MOSAIC CUBATAO/SP',
        'MOSAIC CUBATAO': 'MOSAIC CUBATAO/SP', 
        'MOSAIC CUBATÃO': 'MOSAIC CUBATAO/SP',
        'MOSAIC CUBATAO/SP': 'MOSAIC CUBATAO/SP',
        'MOSAIC CUBATÃO/SP': 'MOSAIC CUBATAO/SP',
        'MOSAIC CUBATAO 0099-60/SP': 'MOSAIC CUBATAO/SP',
        'MOSAIC CUBATAO/SP': 'MOSAIC CUBATAO/SP',
        
        # MOSAIC UBERABA - todas as variações  
        'MOSAIC UBERABA': 'MOSAIC UBERABA/MG',
        'MOSAIC UBERABA/MG': 'MOSAIC UBERABA/MG',
        'MOSAIC UBERABA 0110-00/MG': 'MOSAIC UBERABA/MG',
        'MOSAIC UBERABA 0110-00': 'MOSAIC UBERABA/MG',
        
        # ELEKEIROZ - todas as variações
        'ELEKEIROZ': 'ELEKEIROZ VARZEA/SP',
        'ELEKEIROZ VARZEA': 'ELEKEIROZ VARZEA/SP',
        'ELEKEIROZ VÁRZEA': 'ELEKEIROZ VARZEA/SP',
        'ELEKEIROZ VARZEA/SP': 'ELEKEIROZ VARZEA/SP',
        'ELEKEIROZ VÁRZEA/SP': 'ELEKEIROZ VARZEA/SP',
        'ELEKEIROZ / VARZEA - SP': 'ELEKEIROZ VARZEA/SP',
        
        # CSRD - manter como está
        'CSRD': 'CSRD'
    }
    
    # Tentar encontrar correspondência exata primeiro
    if nome_limpo in mapeamento_clientes:
        return mapeamento_clientes[nome_limpo]
    
    # Busca por similaridade (contém parte do nome)
    for chave, valor_padrao in mapeamento_clientes.items():
        if chave in nome_limpo or nome_limpo in chave:
            return valor_padrao
    
    # Se não encontrou correspondência, retorna o nome original limpo
    return nome_limpo

def main():
    st.title("Trocas de Nota Terloc Sólidos")
    st.markdown("### Análise de Tempos Entre Etapas do Processo")
    
    # Volume fixo - sem opção para o usuário
    limite_registros = 50000  # Valor fixo otimizado
    
    # Carregar dados (mais discreto)
    with st.spinner("Carregando dados..."):
        df = carregar_dados(limite_registros)
    if df is None:
        st.error("Erro ao carregar dados")
        return
    
    # TÍTULO PRINCIPAL DOS FILTROS
    st.sidebar.markdown("# Filtros de Análise")
    
    # Calcular períodos disponíveis
    if 'DATA' in df.columns:
        df['data_convertida'] = pd.to_datetime(df['DATA'], errors='coerce')
        datas_validas = df['data_convertida'].dropna()
        
        if len(datas_validas) > 0:
            data_min = datas_validas.min().date()
            data_max = datas_validas.max().date()
            
            # SEÇÃO EXPANSÍVEL - Períodos de Análise
            with st.sidebar.expander("Períodos de Análise", expanded=True):
                # Info box azul - formato dd/mm/aaaa
                st.info(f"Período disponível na base: De {data_min.strftime('%d/%m/%Y')} até {data_max.strftime('%d/%m/%Y')}")
                
                # P1 em linha (lado a lado) - formato dd/mm/aaaa
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown("**Início P1**")
                    data_inicio_p1 = st.date_input("", value=data_min, key="inicio_p1", 
                                                  label_visibility="collapsed", format="DD/MM/YYYY")
                with col2:
                    st.markdown("**Fim P1**")
                    data_fim_p1 = st.date_input("", value=data_max, key="fim_p1", 
                                               label_visibility="collapsed", format="DD/MM/YYYY")
                
                # P2 em linha (lado a lado) - formato dd/mm/aaaa
                col3, col4 = st.columns(2)
                with col3:
                    st.markdown("**Início P2**")
                    data_inicio_p2 = st.date_input("", value=data_min, key="inicio_p2", 
                                                  label_visibility="collapsed", format="DD/MM/YYYY")
                with col4:
                    st.markdown("**Fim P2**") 
                    data_fim_p2 = st.date_input("", value=data_max, key="fim_p2", 
                                               label_visibility="collapsed", format="DD/MM/YYYY")
            
            # APLICAR FILTRO P1 COMO PRINCIPAL (sempre ativo)
            mask_periodo_p1 = (df['data_convertida'].dt.date >= data_inicio_p1) & (df['data_convertida'].dt.date <= data_fim_p1)
            df_filtrado = df[mask_periodo_p1].copy()
            
            # Criar dataset P2 para comparações (quando necessário)
            mask_periodo_p2 = (df['data_convertida'].dt.date >= data_inicio_p2) & (df['data_convertida'].dt.date <= data_fim_p2)
            df_p2 = df[mask_periodo_p2].copy()
            
            # Usar P1 como filtro principal
            df = df_filtrado
            data_inicio = data_inicio_p1
            data_fim = data_fim_p1
    
    # SEÇÃO EXPANSÍVEL - Clientes (multiselect)
    with st.sidebar.expander("Clientes", expanded=True):
        st.markdown("Selecione os clientes")
        
        if 'CLIENTE' in df.columns:
            clientes_todos = sorted(df['CLIENTE'].dropna().unique())
            
            # Multiselect - permite múltiplas seleções
            clientes_selecionados = st.multiselect(
                "",
                clientes_todos,
                default=[],
                key="clientes_filter",
                label_visibility="collapsed"
            )
            
            # Aplicar filtro se houver seleções
            if clientes_selecionados:
                df = df[df['CLIENTE'].isin(clientes_selecionados)]
    
    # SEÇÃO EXPANSÍVEL - Cliente de Venda (destino da carga)
    with st.sidebar.expander("Cliente de Venda", expanded=True):
        st.markdown("Selecione os clientes de venda (destino da carga)")
        
        if 'CLIENTE DE VENDA' in df.columns:
            clientes_venda_todos = sorted(df['CLIENTE DE VENDA'].dropna().unique())
            
            # Multiselect para clientes de venda
            clientes_venda_selecionados = st.multiselect(
                "",
                clientes_venda_todos,
                default=[],
                key="clientes_venda_filter",
                label_visibility="collapsed"
            )
            
            # Aplicar filtro se houver seleções
            if clientes_venda_selecionados:
                df = df[df['CLIENTE DE VENDA'].isin(clientes_venda_selecionados)]
        else:
            st.warning("Coluna 'CLIENTE DE VENDA' não encontrada na planilha")
    
    # SEÇÃO EXPANSÍVEL - Normalização de Clientes (diagnóstico) - Final da sidebar
    with st.sidebar.expander("Normalização de Clientes", expanded=False):
        if 'CLIENTE' in df.columns:
            # Mostrar estatísticas de normalização
            clientes_originais = df['CLIENTE'].value_counts()
            clientes_unicos = len(clientes_originais)
            
            st.markdown(f"**Clientes únicos após normalização:** {clientes_unicos}")
            
            # Mostrar top 5 clientes mais frequentes
            st.markdown("**Top 5 clientes:**")
            for i, (cliente, count) in enumerate(clientes_originais.head(5).items(), 1):
                st.text(f"{i}. {cliente} ({count})")
            
            # Botão para mostrar todos os clientes originais
            if st.button("Ver todos os clientes"):
                st.markdown("**Todos os clientes normalizados:**")
                for cliente in sorted(clientes_originais.index):
                    st.text(f"• {cliente}")
    
    # MÉTRICAS PRINCIPAIS - Padrão de espaçamento
    if 'data_inicio' in locals():
        periodo_str = f"Período 1 (P1): {data_inicio.strftime('%d/%m/%Y')} a {data_fim.strftime('%d/%m/%Y')}"
        st.markdown(f"""
        <h2 style="margin-bottom: 0px; margin-top: 30px;">Visão Geral ({periodo_str})</h2>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <h2 style="margin-bottom: 0px; margin-top: 30px;">Visão Geral</h2>
        """, unsafe_allow_html=True)
    
    # Função para calcular tempo médio e formatar
    def calcular_e_formatar_tempo(df, col_data, col_hora1, col_hora2):
        """Calcula tempo médio entre duas etapas e formata como h:mm:ss"""
        try:
            if col_data in df.columns and col_hora1 in df.columns and col_hora2 in df.columns:
                datetime1 = pd.to_datetime(df[col_data].astype(str) + ' ' + df[col_hora1].astype(str), errors='coerce')
                datetime2 = pd.to_datetime(df[col_data].astype(str) + ' ' + df[col_hora2].astype(str), errors='coerce')
                
                diferenca = (datetime2 - datetime1).dt.total_seconds()  # em segundos
                diferenca_valida = diferenca[diferenca.notna() & (diferenca >= 0) & (diferenca < 24*3600)]
                
                if len(diferenca_valida) > 0:
                    media_segundos = diferenca_valida.mean()
                    horas = int(media_segundos // 3600)
                    minutos = int((media_segundos % 3600) // 60)
                    segundos = int(media_segundos % 60)
                    return f"{horas}:{minutos:02d}:{segundos:02d}"
            return "0:00:00"
        except:
            return "0:00:00"
    
    # Calcular tempos médios reais
    tempo_ticket_senha = calcular_e_formatar_tempo(df, 'DATA  TICKET', 'HORA TICKET', 'HORARIO SENHA ')
    tempo_senha_gate = calcular_e_formatar_tempo(df, 'DATA  TICKET', 'HORARIO SENHA ', 'HORA GATE ')  
    tempo_gate_nf = calcular_e_formatar_tempo(df, 'DATA  TICKET', 'HORA GATE ', 'HORA RECEBIMENTO NF DE VENDA')
    tempo_nf_liberacao = calcular_e_formatar_tempo(df, 'DATA  TICKET', 'HORA RECEBIMENTO NF DE VENDA', 'HORARIO DE LIBERAÇÃO')
    
    # Métricas principais com 5 colunas
    col1, col2, col3, col4, col5 = st.columns(5)
    
    total_atendimentos = len(df)
    
    with col1:
        st.metric(
            "Total de Atendimentos",
            f"{total_atendimentos:,}",
            help="Total de registros no período selecionado"
        )
    
    with col2:
        st.metric(
            "Tempo Médio - Intervalo Ticket e Senha",
            tempo_ticket_senha,
            help="Tempo médio entre ENTRADA (TICKET) e HORA SENHA"
        )
    
    with col3:
        st.metric(
            "Tempo Médio de Espera", 
            tempo_senha_gate,
            help="Tempo médio entre HORA SENHA e HORA GATE"
        )
    
    with col4:
        st.metric(
            "Espera pela Nota de Venda",
            tempo_gate_nf,
            help="Tempo médio entre HORA GATE e HORA NF VENDA"
        )
    
    with col5:
        st.metric(
            "Tempo para Liberação",
            tempo_nf_liberacao,
            help="Tempo médio entre HORA NF VENDA e HORA LIBERAÇÃO"
        )
    
    # Separador discreto e espaçamento
    st.markdown('<div style="margin: 30px 0; border-bottom: 1px solid #e0e0e0;"></div>', unsafe_allow_html=True)
    
    # Se não há dados suficientes, mostrar mensagem mais discreta
    if len(df) == 0:
        st.warning("Poucos dados no período selecionado para análise detalhada")
        return
    
    # Layout empilhado: Top 10 clientes em cima, Atendimentos Diários abaixo (cada um ocupa a linha inteira)
    # Top 10 Movimentação - Clientes (linha inteira)
    st.markdown("""
    <h3 style="margin-bottom: 0px; margin-top: 20px;">Top 10 Movimentação - Clientes</h3>
    """, unsafe_allow_html=True)

    # Gráfico de top clientes (full width)
    if 'CLIENTE' in df.columns:
        top_clientes = df['CLIENTE'].value_counts().head(10).reset_index()
        top_clientes.columns = ['Cliente', 'Quantidade']

        fig_clientes = px.bar(
            top_clientes,
            x='Quantidade',
            y='Cliente',
            orientation='h',
            color='Quantidade',
            color_continuous_scale=[[0, '#1f4e79'], [0.5, '#2e5f8a'], [1, '#4682b4']],
            text='Quantidade'
        )
        fig_clientes.update_traces(
            texttemplate='<b>%{text}</b>', 
            textposition='outside',
            textfont_size=14,
            textfont_color='#1f4e79'
        )
        fig_clientes.update_layout(
            showlegend=False,
            height=400,
            yaxis={
                'categoryorder': 'total ascending',
                'tickfont': {'size': 14, 'color': '#1f4e79'},
                'title_font': {'size': 16, 'color': '#1f4e79'}
            },
            xaxis={
                'tickfont': {'size': 14, 'color': '#1f4e79'},
                'title_font': {'size': 16, 'color': '#1f4e79'}
            },
            margin=dict(l=20, r=80, t=10, b=10)
        )
        st.plotly_chart(fig_clientes, use_container_width=True)

    st.markdown('<div style="height:12px"></div>', unsafe_allow_html=True)

    # Atendimentos Diários (linha inteira, abaixo)
    st.markdown("""
    <h3 style="margin-bottom: 0px; margin-top: 20px;">Atendimentos Diários</h3>
    """, unsafe_allow_html=True)

    # Gráfico de atendimentos por data (full width)
    if 'data_convertida' in df.columns:
        atendimentos_diarios = df.groupby(df['data_convertida'].dt.date).size().reset_index()
        atendimentos_diarios.columns = ['Data', 'Quantidade']

        fig_diarios = px.bar(
            atendimentos_diarios,
            x='Data',
            y='Quantidade',
            title="",
            color='Quantidade',
            color_continuous_scale=[[0, '#1f4e79'], [0.5, '#2e5f8a'], [1, '#4682b4']],
            text='Quantidade'
        )
        fig_diarios.update_traces(
            texttemplate='<b>%{text}</b>', 
            textposition='outside',
            textfont_size=14,
            textfont_color='#1f4e79'
        )
        fig_diarios.update_layout(
            showlegend=False,
            height=420,
            xaxis_title="Data",
            yaxis_title="Quantidade de Atendimentos",
            xaxis={
                'tickfont': {'size': 14, 'color': '#1f4e79'},
                'title_font': {'size': 16, 'color': '#1f4e79'}
            },
            yaxis={
                'tickfont': {'size': 14, 'color': '#1f4e79'},
                'title_font': {'size': 16, 'color': '#1f4e79'},
                'range': [0, atendimentos_diarios['Quantidade'].max() * 1.15]
            },
            margin=dict(l=60, r=30, t=80, b=50)
        )
        st.plotly_chart(fig_diarios, use_container_width=True)
    
    # Separador discreto antes da linha do tempo
    st.markdown('<div style="margin: 30px 0; border-bottom: 1px solid #e0e0e0;"></div>', unsafe_allow_html=True)
    
    # ETAPAS DO PROCESSO - Padrão de espaçamento 
    periodo_texto = f"{data_inicio_p1.strftime('%d/%m/%Y')} a {data_fim_p1.strftime('%d/%m/%Y')}"
    st.markdown(f"""
    <h2 style="margin-bottom: 0px; margin-top: 20px;">Média - Intervalos entre as Etapas - (Período P1: {periodo_texto})</h2>
    """, unsafe_allow_html=True)
    
    # Definir etapas do processo com dados baseados no período
    if len(df) > 0:
        # Pegar uma amostra para mostrar horários reais
        amostra = df.head(1)
        if not amostra.empty and 'data_convertida' in amostra.columns:
            data_base = amostra.iloc[0]['data_convertida'].strftime('%d/%m/%Y')
        else:
            data_base = "20/10/2025"
    else:
        data_base = "20/10/2025"
    
    # CALCULAR MÉDIAS REAIS das etapas com nomes exatos
    def calcular_tempo_medio(df, col_data, col_hora1, col_hora2):
        """Calcula tempo médio entre duas etapas no formato h:mm:ss"""
        try:
            if col_data in df.columns and col_hora1 in df.columns and col_hora2 in df.columns:
                # Combinar data e hora
                datetime1 = pd.to_datetime(df[col_data].astype(str) + ' ' + df[col_hora1].astype(str), errors='coerce')
                datetime2 = pd.to_datetime(df[col_data].astype(str) + ' ' + df[col_hora2].astype(str), errors='coerce')
                
                # Calcular diferença em segundos
                diferenca = (datetime2 - datetime1).dt.total_seconds()
                diferenca_valida = diferenca[diferenca.notna() & (diferenca >= 0) & (diferenca < 24*3600)]
                
                if len(diferenca_valida) > 0:
                    media_segundos = diferenca_valida.mean()
                    horas = int(media_segundos // 3600)
                    minutos = int((media_segundos % 3600) // 60)
                    segundos = int(media_segundos % 60)
                    return f"{horas}:{minutos:02d}:{segundos:02d}"
                        
            return "0:00:00"
        except Exception:
            return "0:00:00"
    
    # Calcular intervalos médios com nomes exatos das colunas
    intervalo1 = calcular_tempo_medio(df, 'DATA  TICKET', 'HORA TICKET', 'HORARIO SENHA ')  # Entrada → Senha
    intervalo2 = calcular_tempo_medio(df, 'DATA  TICKET', 'HORARIO SENHA ', 'HORA GATE ')   # Senha → Gate  
    intervalo3 = calcular_tempo_medio(df, 'DATA  TICKET', 'HORA GATE ', 'HORARIO DE LIBERAÇÃO')  # Gate → Liberação
    
    # Calcular novos intervalos para as 5 etapas
    intervalo1 = calcular_tempo_medio(df, 'DATA  TICKET', 'HORA TICKET', 'HORARIO SENHA ')      # Ticket → Senha
    intervalo2 = calcular_tempo_medio(df, 'DATA  TICKET', 'HORARIO SENHA ', 'HORA GATE ')       # Senha → Gate
    intervalo3 = calcular_tempo_medio(df, 'DATA  TICKET', 'HORA GATE ', 'HORA RECEBIMENTO NF DE VENDA')  # Gate → NF Venda
    intervalo4 = calcular_tempo_medio(df, 'DATA  TICKET', 'HORA RECEBIMENTO NF DE VENDA', 'HORARIO DE LIBERAÇÃO')  # NF Venda → Liberação
    
    # 5 etapas do processo sem horários
    etapas_info = [
        {"num": 1, "nome": "ENTRADA (TICKET)", "intervalo": intervalo1},
        {"num": 2, "nome": "HORA SENHA", "intervalo": intervalo2},
        {"num": 3, "nome": "HORA GATE", "intervalo": intervalo3},
        {"num": 4, "nome": "HORA NF VENDA", "intervalo": intervalo4},
        {"num": 5, "nome": "HORA LIBERAÇÃO", "intervalo": ""}
    ]
    
    # Layout HORIZONTAL - espaçamento mínimo
    st.markdown("""
    <style>
    .etapa-box {
        text-align: center;
        padding: 5px;
        background-color: #f8f9fa;
        border-radius: 10px;
        margin: 2px;
    }
    .etapa-circulo {
        width: 50px;
        height: 50px;
        border-radius: 50%;
        background-color: #28a745;
        color: white;
        display: flex;
        align-items: center;
        justify-content: center;
        margin: 0 auto 8px;
        font-weight: bold;
        font-size: 18px;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # FORÇAR espaçamento ZERO com CSS
    st.markdown("""
    <div style="margin-top: -40px; padding-top: 10px;">
    """, unsafe_allow_html=True)
    
    # Usar 9 colunas para 5 etapas: etapa1, seta1, etapa2, seta2, etapa3, seta3, etapa4, seta4, etapa5
    col1, col2, col3, col4, col5, col6, col7, col8, col9 = st.columns([2, 1, 2, 1, 2, 1, 2, 1, 2])
    
    colunas_etapas = [col1, col3, col5, col7, col9]
    colunas_setas = [col2, col4, col6, col8]
        
    # Renderizar etapas (sem horários)
    for i, etapa in enumerate(etapas_info):
        with colunas_etapas[i]:
            st.markdown(f"""
            <div class="etapa-box">
                <div class="etapa-circulo">{etapa['num']}</div>
                <div style="font-weight: bold; font-size: 12px; color: #333; text-align: center;">
                    {etapa['nome']}
                </div>
            </div>
            """, unsafe_allow_html=True)
    
    # Renderizar setas e intervalos - espaçamento reduzido
    for i in range(len(etapas_info) - 1):
        with colunas_setas[i]:
            st.markdown(f"""
            <div style="text-align: center; margin-top: 15px;">
                <div style="color: #28a745; font-size: 20px;">→</div>
                <div style="color: #28a745; font-weight: bold; font-size: 12px; margin-top: 2px;">
                    {etapas_info[i]['intervalo']}
                </div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)  # Fechar div do container
    
    # Espaçamento adequado após a linha do tempo
    st.markdown('<div style="margin-bottom: 30px;"></div>', unsafe_allow_html=True)
    
    # Identificar colunas para gaps (manter funcionalidade)
    colunas = list(df.columns)
    etapas_encontradas = {}
    
    # Mapear etapas principais
    mapeamento_etapas = {
        'entrada_patio': ('HORA TICKET', 'Entrada no Pátio (Ticket)'),
        'retorno_simbolico': ('SIMBOLICO', 'Retorno Simbólico'),
        'nota_venda': ('NF DE VENDA', 'Nota de Venda'),
        'hora_senha': ('SENHA', 'Hora Senha'),
        'hora_gate': ('GATE', 'Hora Gate'),
        'liberacao': ('LIBERAÇÃO', 'Liberação')
    }
    
    for etapa_id, (busca, nome_etapa) in mapeamento_etapas.items():
        for col in colunas:
            if busca in col.upper() and 'HORA' in col.upper():
                etapas_encontradas[etapa_id] = {'coluna': col, 'nome': nome_etapa}
                break
    
    # Calcular gaps
    gaps_calculados = {}
    
    # Calcular gaps usando as etapas encontradas
    # Gap 1: Cliente - Tempo para enviar NF
    if 'entrada_patio' in etapas_encontradas and 'nota_venda' in etapas_encontradas:
        try:
            col_ticket = etapas_encontradas['entrada_patio']['coluna']
            col_nf = etapas_encontradas['nota_venda']['coluna']
            
            # Converter para datetime
            base_date = pd.Timestamp('2024-01-01')
            
            dt_ticket = pd.to_datetime(base_date.strftime('%Y-%m-%d') + ' ' + df[col_ticket].astype(str), errors='coerce')
            dt_nf = pd.to_datetime(base_date.strftime('%Y-%m-%d') + ' ' + df[col_nf].astype(str), errors='coerce')
            
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
            st.warning(f"Erro no Gap Cliente: {str(e)}")
    
    # Gap 2: Pátio - Tempo de liberação
    if 'nota_venda' in etapas_encontradas and 'liberacao' in etapas_encontradas:
        try:
            col_nf = etapas_encontradas['nota_venda']['coluna']
            col_liberacao = etapas_encontradas['liberacao']['coluna']
            
            base_date = pd.Timestamp('2024-01-01')
            
            dt_nf = pd.to_datetime(base_date.strftime('%Y-%m-%d') + ' ' + df[col_nf].astype(str), errors='coerce')
            dt_liberacao = pd.to_datetime(base_date.strftime('%Y-%m-%d') + ' ' + df[col_liberacao].astype(str), errors='coerce')
            
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
            st.warning(f"Erro no Gap Pátio: {str(e)}")
    
    # EXIBIR RESULTADOS DOS GAPS
    if gaps_calculados:
        # Separador discreto
        st.markdown('<div style="margin: 30px 0; border-bottom: 1px solid #e0e0e0;"></div>', unsafe_allow_html=True)
        
        st.markdown("""
        <h2 style="margin-bottom: 0px; margin-top: 20px;">Métricas Principais - Gaps Calculados</h2>
        """, unsafe_allow_html=True)
        
        # Métricas em destaque
        cols = st.columns(len(gaps_calculados))
        
        for idx, (gap_nome, dados) in enumerate(gaps_calculados.items()):
            with cols[idx]:
                tempo_medio = dados['tempo_medio']
                tempo_max = dados['tempo_maximo']
                registros = dados['registros']
                
                # Sistema de cores
                if tempo_medio > 24:
                    status = "CRÍTICO"
                elif tempo_medio > 12:
                    status = "ALTO"
                else:
                    status = "OK"
                
                st.metric(
                    label=gap_nome,
                    value=f"{tempo_medio:.1f}h",
                    delta=f"Máx: {tempo_max:.1f}h ({status})",
                    help=f"Baseado em {registros:,} processos completos"
                )
        
        # Gráfico comparativo
        if len(gaps_calculados) > 1:
            st.markdown("### **Comparação de Tempos**")
            
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
                title="Tempo Médio por Etapa do Processo",
                text='Tempo Médio (h)',
                color='Tempo Médio (h)',
                color_continuous_scale=[[0, '#1f4e79'], [0.5, '#2e5f8a'], [1, '#4682b4']]
            )
            fig.update_traces(
                texttemplate='<b>%{text:.1f}h</b>', 
                textposition='outside',
                textfont_size=14,
                textfont_color='#1f4e79'
            )
            fig.update_layout(
                title_font={'size': 18, 'color': '#1f4e79'},
                xaxis={
                    'tickfont': {'size': 14, 'color': '#1f4e79'},
                    'title_font': {'size': 16, 'color': '#1f4e79'}
                },
                yaxis={
                    'tickfont': {'size': 14, 'color': '#1f4e79'},
                    'title_font': {'size': 16, 'color': '#1f4e79'},
                    'range': [0, df_grafico['Tempo Médio (h)'].max() * 1.2]
                },
                height=480,
                margin=dict(l=60, r=30, t=100, b=50)
            )
            st.plotly_chart(fig, use_container_width=True)
        
        # Resumo executivo
        st.markdown("### **RESUMO**")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**GARGALOS IDENTIFICADOS:**")
            for gap_nome, dados in gaps_calculados.items():
                tempo = dados['tempo_medio']
                if tempo > 24:
                    st.error(f"**{gap_nome}**: {tempo:.1f}h - CRÍTICO!")
                elif tempo > 12:
                    st.warning(f"**{gap_nome}**: {tempo:.1f}h - ALTO")
                else:
                    st.success(f"**{gap_nome}**: {tempo:.1f}h - OK")
        
        with col2:
            st.markdown("**MÉTRICAS CHAVE:**")
            
            tempo_total = sum(dados['tempo_medio'] for dados in gaps_calculados.values())
            st.info(f"**Tempo Total Médio:** {tempo_total:.1f} horas")
            
            maior_gargalo = max(gaps_calculados.items(), key=lambda x: x[1]['tempo_medio'])
            st.warning(f"**Maior Gargalo:** {maior_gargalo[0]} ({maior_gargalo[1]['tempo_medio']:.1f}h)")
            
            if len(gaps_calculados) > 1:
                menor_tempo = min(gaps_calculados.items(), key=lambda x: x[1]['tempo_medio'])
                st.success(f"**Processo Mais Eficiente:** {menor_tempo[0]} ({menor_tempo[1]['tempo_medio']:.1f}h)")
    
    
    # TABELA LIMPA DOS DADOS - VERSÃO SIMPLIFICADA DA PLANILHA
    # Separador discreto  
    st.markdown('<div style="margin: 30px 0; border-bottom: 1px solid #e0e0e0;"></div>', unsafe_allow_html=True)
    
    st.markdown("""
    <h2 style="margin-bottom: 0px; margin-top: 20px;">Dados da Planilha</h2>
    """, unsafe_allow_html=True)
    
    # Selecionar colunas mais importantes para mostrar
    colunas_importantes = []
    
    # Colunas essenciais que sempre tentamos incluir
    colunas_padrao = ['DATA', 'CLIENTE', 'EXPEDIÇÃO']
    
    for col in colunas_padrao:
        if col in df.columns:
            colunas_importantes.append(col)
    
    # Adicionar colunas de tempo identificadas
    for etapa_id, dados in etapas_encontradas.items():
        if dados['coluna'] not in colunas_importantes:
            colunas_importantes.append(dados['coluna'])
    
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
            mostrar_apenas_completos = st.checkbox("Apenas processos completos", value=False)
        
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
        st.info(f"Exibindo {len(df_final):,} registros de {len(df):,} totais | Colunas: {len(colunas_existentes)}")
        
        # Exibir a tabela
        st.dataframe(
            df_final, 
            use_container_width=True,
            height=400,
            hide_index=False
        )
        
        # Estatísticas rápidas da tabela
        st.markdown("### **Estatísticas Rápidas da Tabela**")
        
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
        if st.button("Preparar Download da Tabela"):
            csv = df_final.to_csv(index=False).encode('utf-8-sig')
            st.download_button(
                label="Baixar Tabela (CSV)",
                data=csv,
                file_name=f'terloc_dados_limpos_{datetime.now().strftime("%Y%m%d_%H%M")}.csv',
                mime='text/csv'
            )
    
    else:
        st.warning("Não foi possível identificar colunas importantes para exibir")
        
        # Fallback - mostrar pelo menos algumas colunas
        st.markdown("### **Primeiras Colunas Disponíveis:**")
        primeiras_colunas = df.columns[:8].tolist()
        df_fallback = df[primeiras_colunas].head(20)
        st.dataframe(df_fallback, use_container_width=True)
    

if __name__ == "__main__":
    main()