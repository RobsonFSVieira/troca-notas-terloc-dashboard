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

# � CARREGAMENTO INTELIGENTE - Monitor de Mudanças + Cache
try:
    from sistema_hibrido_terloc import carregar_dados_streamlit  # interface_upload_streamlit - TEMPORARIAMENTE COMENTADO
    
    @st.cache_data(ttl=7200, show_spinner=False)  # Cache por 2 horas
    def carregar_dados(limite_registros=50000):
        """Carrega dados com sistema híbrido (padrão + upload)"""
        return carregar_dados_streamlit(limite_registros)
        
except ImportError:
    # Fallback para sistema antigo se carregador não estiver disponível
    @st.cache_data(ttl=600)
    def carregar_dados(limite_registros=10000):
        """FALLBACK: Carrega dados da planilha TERLOC (sistema antigo)"""
        try:
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
            
            df = pd.read_excel(arquivo_excel, sheet_name='PLANILHA ÚNICA', nrows=limite_registros)
            
            # Processamento básico
            colunas_tempo = [col for col in df.columns if any(termo in col.upper() for termo in ['HORA', 'DATA', 'TICKET', 'LIBERAÇÃO'])]
            df['campos_preenchidos'] = df[colunas_tempo].notna().sum(axis=1)
            df['processo_completo'] = df['campos_preenchidos'] >= len(colunas_tempo) * 0.6
            
            if 'CLIENTE' in df.columns:
                df['CLIENTE'] = df['CLIENTE'].apply(normalizar_nome_cliente)
            if 'CLIENTE DE VENDA' in df.columns:
                df['CLIENTE DE VENDA'] = df['CLIENTE DE VENDA'].apply(normalizar_cliente_venda)
            
            return df
            
        except Exception as e:
            st.error(f"Erro ao carregar dados: {e}")
            return None

def normalizar_nome_cliente(nome):
    """
    Normaliza nomes de clientes usando correção automática de erros típicos de digitação
    """
    if pd.isna(nome) or nome == '':
        return 'NÃO INFORMADO'
    
    # Converter para string e limpar
    nome_limpo = str(nome).strip().upper()
    
    # Remover acentos e caracteres especiais
    nome_limpo = (nome_limpo.replace('Ã', 'A').replace('Õ', 'O').replace('Ç', 'C')
                            .replace('É', 'E').replace('Ê', 'E').replace('Í', 'I')
                            .replace('Ó', 'O').replace('Ô', 'O').replace('Ú', 'U')
                            .replace('Ù', 'U').replace('Û', 'U').replace('Ü', 'U'))
    
    # CORREÇÃO AUTOMÁTICA DE ERROS DE DIGITAÇÃO
    
    # 1. ELEKEIROZ - Capturar TODAS as variações com erros de digitação
    if any(variacao in nome_limpo for variacao in ['ELEKEIROZ', 'ELEIKEIROZ', 'ELEQUEIROZ', 'ELEQUEIOZ', 'ELKEIROZ']):
        return 'ELEKEIROZ VARZEA/SP'
    
    # 2. ADUFERTIL - Capturar todas as variações
    if any(variacao in nome_limpo for variacao in ['ADUFERTIL', 'ADULFERTIL', 'ADUFETIL', 'ADUFERIL']):
        return 'ADUFERTIL JUNDIAI/SP'
    
    # 3. MOSAIC CUBATÃO
    if 'MOSAIC' in nome_limpo and ('CUBATAO' in nome_limpo or nome_limpo == 'MOSAIC'):
        return 'MOSAIC CUBATAO/SP'
    
    # 4. MOSAIC UBERABA
    if 'MOSAIC' in nome_limpo and 'UBERABA' in nome_limpo:
        return 'MOSAIC UBERABA/MG'
    
    # 5. CSRD
    if 'CSRD' in nome_limpo:
        return 'CSRD'
    
    # Se não encontrou padrão conhecido, retorna normalizado
    return nome_limpo.replace('-', '/').replace('  ', ' ').strip()

def normalizar_cliente_venda(nome):
    """
    Normaliza nomes de clientes de venda usando o arquivo de mapeamento
    """
    if pd.isna(nome) or nome == '':
        return 'NÃO INFORMADO'
    
    # Converter para string e limpar
    nome_limpo = str(nome).strip().upper()
    
    # Dicionário completo baseado no arquivo "Mapeamento de Normalização de Nomes.txt"
    mapeamento_clientes_venda = {
        # ADUBOS ARAGUAIA ANAPOLIS
        'ADUBOS ANAPOLIS': 'ADUBOS ARAGUAIA ANAPOLIS',
        'ADUBOS ARAG. ANAPOLIS /GO': 'ADUBOS ARAGUAIA ANAPOLIS',
        'ADUBOS ARAG. ANAPOLIS/GO': 'ADUBOS ARAGUAIA ANAPOLIS',
        'ADUBOS ARAG. ANAPOLIS/MG': 'ADUBOS ARAGUAIA ANAPOLIS',
        'ADUBOS ARAG.ANAPOLIS/GO': 'ADUBOS ARAGUAIA ANAPOLIS',
        
        # ADUBOS ARAGUAIA CATALÃO
        'ADUBOS ARAG - CATALAO/GO': 'ADUBOS ARAGUAIA CATALÃO',
        'ADUBOS ARAG. CATALAO/GO': 'ADUBOS ARAGUAIA CATALÃO',
        'ADUBOS ARAG. CATALÃO/GO': 'ADUBOS ARAGUAIA CATALÃO',
        'ADUBOS ARAG.CATALAO/GO': 'ADUBOS ARAGUAIA CATALÃO',
        'ADUBOS ARAGUAIA CATALAO/GO': 'ADUBOS ARAGUAIA CATALÃO',
        
        # ADUFERTIL ALFENAS
        'ADUFERTIL - ALFENAS/MG': 'ADUFERTIL ALFENAS',
        'ADUFÉRTIL - ALFENAS/MG': 'ADUFERTIL ALFENAS',
        'ADUFERTIL / ALFENAS': 'ADUFERTIL ALFENAS',
        'ADUFERTIL / ALFENAS/MG': 'ADUFERTIL ALFENAS',
        'ADUFERTIL ALFENAS': 'ADUFERTIL ALFENAS',
        'ADUFERTIL ALFENAS/MG': 'ADUFERTIL ALFENAS',
        'ADULFERTIL ALFENAS/MG': 'ADUFERTIL ALFENAS',
        
        # BONFINOPOLIS
        'BONFINOPOLIS/MG': 'BONFINOPOLIS',
        
        # CAFE BRASIL
        'CAFE BRASIL /MG': 'CAFE BRASIL',
        'CAFE BRASIL/MG': 'CAFE BRASIL',
        
        # COFCO CATANDUVA
        'COFCO - CATANDUVA/SP': 'COFCO CATANDUVA',
        'COFCO CATANDUVA': 'COFCO CATANDUVA',
        'COFCO CATANDUVA/SP': 'COFCO CATANDUVA',
        'COFCO-CATANDUVA': 'COFCO CATANDUVA',
        
        # COFCO MERIDIANO
        'COFCO - MERIDIANO/SP': 'COFCO MERIDIANO',
        'COFCO MERIDIANO': 'COFCO MERIDIANO',
        'COFCO MERIDIANO/SP': 'COFCO MERIDIANO',
        
        # COFCO POTIRENDABA
        'COFCO - POTIRENDABA': 'COFCO POTIRENDABA',
        'COFCO - POTIRENDABA/SP': 'COFCO POTIRENDABA',
        'COFCO POTIRENDA/SP': 'COFCO POTIRENDABA',
        'COFCO POTIRENDABA': 'COFCO POTIRENDABA',
        'COFCO POTIRENDABA/SP': 'COFCO POTIRENDABA',
        'COFCO/POTIRENDABA/SP': 'COFCO POTIRENDABA',
        
        # COFCO SEBASTIANÓPOLIS
        'COFCO - SEBASTIANOPOLIS': 'COFCO SEBASTIANÓPOLIS',
        'COFCO - SEBASTIANOPOLIS/SP': 'COFCO SEBASTIANÓPOLIS',
        'COFCO - SEBASTIANÓPOLIS/SP': 'COFCO SEBASTIANÓPOLIS',
        'COFCO - SEBASTIANPOLIS/SP': 'COFCO SEBASTIANÓPOLIS',
        'COFCO SEBASTIANOPOLIS': 'COFCO SEBASTIANÓPOLIS',
        'COFCO SEBASTIANÓPOLIS/SP': 'COFCO SEBASTIANÓPOLIS',
        
        # EMBRAFOS BARRETOS
        'EMBRAFOS BARRETOS': 'EMBRAFOS BARRETOS',
        
        # EQUILIBRIO ITAPETININGA
        'EQUILIBRIO ITAPETININGA/SP': 'EQUILIBRIO ITAPETININGA',
        'EQUILIBRIO ITAPETININGA04': 'EQUILIBRIO ITAPETININGA',
        
        # FASS NOVA INDEPENDÊNCIA
        'FASS - NOVA INDEPENDENCIA': 'FASS NOVA INDEPENDÊNCIA',
        'FASS - NOVA INDEPENDENCIA/SP': 'FASS NOVA INDEPENDÊNCIA',
        'FASS INDEPENDENCIA': 'FASS NOVA INDEPENDÊNCIA',
        'FASS N.INDEPENDENCIA': 'FASS NOVA INDEPENDÊNCIA',
        'FASS NOVA IND.': 'FASS NOVA INDEPENDÊNCIA',
        'FASS NOVA INDEPEDENCIA': 'FASS NOVA INDEPENDÊNCIA',
        'FASS NOVA INDEPENCIA': 'FASS NOVA INDEPENDÊNCIA',
        'FASS NOVA INDEPENDENCIA': 'FASS NOVA INDEPENDÊNCIA',
        'FASS NOVA INDEPENDÊNCIA': 'FASS NOVA INDEPENDÊNCIA',
        'FASS NOVA INDEPÊNDENCIA': 'FASS NOVA INDEPENDÊNCIA',
        'FASS NOVA INDEPENDENCIA/SP': 'FASS NOVA INDEPENDÊNCIA',
        
        # FASS SERTÃOZINHO
        'FAAS - SERTAOZINHO/SP': 'FASS SERTÃOZINHO',
        'FASS - SERTAOZINHO': 'FASS SERTÃOZINHO',
        'FASS - SERTAOZINHO/SP': 'FASS SERTÃOZINHO',
        'FASS - SERTÃOZINHO/SP': 'FASS SERTÃOZINHO',
        'FASS SERTAOZINHO': 'FASS SERTÃOZINHO',
        'FASS SERTÃOZINHO': 'FASS SERTÃOZINHO',
        'FASS SERTAOZINHO SP': 'FASS SERTÃOZINHO',
        'FASS SERTAOZINHO/SP': 'FASS SERTÃOZINHO',
        'FASS- SERTAOZINHO/SP': 'FASS SERTÃOZINHO',
        'FASS SERTÃOZINHO/SP': 'FASS SERTÃOZINHO',
        'FASS- SERTÃOZINHO/SP': 'FASS SERTÃOZINHO',
        'FASS-SERTAOZINHO/SP': 'FASS SERTÃOZINHO',
        'FASS-SERTÃOZINHO/SP': 'FASS SERTÃOZINHO',
        
        # FERTI SOLO INSUMOS
        'FERTI SOLO INSUMOS AGRICO': 'FERTI SOLO INSUMOS',
        'FERTI SOLO INSUMOS AGRICO/PR': 'FERTI SOLO INSUMOS',
        
        # FERTIBOM CATANDUVA
        'FERTIBOM - CATANDUVA': 'FERTIBOM CATANDUVA',
        'FERTIBOM - CATANDUVA/SP': 'FERTIBOM CATANDUVA',
        'FERTIBOM CATANDUVA': 'FERTIBOM CATANDUVA',
        'FERTIBOM/ CATANDUVA': 'FERTIBOM CATANDUVA',
        'FERTIBOM/CATANDUVA': 'FERTIBOM CATANDUVA',
        
        # IC ARAUCARIA
        'IC ARAUCARIA': 'IC ARAUCARIA',
        
        # ICL JACAREÍ
        'ICL - JACAREI/SP': 'ICL JACAREÍ',
        'ICL - JACAREI/SP - 0013/56': 'ICL JACAREÍ',
        'ICL - JACAREÍ/SP - 0013/56': 'ICL JACAREÍ',
        'ICL JACAREI': 'ICL JACAREÍ',
        'ICL JACAREI 0008/99': 'ICL JACAREÍ',
        'ICL JACAREI- 0008/99': 'ICL JACAREÍ',
        'ICL JACAREI 0013/56': 'ICL JACAREÍ',
        'ICL JACAREI 0013-56 /SP': 'ICL JACAREÍ',
        'ICL JACAREI/SP': 'ICL JACAREÍ',
        'ICL JACAREÍ/SP': 'ICL JACAREÍ',
        'ICL JACAREI/SP - 00008/99': 'ICL JACAREÍ',
        'ICL JACAREI/SP - 0008/99': 'ICL JACAREÍ',
        'ICL JACAREI/SP - 0008-99': 'ICL JACAREÍ',
        'ICL JACAREI/SP - 0013/56': 'ICL JACAREÍ',
        'ICL JACAREÍ/SP - 0013/56': 'ICL JACAREÍ',
        'ICL JACAREI/SP 0008/99': 'ICL JACAREÍ',
        'ICL JACAREI/SP -0013/56': 'ICL JACAREÍ',
        
        # ICL UBERLÂNDIA
        'ICL UBERLANDIA': 'ICL UBERLÂNDIA',
        'ICL UBERLANDIA/MG': 'ICL UBERLÂNDIA',
        'ICL UBERLANDIA/SP': 'ICL UBERLÂNDIA',
        
        # KALIUM
        'KALIUM': 'KALIUM',
        
        # LOYDER OLÍMPIA
        'LOYDER - OLIMPIA/SP': 'LOYDER OLÍMPIA',
        'LOYDER OLIMPIA': 'LOYDER OLÍMPIA',
        'LOYDER OLIMPIA/SP': 'LOYDER OLÍMPIA',
        'LOYDER- OLIMPIA/SP': 'LOYDER OLÍMPIA',
        
        # MAXFOL AGROIND
        'MAXFOL AGRO.IND/SP': 'MAXFOL AGROIND',
        
        # MOSAIC CAJATI
        'MOSAIC P&K - CAJATI': 'MOSAIC CAJATI',
        
        # SAFRA ALFENAS
        'SAFRA ALFENAS': 'SAFRA ALFENAS',
        'SAFRA- ALFENAS': 'SAFRA ALFENAS',
        'SAFRA ALFENAS/MG': 'SAFRA ALFENAS',
        'SAFRA IND ALFENAS': 'SAFRA ALFENAS',
        'SAFRA IND FERT/ALFENAS': 'SAFRA ALFENAS',
        'SAFRA IND. ALFENAS': 'SAFRA ALFENAS',
        'SAFRA IND. ALFENAS/MG': 'SAFRA ALFENAS',
        'SAFRA IND. FERLT/ALFENAS': 'SAFRA ALFENAS',
        'SAFRA IND. FERT/ALFENAS': 'SAFRA ALFENAS',
        'SAFRA IND. FERTL ALFENAS/MG': 'SAFRA ALFENAS',
        'SAFRA IND. FERTL/ALFENAS': 'SAFRA ALFENAS',
        'SAFRA IND.FERTL/ALFENAS': 'SAFRA ALFENAS',
        'SANDRA IND. FERT/ALFENAS': 'SAFRA ALFENAS',
        
        # TERA FERTILIZANTES
        'TERA FERTILIZANTES/MG': 'TERA FERTILIZANTES',
        'TRA FERTILIZANTES/MG': 'TERA FERTILIZANTES',
        
        # USINA SANTA ADÉLIA
        'USINA SANTA ADELEIA/SP': 'USINA SANTA ADÉLIA',
        'USINA SANTA ADELIA S/A': 'USINA SANTA ADÉLIA',
        
        # USINA SÃO MANOEL
        'USINA SÃO MANOEL /SP': 'USINA SÃO MANOEL',
        'USINA SÃO MANOEL/SP': 'USINA SÃO MANOEL',
        'USINA SAO MANUEL': 'USINA SÃO MANOEL',
        'USINA SAO MANUEL/SP': 'USINA SÃO MANOEL',
        'USINA SÃO MANUEL/SP': 'USINA SÃO MANOEL',
    }
    
    # Aplicar mapeamento
    return mapeamento_clientes_venda.get(nome_limpo, nome_limpo)
def main():
    st.title("Trocas de Nota Terloc Sólidos")
    
    # Volume fixo - sem opção para o usuário
    limite_registros = 50000  # Valor fixo otimizado
    
    # Carregar dados (mais discreto)
    with st.spinner("Carregando dados..."):
        df = carregar_dados(limite_registros)
    if df is None:
        st.error("Erro ao carregar dados")
        return
    

    
    # ═══════════════════════════════════════════════════════════════════════════════════
    # 📤 SEÇÃO DE UPLOAD HÍBRIDO - TEMPORARIAMENTE OCULTA
    # ═══════════════════════════════════════════════════════════════════════════════════
    # 
    # Para reativar a funcionalidade de upload de novas planilhas:
    # 1. Descomente a linha abaixo
    # 2. Descomente o import de interface_upload_streamlit na linha 21
    # 3. Descomente a função interface_upload_streamlit() no arquivo sistema_hibrido_terloc.py
    # 4. Descomente o botão "🔄 Atualizar Dados" nas linhas ~380-385
    #
    # interface_upload_streamlit()
    # ═══════════════════════════════════════════════════════════════════════════════════

    # TÍTULO PRINCIPAL DOS FILTROS
    st.sidebar.markdown("# Filtros de Análise")
    
    # Variável padrão do período (será atualizada se houver dados válidos)
    periodo_texto = "Período não definido"
    
    # Inicializar variáveis padrão para datas P2 (evitar erro UnboundLocalError)
    data_inicio_p2 = None
    data_fim_p2 = None
    df_p2 = pd.DataFrame()  # DataFrame vazio por padrão
    
    # Calcular períodos disponíveis
    if 'DATA' in df.columns:
        df['data_convertida'] = pd.to_datetime(df['DATA'], errors='coerce')
        datas_validas = df['data_convertida'].dropna()
        
        if len(datas_validas) > 0:
            data_min = datas_validas.min().date()
            data_max = datas_validas.max().date()
            
            # SEÇÃO EXPANSÍVEL - Períodos de Análise
            with st.sidebar.expander("Períodos de Análise", expanded=True):
                # Info discreta - formato dd/mm/aaaa
                st.caption(f"📊 Dados: {data_min.strftime('%d/%m/%Y')} a {data_max.strftime('%d/%m/%Y')}")
                
                # P1 em linha (lado a lado) - formato dd/mm/aaaa
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown("**Início P1**")
                    data_inicio_p1 = st.date_input("", value=data_min, key="inicio_p1", 
                                                  label_visibility="collapsed", format="DD/MM/YYYY",
                                                  min_value=data_min, max_value=data_max)
                with col2:
                    st.markdown("**Fim P1**")
                    data_fim_p1 = st.date_input("", value=data_max, key="fim_p1", 
                                               label_visibility="collapsed", format="DD/MM/YYYY",
                                               min_value=data_min, max_value=data_max)
                
                #P2 em linha (lado a lado) - formato dd/mm/aaaa
                col3, col4 = st.columns(2)
                with col3:
                    st.markdown("**InícioP2**")
                    data_inicio_p2 = st.date_input("", value=data_min, key="inicio_p2", 
                                                  label_visibility="collapsed", format="DD/MM/YYYY",
                                                  min_value=data_min, max_value=data_max)
                with col4:
                    st.markdown("**FimP2**") 
                    data_fim_p2 = st.date_input("", value=data_max, key="fim_p2", 
                                               label_visibility="collapsed", format="DD/MM/YYYY",
                                               min_value=data_min, max_value=data_max)
            
            # VALIDAÇÃO DAS DATAS
            if data_inicio_p1 > data_fim_p1:
                st.sidebar.error("❌ **P1**: Data de início deve ser menor ou igual à data de fim!")
                st.stop()
            
            if data_inicio_p2 > data_fim_p2:
                st.sidebar.error("❌ **P2**: Data de início deve ser menor ou igual à data de fim!")
                st.stop()
            
            # APLICAR FILTRO P1 COMO PRINCIPAL (sempre ativo)
            mask_periodo_p1 = (df['data_convertida'].dt.date >= data_inicio_p1) & (df['data_convertida'].dt.date <= data_fim_p1)
            df_filtrado = df[mask_periodo_p1].copy()
            
            # Criar datasetP2 para comparações (quando necessário)
            mask_periodo_p2 = (df['data_convertida'].dt.date >= data_inicio_p2) & (df['data_convertida'].dt.date <= data_fim_p2)
            df_p2 = df[mask_periodo_p2].copy()
            
            # Usar P1 como filtro principal
            df = df_filtrado
            data_inicio = data_inicio_p1
            data_fim = data_fim_p1
            
            # Definir texto do período para usar em todos os títulos
            periodo_texto = f"{data_inicio_p1.strftime('%d/%m/%Y')} a {data_fim_p1.strftime('%d/%m/%Y')}"
            
            # VISÃO GERAL - Movida para cima, logo após o título principal
            periodo_str = f"Período 1 (P1): {data_inicio.strftime('%d/%m/%Y')} a {data_fim.strftime('%d/%m/%Y')}"
            st.markdown(f"""
            ### {periodo_str}
            """, unsafe_allow_html=True)
    
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
    
    # ═══════════════════════════════════════════════════════════════════════════════════
    # 🔄 BOTÃO "ATUALIZAR DADOS" - TEMPORARIAMENTE OCULTO
    # ═══════════════════════════════════════════════════════════════════════════════════
    # Para reativar, descomente as linhas abaixo:
    # st.sidebar.markdown("---")  # Separador visual
    # if st.sidebar.button("🔄 Atualizar Dados", help="Força o recarregamento dos dados da planilha com normalização atualizada"):
    #     st.cache_data.clear()
    #     st.rerun()
    # ═══════════════════════════════════════════════════════════════════════════════════
    
    # MÉTRICAS PRINCIPAIS - Padrão de espaçamento
    
    # Função para calcular tempo médio e formatar
    def calcular_e_formatar_tempo(df, col_data, col_hora1, col_hora2):
        """Calcula tempo médio entre duas etapas e formata como h:mm:ss - IGNORA linhas vazias"""
        try:
            if col_data in df.columns and col_hora1 in df.columns and col_hora2 in df.columns:
                # Criar datetime apenas para linhas onde AMBAS as colunas têm dados
                mask_dados_validos = (
                    df[col_hora1].notna() & 
                    (df[col_hora1] != '') & 
                    df[col_hora2].notna() & 
                    (df[col_hora2] != '')
                )
                
                if mask_dados_validos.sum() == 0:
                    return "0:00:00"
                
                # Filtrar apenas linhas com dados completos
                df_valido = df[mask_dados_validos].copy()
                
                datetime1 = pd.to_datetime(df_valido[col_data].astype(str) + ' ' + df_valido[col_hora1].astype(str), errors='coerce')
                datetime2 = pd.to_datetime(df_valido[col_data].astype(str) + ' ' + df_valido[col_hora2].astype(str), errors='coerce')
                
                diferenca = (datetime2 - datetime1).dt.total_seconds()  # em segundos
                diferenca_valida = diferenca[diferenca.notna() & (diferenca >= 0) & (diferenca < 24*3600)]
                
                if len(diferenca_valida) > 0:
                    media_segundos = diferenca_valida.mean()
                    horas = int(media_segundos // 3600)
                    minutos = int((media_segundos % 3600) // 60)
                    segundos = int(media_segundos % 60)
                    return f"{horas}:{minutos:02d}:{segundos:02d}"
                    
            return "0:00:00"
        except Exception as e:
            print(f"Erro no cálculo {col_hora1} → {col_hora2}: {e}")
            return "0:00:00"
    
    # Verificar se existe a coluna crítica para o cálculo
    if 'HORA RECEBIMENTO NF DE VENDA' not in df.columns:
        colunas_nf_venda = [col for col in df.columns if 'NF' in col.upper() and 'VENDA' in col.upper()]
        if not colunas_nf_venda:
            st.warning("⚠️ **Aviso**: A coluna 'HORA RECEBIMENTO NF DE VENDA' não foi encontrada neste período. O campo 'Espera pela Nota de Venda' será exibido como 0:00:00.")
    
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
            "Total de Processos",
            f"{total_atendimentos:,}",
            help="Quantidade total de processos de troca de nota no período selecionado. Cada processo representa uma operação completa desde a entrada até a liberação."
        )

    with col2:
        st.metric(
            "Tempo: Entrada → Senha",
            tempo_ticket_senha,
            help="ENTRADA ATÉ RETIRADA DA SENHA\n\nTempo médio que o motorista leva desde a chegada no pátio (entrada com ticket) até retirar a senha para iniciar o processo de troca de nota."
        )

    with col3:
        st.metric(
            "Tempo: Senha → Gate", 
            tempo_senha_gate,
            help="RETIRADA DA SENHA ATÉ CHEGADA NO GATE\n\nTempo médio entre retirar a senha e chegar no gate para apresentar os documentos e iniciar a troca propriamente dita."
        )

    with col4:
        st.metric(
            "Tempo: Gate → Nota",
            tempo_gate_nf,
            help="GATE ATÉ RECEBIMENTO DA NOVA NOTA\n\nTempo médio que leva para processar a troca no gate e receber a nova nota fiscal de venda. Esta é uma das etapas mais críticas do processo."
        )

    with col5:
        st.metric(
            "Tempo: Nota → Liberação",
            tempo_nf_liberacao,
            help="NOTA FISCAL ATÉ LIBERAÇÃO FINAL\n\nTempo médio entre receber a nova nota fiscal e ser liberado para sair do pátio com a carga autorizada."
        )    # Separador discreto e espaçamento
    st.markdown('<div style="margin: 30px 0; border-bottom: 1px solid #e0e0e0;"></div>', unsafe_allow_html=True)
    
    # Se não há dados suficientes, mostrar mensagem mais discreta
    if len(df) == 0:
        st.warning("Poucos dados no período selecionado para análise detalhada")
        return
    
    # Layout empilhado: Top 10 clientes em cima, Atendimentos Diários abaixo (cada um ocupa a linha inteira)
    # Top 10 Movimentação - Clientes (linha inteira)
    st.markdown(f"""
    <h3 style="margin-bottom: 0px; margin-top: 20px;">Top 10 Movimentação - Clientes - (Período P1: {periodo_texto})</h3>
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
            text='Quantidade',
            title="<b>Ranking de Clientes por Volume</b>"
        )
        
        # Calcular margem direita baseada no valor máximo
        max_quantidade_clientes = top_clientes['Quantidade'].max()
        x_range_max = max_quantidade_clientes * 1.15  # 15% de margem
        
        fig_clientes.update_traces(
            texttemplate='<b>%{text}</b>', 
            textposition='outside',
            textfont_size=14,
            textfont_color='black'
        )
        fig_clientes.update_layout(
            showlegend=False,
            height=450,
            title_font={'size': 18, 'color': '#1f4e79'},
            yaxis={
                'categoryorder': 'total ascending',
                'tickfont': {'size': 12, 'color': '#1f4e79'},
                'title_font': {'size': 16, 'color': '#1f4e79'},
                'title': '<b>Cliente</b>'
            },
            xaxis={
                'tickfont': {'size': 14, 'color': '#1f4e79'},
                'title_font': {'size': 16, 'color': '#1f4e79'},
                'title': '<b>Quantidade de Processos</b>',
                'range': [0, x_range_max]
            },
            margin=dict(l=150, r=100, t=60, b=60)
        )
        st.plotly_chart(fig_clientes, use_container_width=True)

    st.markdown('<div style="height:12px"></div>', unsafe_allow_html=True)

    # TEMPO TOTAL DE PERMANÊNCIA - Nova análise para o gerente
    st.markdown(f"""
    <h3 style="margin-bottom: 0px; margin-top: 20px;">Tempo Total de Permanência - (Período P1: {periodo_texto})</h3>
    <p style="margin-bottom: 15px; color: #666; font-size: 12px;">
    Análise do tempo total que cada processo permanece no sistema (Hora de Liberação - Hora Ticket)
    </p>
    """, unsafe_allow_html=True)

    # Calcular Tempo Total de Permanência
    if 'HORA TICKET' in df.columns and 'HORARIO DE LIBERAÇÃO' in df.columns and 'data_convertida' in df.columns:
        df_permanencia = df.copy()
        
        # Combinar data com horários para criar datetime completo
        try:
            df_permanencia['datetime_ticket'] = pd.to_datetime(
                df_permanencia['data_convertida'].astype(str) + ' ' + 
                df_permanencia['HORA TICKET'].astype(str), 
                errors='coerce'
            )
            df_permanencia['datetime_liberacao'] = pd.to_datetime(
                df_permanencia['data_convertida'].astype(str) + ' ' + 
                df_permanencia['HORARIO DE LIBERAÇÃO'].astype(str), 
                errors='coerce'
            )
            
            # Calcular diferença em horas
            df_permanencia['tempo_permanencia_segundos'] = (
                df_permanencia['datetime_liberacao'] - df_permanencia['datetime_ticket']
            ).dt.total_seconds()
            
            # Filtrar valores válidos (entre 0 e 24 horas)
            df_permanencia = df_permanencia[
                (df_permanencia['tempo_permanencia_segundos'].notna()) & 
                (df_permanencia['tempo_permanencia_segundos'] >= 0) & 
                (df_permanencia['tempo_permanencia_segundos'] <= 24*3600)
            ].copy()
            
            if len(df_permanencia) > 0:
                # Converter para horas e minutos
                df_permanencia['tempo_permanencia_horas'] = df_permanencia['tempo_permanencia_segundos'] / 3600
                df_permanencia['tempo_formatado'] = df_permanencia['tempo_permanencia_segundos'].apply(
                    lambda x: f"{int(x//3600):02d}:{int((x%3600)//60):02d}" if pd.notna(x) else "N/A"
                )
                
                # Métricas principais
                media_permanencia = df_permanencia['tempo_permanencia_horas'].mean()
                max_permanencia = df_permanencia['tempo_permanencia_horas'].max()
                total_processos_validos = len(df_permanencia)
                total_processos_periodo = len(df)
                processos_sem_dados = total_processos_periodo - total_processos_validos
                
                # Exibir métricas principais
                col1, col2, col3 = st.columns(3)
                with col1:
                    # Converter para formato HH:MM
                    media_hh_mm = f"{int(media_permanencia)}:{int((media_permanencia % 1) * 60):02d}"
                    st.metric("Média de Permanência", media_hh_mm, 
                             help="Tempo médio que um processo permanece no sistema")
                with col2:
                    # Converter para formato HH:MM
                    max_hh_mm = f"{int(max_permanencia)}:{int((max_permanencia % 1) * 60):02d}"
                    st.metric("Maior Tempo", max_hh_mm, 
                             help="Processo que demorou mais tempo")
                with col3:
                    delta_info = f"-{processos_sem_dados} sem dados" if processos_sem_dados > 0 else "Todos válidos"
                    st.metric("Processos Analisados", f"{total_processos_validos}", 
                             delta=delta_info,
                             help=f"Processos com dados válidos para análise\nTotal do período: {total_processos_periodo}\nSem dados de horário: {processos_sem_dados}")
                
                # Tabela detalhada (similar ao anexo)
                st.markdown("#### **Detalhamento dos Processos**")
                
                # Preparar dados para exibição
                df_exibicao = df_permanencia[[
                    'data_convertida', 'PLACA', 'MOTORISTA', 'HORA TICKET', 
                    'HORARIO DE LIBERAÇÃO', 'tempo_formatado'
                ]].copy()
                
                df_exibicao.columns = [
                    'Data', 'Placa', 'Motorista', 'Hora Ticket', 
                    'Horário Liberação', 'Tempo Total Permanência'
                ]
                
                # Ordenar por tempo de permanência (maior para menor)
                df_exibicao = df_exibicao.sort_values('Tempo Total Permanência', ascending=False)
                
                # Exibir tabela com paginação
                st.dataframe(
                    df_exibicao, 
                    use_container_width=True,
                    height=400,
                    column_config={
                        "Data": st.column_config.DateColumn("Data", format="DD/MM/YYYY"),
                        "Tempo Total Permanência": st.column_config.TextColumn(
                            "Tempo Total Permanência",
                            help="Formato: HH:MM"
                        )
                    }
                )
                
                # Gráfico de distribuição dos tempos
                st.markdown("#### **Distribuição dos Tempos de Permanência**")
                
                # Definir bins sequenciais de 0 até o máximo (arredondado para cima)
                import math
                max_horas = math.ceil(max_permanencia)
                bins = list(range(0, max_horas + 1))  # [0, 1, 2, 3, ..., max_horas]
                
                fig_permanencia = px.histogram(
                    df_permanencia, 
                    x='tempo_permanencia_horas',
                    title="<b>Distribuição dos Tempos de Permanência</b>",
                    labels={'tempo_permanencia_horas': 'Tempo de Permanência (horas)', 'count': 'Quantidade'},
                    color_discrete_sequence=['#1f4e79'],
                    nbins=len(bins)-1  # Número de intervalos
                )
                
                fig_permanencia.update_layout(
                    title_font={'size': 18, 'color': '#1f4e79'},
                    xaxis_title="<b>Tempo de Permanência (horas)</b>",
                    yaxis_title="<b>Quantidade de Processos</b>",
                    height=400,
                    xaxis=dict(
                        tickmode='linear',
                        tick0=0,
                        dtick=1,  # Mostrar tick a cada 1 hora
                        range=[0, max_horas]
                    )
                )
                
                st.plotly_chart(fig_permanencia, use_container_width=True)
                
            else:
                st.warning("⚠️ Não foram encontrados dados válidos para calcular o tempo de permanência.")
                
        except Exception as e:
            st.error(f"❌ Erro ao calcular tempo de permanência: {str(e)}")
    else:
        st.warning("⚠️ Colunas necessárias não encontradas: 'HORA TICKET' e 'HORARIO DE LIBERAÇÃO'")

    st.markdown('<div style="height:12px"></div>', unsafe_allow_html=True)

    # Atendimentos Diários - Comparação P1 vsP2
    if data_inicio_p2 is not None and data_fim_p2 is not None:
        periodo_p2_texto = f"{data_inicio_p2.strftime('%d/%m/%Y')} a {data_fim_p2.strftime('%d/%m/%Y')}"
        st.markdown(f"""
        <h3 style="margin-bottom: 0px; margin-top: 20px;">Atendimentos Diários - Comparação P1 vsP2</h3>
        <p style="margin-bottom: 10px; color: #666; font-size: 14px;">
        <strong>P1:</strong> {periodo_texto} | <strong>P2:</strong> {periodo_p2_texto}
        </p>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <h3 style="margin-bottom: 0px; margin-top: 20px;">Atendimentos Diários - P1</h3>
        <p style="margin-bottom: 10px; color: #666; font-size: 14px;">
        <strong>P1:</strong> {periodo_texto}
        </p>
        """, unsafe_allow_html=True)

    # Gráfico de atendimentos por data (full width)
    if 'data_convertida' in df.columns:
        # Calcular métricas para P1
        atendimentos_diarios_p1 = df.groupby(df['data_convertida'].dt.date).size().reset_index()
        atendimentos_diarios_p1.columns = ['Data', 'Quantidade']
        
        media_diaria_p1 = atendimentos_diarios_p1['Quantidade'].mean()
        dias_acima_media_p1 = (atendimentos_diarios_p1['Quantidade'] > media_diaria_p1).sum()
        dias_abaixo_media_p1 = (atendimentos_diarios_p1['Quantidade'] < media_diaria_p1).sum()
        total_dias_p1 = len(atendimentos_diarios_p1)
        max_dia_p1 = atendimentos_diarios_p1.loc[atendimentos_diarios_p1['Quantidade'].idxmax()]
        vale_dia_p1 = atendimentos_diarios_p1.loc[atendimentos_diarios_p1['Quantidade'].idxmin()]
        
        # Calcular métricas paraP2
        atendimentos_diarios_p2 = df_p2.groupby(df_p2['data_convertida'].dt.date).size().reset_index()
        atendimentos_diarios_p2.columns = ['Data', 'Quantidade']
        
        if len(atendimentos_diarios_p2) > 0:
            media_diaria_p2 = atendimentos_diarios_p2['Quantidade'].mean()
            dias_acima_media_p2 = (atendimentos_diarios_p2['Quantidade'] > media_diaria_p2).sum()
            dias_abaixo_media_p2 = (atendimentos_diarios_p2['Quantidade'] < media_diaria_p2).sum()
            total_dias_p2 = len(atendimentos_diarios_p2)
            max_dia_p2 = atendimentos_diarios_p2.loc[atendimentos_diarios_p2['Quantidade'].idxmax()]
            vale_dia_p2 = atendimentos_diarios_p2.loc[atendimentos_diarios_p2['Quantidade'].idxmin()]
            
            # Calcular diferenças (P2 - P1)
            diff_media = media_diaria_p2 - media_diaria_p1
            diff_dias_acima = ((dias_acima_media_p2/total_dias_p2)*100) - ((dias_acima_media_p1/total_dias_p1)*100)
            diff_dias_abaixo = ((dias_abaixo_media_p2/total_dias_p2)*100) - ((dias_abaixo_media_p1/total_dias_p1)*100)
            diff_pico = max_dia_p2['Quantidade'] - max_dia_p1['Quantidade']
            diff_vale = vale_dia_p2['Quantidade'] - vale_dia_p1['Quantidade']
        else:
            # Valores padrão seP2 não tem dados
            media_diaria_p2 = 0
            dias_acima_media_p2 = 0
            dias_abaixo_media_p2 = 0
            total_dias_p2 = 0
            max_dia_p2 = {'Quantidade': 0}
            vale_dia_p2 = {'Quantidade': 0}
            diff_media = diff_dias_acima = diff_dias_abaixo = diff_pico = diff_vale = 0
        
        # Informações contextuais antes do gráfico
        col1, col2, col3, col4, col5 = st.columns(5)
        with col1:
            st.metric("Média Diária", f"{media_diaria_p1:.1f}", delta=f"{diff_media:+.1f}", delta_color="inverse", help="Média de processos por dia no período P1 vsP2")
        with col2:
            st.metric("Dias Acima da Média", f"{dias_acima_media_p1}", delta=f"{diff_dias_acima:+.1f}%", delta_color="inverse", help="Dias com volume superior à média P1 vsP2")
        with col3:
            st.metric("Dias Abaixo da Média", f"{dias_abaixo_media_p1}", delta=f"{diff_dias_abaixo:+.1f}%", delta_color="inverse", help="Dias com volume inferior à média P1 vsP2")
        with col4:
            st.metric("Pico Máximo", f"{max_dia_p1['Quantidade']}", delta=f"{diff_pico:+.0f}", delta_color="inverse", help="Maior volume registrado em um dia P1 vsP2")
        with col5:
            st.metric("VALE", f"{vale_dia_p1['Quantidade']}", delta=f"{diff_vale:+.0f}", delta_color="inverse", help="Menor volume registrado em um dia P1 vsP2")

        fig_diarios = px.bar(
            atendimentos_diarios_p1,
            x='Data',
            y='Quantidade',
            title="<b>Distribuição de Atendimentos por Data (P1)</b>",
            color='Quantidade',
            color_continuous_scale=[[0, '#1f4e79'], [0.5, '#2e5f8a'], [1, '#4682b4']],
            text='Quantidade'
        )
        
        # Adicionar linha da média diária
        fig_diarios.add_hline(
            y=media_diaria_p1,
            line_dash="dash",
            line_color="red",
            line_width=3,
            annotation_text=f"<b>Média P1: {media_diaria_p1:.1f}</b>",
            annotation_position="top right",
            annotation_font_size=14,
            annotation_font_color="red"
        )
        
        # Calcular margem superior para não cortar os valores
        max_quantidade = atendimentos_diarios_p1['Quantidade'].max()
        y_range_max = max_quantidade * 1.2  # 20% de margem superior
        
        fig_diarios.update_traces(
            texttemplate='<b>%{text}</b>', 
            textposition='outside',
            textfont_size=14,
            textfont_color='black'
        )
        fig_diarios.update_layout(
            showlegend=False,
            height=500,
            title_font={'size': 20, 'color': '#1f4e79'},
            xaxis_title="<b>Data</b>",
            yaxis_title="<b>Quantidade de Atendimentos</b>",
            xaxis={
                'tickfont': {'size': 14, 'color': '#1f4e79'},
                'title_font': {'size': 16, 'color': '#1f4e79'},
                'tickformat': '%-d %b',  # Dia sem zero inicial e mês abreviado (ex: "1 Out")
                'dtick': 'D1'  # Um tick por dia
            },
            yaxis={
                'tickfont': {'size': 14, 'color': '#1f4e79'},
                'title_font': {'size': 16, 'color': '#1f4e79'},
                'range': [0, y_range_max]
            },
            margin=dict(l=80, r=40, t=100, b=80)
        )
        st.plotly_chart(fig_diarios, use_container_width=True)

        # Gráfico de Volume Diário por Cliente
        st.markdown('<div style="height:20px"></div>', unsafe_allow_html=True)
        st.markdown("#### **Volume Diário por Cliente - (Período P1)**")
        st.markdown('<p style="margin-bottom: 15px; color: #666; font-size: 12px;">Movimentação diária de cada cliente ao longo do período selecionado</p>', unsafe_allow_html=True)
        
        if 'CLIENTE' in df.columns and 'data_convertida' in df.columns:
            # Criar tabela pivô: Data x Cliente
            df_cliente_data = df.groupby([df['data_convertida'].dt.date, 'CLIENTE']).size().reset_index()
            df_cliente_data.columns = ['Data', 'Cliente', 'Quantidade']
            
            # Pegar apenas os top 10 clientes por volume total para não poluir o gráfico
            top_clientes = df['CLIENTE'].value_counts().head(10).index.tolist()
            df_cliente_data_top = df_cliente_data[df_cliente_data['Cliente'].isin(top_clientes)]
            
            if len(df_cliente_data_top) > 0:
                # Definir paleta de cores vibrantes e contrastantes
                cores_vibrantes = [
                    '#FF6B35',  # Laranja vibrante
                    '#004E89',  # Azul escuro
                    '#00A859',  # Verde vibrante
                    '#8A2BE2',  # Azul violeta
                    '#DC143C',  # Vermelho carmesim
                    '#FF1493',  # Rosa choque
                    '#32CD32',  # Verde limão
                    '#FF8C00',  # Laranja escuro
                    '#9400D3',  # Violeta escuro
                    '#1E90FF'   # Azul dodger
                ]
                
                # Criar gráfico de linhas
                fig_clientes_tempo = px.line(
                    df_cliente_data_top,
                    x='Data', 
                    y='Quantidade',
                    color='Cliente',
                    title="<b>Evolução Diária do Volume por Cliente</b>",
                    markers=True,
                    line_shape='linear',
                    color_discrete_sequence=cores_vibrantes
                )
                
                # Personalizar o gráfico
                fig_clientes_tempo.update_traces(
                    mode='lines+markers',
                    line=dict(width=3),
                    marker=dict(size=6)
                )
                
                fig_clientes_tempo.update_layout(
                    height=500,
                    title_font={'size': 18, 'color': '#1f4e79'},
                    xaxis_title="<b>Data</b>",
                    yaxis_title="<b>Quantidade de Atendimentos</b>",
                    xaxis={
                        'tickfont': {'size': 12, 'color': '#1f4e79'},
                        'title_font': {'size': 14, 'color': '#1f4e79'},
                        'tickformat': '%-d %b',  # Formato de data limpo
                        'dtick': 'D1'
                    },
                    yaxis={
                        'tickfont': {'size': 12, 'color': '#1f4e79'},
                        'title_font': {'size': 14, 'color': '#1f4e79'}
                    },
                    legend={
                        'font': {'size': 11},
                        'bgcolor': 'rgba(255,255,255,0.8)',
                        'bordercolor': '#e0e0e0',
                        'borderwidth': 1
                    },
                    margin=dict(l=80, r=40, t=80, b=80),
                    hovermode='x unified'
                )
                
                st.plotly_chart(fig_clientes_tempo, use_container_width=True)
                
                # Informações complementares
                col1, col2, col3 = st.columns(3)
                with col1:
                    total_clientes_periodo = df['CLIENTE'].nunique()
                    st.metric("Total de Clientes", total_clientes_periodo, help="Quantidade total de clientes únicos no período")
                with col2:
                    clientes_ativos_por_dia = df_cliente_data.groupby('Data')['Cliente'].nunique().mean()
                    st.metric("Clientes Ativos/Dia", f"{clientes_ativos_por_dia:.1f}", help="Média de clientes únicos por dia")
                with col3:
                    st.metric("Clientes no Gráfico", "10", help="Top 10 clientes com maior volume total")
                    
            else:
                st.warning("⚠️ Não há dados suficientes para gerar o gráfico de clientes por data.")
        else:
            st.warning("⚠️ Colunas necessárias não encontradas: 'CLIENTE' e 'data_convertida'")
    
    # Separador discreto antes da linha do tempo
    st.markdown('<div style="margin: 30px 0; border-bottom: 1px solid #e0e0e0;"></div>', unsafe_allow_html=True)
    
    # ETAPAS DO PROCESSO - Padrão de espaçamento 
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
    def calcular_tempo_medio(df, col_data1, col_hora1, col_hora2, col_data2=None):
        """Calcula tempo médio entre duas etapas no formato h:mm:ss
        
        Parâmetros:
        - col_data1: coluna de data para o primeiro horário
        - col_hora1: primeira hora
        - col_hora2: segunda hora
        - col_data2: coluna de data para o segundo horário (opcional, usa col_data1 se não fornecida)
        """
        try:
            # Se col_data2 não for fornecida, usar a mesma data para ambos os horários
            if col_data2 is None:
                col_data2 = col_data1
            
            if col_data1 in df.columns and col_data2 in df.columns and col_hora1 in df.columns and col_hora2 in df.columns:
                # Filtrar apenas linhas com valores válidos (não nulos e não vazios)
                mask_valido = (
                    df[col_data1].notna() & 
                    df[col_data2].notna() & 
                    df[col_hora1].notna() & 
                    df[col_hora2].notna() &
                    (df[col_data1] != '') &
                    (df[col_data2] != '') &
                    (df[col_hora1] != '') &
                    (df[col_hora2] != '')
                )
                
                df_valido = df[mask_valido].copy()
                
                if len(df_valido) == 0:
                    return "0:00:00"
                
                # Combinar data e hora para criar datetime
                datetime1 = pd.to_datetime(df_valido[col_data1].astype(str) + ' ' + df_valido[col_hora1].astype(str), errors='coerce')
                datetime2 = pd.to_datetime(df_valido[col_data2].astype(str) + ' ' + df_valido[col_hora2].astype(str), errors='coerce')
                
                # Calcular diferença em segundos
                diferenca = (datetime2 - datetime1).dt.total_seconds()
                
                # LÓGICA DE NEGÓCIO adaptada para diferentes casos
                mask_tempo_razoavel = diferenca.notna()
                diferenca_filtrada = diferenca[mask_tempo_razoavel].copy()
                
                # Para Gate → NF Venda (que pode span dias), usar limite maior
                if col_hora1 == 'HORA GATE ' and col_hora2 == 'HORA RECEBIMENTO NF DE VENDA':
                    # Filtrar apenas tempos positivos e razoáveis (0 a 72 horas = 3 dias máximo)
                    diferenca_valida = diferenca_filtrada[(diferenca_filtrada >= 0) & (diferenca_filtrada <= 72*3600)]
                else:
                    # Para outros intervalos, usar lógica anterior
                    # Corrigir casos de meia-noite: se negativo entre -2h e 0, adicionar 24h
                    mask_meia_noite = (diferenca_filtrada >= -2*3600) & (diferenca_filtrada < 0)
                    diferenca_filtrada.loc[mask_meia_noite] = diferenca_filtrada.loc[mask_meia_noite] + 24*3600
                    
                    # Filtrar apenas tempos lógicos: 0 a 6 horas (processo normal)
                    diferenca_valida = diferenca_filtrada[(diferenca_filtrada >= 0) & (diferenca_filtrada <= 6*3600)]
                
                if len(diferenca_valida) > 0:
                    media_segundos = diferenca_valida.mean()
                    horas = int(media_segundos // 3600)
                    minutos = int((media_segundos % 3600) // 60)
                    segundos = int(media_segundos % 60)
                    return f"{horas}:{minutos:02d}:{segundos:02d}"
                        
            return "0:00:00"
        except Exception as e:
            return "0:00:00"
    
    # Informações discretas sobre os dados
    st.sidebar.caption(f"� {len(df):,} registros carregados")
    st.sidebar.caption(f"📅 Período: {df['DATA'].min().strftime('%d/%m/%Y') if 'DATA' in df.columns else 'N/A'} a {df['DATA'].max().strftime('%d/%m/%Y') if 'DATA' in df.columns else 'N/A'}")
    
    # Calcular intervalos das 5 etapas com nomes CORRETOS das colunas (com espaços exatos!)
    intervalo1 = calcular_tempo_medio(df, 'DATA  TICKET', 'HORA TICKET', 'HORARIO SENHA ')       # Ticket → Senha
    intervalo2 = calcular_tempo_medio(df, 'DATA  TICKET', 'HORARIO SENHA ', 'HORA GATE ')        # Senha → Gate
    intervalo3 = calcular_tempo_medio(df, 'DATA  TICKET', 'HORA GATE ', 'HORA RECEBIMENTO NF DE VENDA', 'DATA DE LIBERAÇÃO')  # Gate → NF Venda
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
        font-size: 22px;
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
                <div style="font-weight: bold; font-size: 14px; color: #333; text-align: center;">
                    {etapa['nome']}
                </div>
            </div>
            """, unsafe_allow_html=True)
    
    # Renderizar setas e intervalos - espaçamento reduzido
    for i in range(len(etapas_info) - 1):
        with colunas_setas[i]:
            st.markdown(f"""
            <div style="text-align: center; margin-top: 15px;">
                <div style="color: #28a745; font-size: 24px;">→</div>
                <div style="color: #28a745; font-weight: bold; font-size: 14px; margin-top: 2px;">
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
    
    # Função para calcular gaps de um período específico
    def calcular_gaps_periodo(df_periodo, nome_periodo):
        gaps = {}
        
        # Gap 1: Cliente - Tempo para enviar NF
        if 'entrada_patio' in etapas_encontradas and 'nota_venda' in etapas_encontradas:
            try:
                col_ticket = etapas_encontradas['entrada_patio']['coluna']
                col_nf = etapas_encontradas['nota_venda']['coluna']
                
                # Converter para datetime
                base_date = pd.Timestamp('2024-01-01')
                
                dt_ticket = pd.to_datetime(base_date.strftime('%Y-%m-%d') + ' ' + df_periodo[col_ticket].astype(str), errors='coerce')
                dt_nf = pd.to_datetime(base_date.strftime('%Y-%m-%d') + ' ' + df_periodo[col_nf].astype(str), errors='coerce')
                
                # Calcular diferença
                diferenca = (dt_nf - dt_ticket).dt.total_seconds() / 3600
                diferenca = diferenca.where(diferenca >= 0, diferenca + 24)  # Ajustar para horários que cruzam meia-noite
                
                dados_validos = diferenca.dropna()
                
                if len(dados_validos) > 0:
                    gaps[f'Gap Cliente (Envio NF Venda) - {nome_periodo}'] = {
                        'tempo_medio': dados_validos.mean(),
                        'tempo_maximo': dados_validos.max(),
                        'tempo_minimo': dados_validos.min(),
                        'registros': len(dados_validos),
                        'dados': dados_validos,
                        'periodo': nome_periodo
                    }
            except Exception as e:
                st.warning(f"Erro no Gap Cliente {nome_periodo}: {str(e)}")
        
        # Gap 2: Pátio - Tempo de liberação
        if 'nota_venda' in etapas_encontradas and 'liberacao' in etapas_encontradas:
            try:
                col_nf = etapas_encontradas['nota_venda']['coluna']
                col_liberacao = etapas_encontradas['liberacao']['coluna']
                
                base_date = pd.Timestamp('2024-01-01')
                
                dt_nf = pd.to_datetime(base_date.strftime('%Y-%m-%d') + ' ' + df_periodo[col_nf].astype(str), errors='coerce')
                dt_liberacao = pd.to_datetime(base_date.strftime('%Y-%m-%d') + ' ' + df_periodo[col_liberacao].astype(str), errors='coerce')
                
                diferenca = (dt_liberacao - dt_nf).dt.total_seconds() / 3600
                diferenca = diferenca.where(diferenca >= 0, diferenca + 24)
                
                dados_validos = diferenca.dropna()
                
                if len(dados_validos) > 0:
                    gaps[f'Gap Pátio (Liberação) - {nome_periodo}'] = {
                        'tempo_medio': dados_validos.mean(),
                        'tempo_maximo': dados_validos.max(),
                        'tempo_minimo': dados_validos.min(),
                        'registros': len(dados_validos),
                        'dados': dados_validos,
                        'periodo': nome_periodo
                    }
            except Exception as e:
                st.warning(f"Erro no Gap Pátio {nome_periodo}: {str(e)}")
        
        return gaps
    
    # Calcular gaps para P1 eP2
    gaps_p1 = calcular_gaps_periodo(df, 'P1')
    gaps_p2 = calcular_gaps_periodo(df_p2, 'P2')
    
    # Combinar todos os gaps calculados
    gaps_calculados = {**gaps_p1, **gaps_p2}    # EXIBIR RESULTADOS DOS GAPS
    if gaps_calculados:
        # Separador discreto
        st.markdown('<div style="margin: 30px 0; border-bottom: 1px solid #e0e0e0;"></div>', unsafe_allow_html=True)
        
        if data_inicio_p2 is not None and data_fim_p2 is not None:
            periodo_p2_texto = f"{data_inicio_p2.strftime('%d/%m/%Y')} a {data_fim_p2.strftime('%d/%m/%Y')}"
            
            st.markdown(f"""
            <h2 style="margin-bottom: 0px; margin-top: 20px;">Análise de Gargalos - Comparação P1 vsP2</h2>
            <p style="margin-bottom: 10px; color: #666; font-size: 14px;">
            <strong>P1:</strong> {periodo_texto} | <strong>P2:</strong> {periodo_p2_texto}
            </p>
            <p style="margin-bottom: 15px; color: #666; font-size: 12px;">
            Compare a evolução da performance entre os dois períodos selecionados.
            </p>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <h2 style="margin-bottom: 0px; margin-top: 20px;">Análise de Gargalos - P1</h2>
            <p style="margin-bottom: 10px; color: #666; font-size: 14px;">
            <strong>P1:</strong> {periodo_texto}
            </p>
            <p style="margin-bottom: 15px; color: #666; font-size: 12px;">
            Análise da performance do período selecionado.
            </p>
            """, unsafe_allow_html=True)
        
        # Organizar gaps por tipo para comparação
        gaps_por_tipo = {}
        for gap_nome, dados in gaps_calculados.items():
            if "Cliente" in gap_nome:
                tipo = "Cliente"
            elif "Pátio" in gap_nome:
                tipo = "Pátio" 
            else:
                tipo = "Outros"
            
            periodo = dados.get('periodo', 'P1')
            
            if tipo not in gaps_por_tipo:
                gaps_por_tipo[tipo] = {}
            
            gaps_por_tipo[tipo][periodo] = dados
        
        # Exibir métricas comparativas
        if gaps_por_tipo:
            for tipo, periodos in gaps_por_tipo.items():
                st.markdown(f"#### **{tipo} - Envio NF Venda**" if tipo == "Cliente" else f"#### **{tipo} - Liberação**")
                
                cols = st.columns(3)  # P1,P2, Comparação
                
                # P1
                if 'P1' in periodos:
                    dados_p1 = periodos['P1']
                    tempo_p1 = dados_p1['tempo_medio']
                    registros_p1 = dados_p1['registros']
                    
                    with cols[0]:
                        status_p1 = "CRÍTICO" if tempo_p1 > 24 else "ALTO" if tempo_p1 > 12 else "OK"
                        st.metric(
                            label="P1",
                            value=f"{tempo_p1:.1f}h",
                            delta=f"{registros_p1} processos",
                            help=f"Período 1: {periodo_texto}\nStatus: {status_p1}\nTempo máximo: {dados_p1['tempo_maximo']:.1f}h"
                        )
                
                #P2
                if 'P2' in periodos:
                    dados_p2 = periodos['P2']
                    tempo_p2 = dados_p2['tempo_medio']
                    registros_p2 = dados_p2['registros']
                    
                    with cols[1]:
                        status_p2 = "CRÍTICO" if tempo_p2 > 24 else "ALTO" if tempo_p2 > 12 else "OK"
                        st.metric(
                            label="P2",
                            value=f"{tempo_p2:.1f}h",
                            delta=f"{registros_p2} processos",
                            help=f"Período 2: {periodo_p2_texto}\nStatus: {status_p2}\nTempo máximo: {dados_p2['tempo_maximo']:.1f}h"
                        )
                
                # Comparação
                if 'P1' in periodos and 'P2' in periodos:
                    diferenca = dados_p2['tempo_medio'] - dados_p1['tempo_medio']
                    percentual = (diferenca / dados_p1['tempo_medio']) * 100
                    
                    with cols[2]:
                        tendencia = "Piora" if diferenca > 0 else "Melhora" if diferenca < 0 else "Estável"
                        
                        # Definir cor do delta: vermelho para piora, verde para melhora, normal para estável
                        if diferenca > 0.1:  # Piora significativa
                            delta_color = "inverse"  # Vermelho
                        elif diferenca < -0.1:  # Melhora significativa 
                            delta_color = "normal"   # Verde
                        else:  # Estável
                            delta_color = "off"      # Cinza
                        
                        st.metric(
                            label="EvoluçãoP2 vs P1",
                            value=f"{diferenca:+.1f}h",
                            delta=f"{percentual:+.0f}% ({tendencia})",
                            delta_color=delta_color,
                            help=f"VariaçãoP2 vs P1\n\nP1: {dados_p1['tempo_medio']:.1f}h\nP2: {dados_p2['tempo_medio']:.1f}h\nDiferença: {diferenca:+.1f}h ({percentual:+.0f}%)\n\nInterpretação:\n+ =P2 mais lento que P1 (piora)\n- =P2 mais rápido que P1 (melhora)\n≈ = Sem mudança significativa"
                        )
                
                st.markdown("---")  # Separador entre tipos
        
        # Gráfico comparativo P1 vsP2
        if gaps_por_tipo:
            st.markdown(f"""
            ### **Gráfico Comparativo: P1 vsP2**
            <p style="margin-bottom: 10px; color: #666; font-size: 14px;">
            <strong>P1:</strong> {periodo_texto} | <strong>P2:</strong> {periodo_p2_texto}
            </p>
            """, unsafe_allow_html=True)
            
            # Preparar dados para o gráfico
            dados_grafico = []
            for tipo, periodos in gaps_por_tipo.items():
                etapa_nome = "Cliente (Envio NF Venda)" if tipo == "Cliente" else "Pátio (Liberação)"
                
                if 'P1' in periodos:
                    dados_grafico.append({
                        'Etapa': etapa_nome,
                        'Período': 'P1',
                        'Tempo Médio (h)': periodos['P1']['tempo_medio'],
                        'Registros': periodos['P1']['registros']
                    })
                
                if 'P2' in periodos:
                    dados_grafico.append({
                        'Etapa': etapa_nome,
                        'Período': 'P2', 
                        'Tempo Médio (h)': periodos['P2']['tempo_medio'],
                        'Registros': periodos['P2']['registros']
                    })
            
            if dados_grafico:
                df_grafico = pd.DataFrame(dados_grafico)
                
                # Métricas de resumo antes do gráfico
                col_comp1, col_comp2, col_comp3 = st.columns(3)
                
                # Calcular médias por período
                tempo_p1 = df_grafico[df_grafico['Período'] == 'P1']['Tempo Médio (h)'].mean() if 'P1' in df_grafico['Período'].values else 0
                tempo_p2 = df_grafico[df_grafico['Período'] == 'P2']['Tempo Médio (h)'].mean() if 'P2' in df_grafico['Período'].values else 0
                
                with col_comp1:
                    st.metric("P1 - Tempo Médio", f"{tempo_p1:.1f}h", help=f"Média geral do período P1: {periodo_texto}")
                with col_comp2:
                    st.metric("P2 - Tempo Médio", f"{tempo_p2:.1f}h", help=f"Média geral do períodoP2: {periodo_p2_texto}")
                with col_comp3:
                    if tempo_p1 > 0 and tempo_p2 > 0:
                        evolucao = tempo_p2 - tempo_p1
                        percentual_evo = (evolucao / tempo_p1) * 100
                        tendencia = "↑" if evolucao > 0 else "↓" if evolucao < 0 else "→"
                        
                        # Definir cor do delta: vermelho para piora, verde para melhora
                        if evolucao > 0.1:  # Piora significativa
                            delta_color_geral = "inverse"  # Vermelho
                        elif evolucao < -0.1:  # Melhora significativa
                            delta_color_geral = "normal"   # Verde  
                        else:  # Estável
                            delta_color_geral = "off"      # Cinza
                        
                        st.metric("Evolução Geral", f"{evolucao:+.1f}h", delta=f"{percentual_evo:+.0f}% {tendencia}", delta_color=delta_color_geral)
                
                # Gráfico de barras agrupadas
                fig = px.bar(
                    df_grafico,
                    x='Etapa',
                    y='Tempo Médio (h)',
                    color='Período',
                    title="<b>Comparação P1 vsP2 por Etapa</b>",
                    text='Tempo Médio (h)',
                    color_discrete_map={'P1': '#1f4e79', 'P2': '#e74c3c'},  # Azul para P1, vermelho paraP2
                    barmode='group'
                )
                
                fig.update_traces(
                    texttemplate='<b>%{text:.1f}h</b>', 
                    textposition='outside',
                    textfont_size=14,
                    textfont_color='black'
                )
                
                # Calcular margem superior baseada no valor máximo para evitar corte
                max_value = df_grafico['Tempo Médio (h)'].max()
                y_range_max = max_value * 1.25  # 25% de margem superior
                
                fig.update_layout(
                    height=500,
                    title_font={'size': 20, 'color': '#1f4e79'},
                    xaxis_title="<b>Etapa do Processo</b>",
                    yaxis_title="<b>Tempo Médio (horas)</b>",
                    xaxis={
                        'tickfont': {'size': 14, 'color': '#1f4e79'},
                        'title_font': {'size': 16, 'color': '#1f4e79'}
                    },
                    yaxis={
                        'tickfont': {'size': 14, 'color': '#1f4e79'},
                        'title_font': {'size': 16, 'color': '#1f4e79'},
                        'range': [0, y_range_max]
                    },
                    legend=dict(
                        orientation="h",
                        yanchor="bottom",
                        y=1.02,
                        xanchor="right",
                        x=1,
                        font={'size': 14}
                    ),
                    margin=dict(l=80, r=40, t=120, b=100)
                )
                
                st.plotly_chart(fig, use_container_width=True)
                
                # Tabela de comparação detalhada
                st.markdown("#### **Detalhamento da Comparação**")
                comparacao_detalhada = []
                
                for tipo, periodos in gaps_por_tipo.items():
                    etapa = "Cliente (Envio NF)" if tipo == "Cliente" else "Pátio (Liberação)"
                    
                    p1_tempo = periodos.get('P1', {}).get('tempo_medio', 0)
                    p2_tempo = periodos.get('P2', {}).get('tempo_medio', 0)
                    p1_registros = periodos.get('P1', {}).get('registros', 0)
                    p2_registros = periodos.get('P2', {}).get('registros', 0)
                    
                    if p1_tempo > 0 and p2_tempo > 0:
                        diferenca = p2_tempo - p1_tempo
                        percentual = (diferenca / p1_tempo) * 100
                        resultado = "Melhorou" if diferenca < -0.5 else "Piorou" if diferenca > 0.5 else "Estável"
                        
                        comparacao_detalhada.append({
                            'Etapa': etapa,
                            'P1 (h)': f"{p1_tempo:.1f}",
                            'P2 (h)': f"{p2_tempo:.1f}",
                            'Diferença (h)': f"{diferenca:+.1f}",
                            'Variação (%)': f"{percentual:+.0f}%",
                            'Resultado': resultado,
                            'Processos P1': p1_registros,
                            'Processos P2': p2_registros
                        })
                
                if comparacao_detalhada:
                    df_comparacao = pd.DataFrame(comparacao_detalhada)
                    st.dataframe(df_comparacao, use_container_width=True)
        
        # Resumo executivo
        st.markdown(f"### **RESUMO - (Período P1: {periodo_texto})**")
        
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
        
        # Informações discretas da tabela
        st.caption(f"Mostrando {len(df_final):,} de {len(df):,} registros | {len(colunas_existentes)} colunas")
        
        # Exibir a tabela
        st.dataframe(
            df_final, 
            use_container_width=True,
            height=400,
            hide_index=False
        )
        
        # Estatísticas rápidas da tabela
        st.markdown(f"### **Qualidade dos Dados - (Período P1: {periodo_texto})**")
        st.markdown("*Percentual de preenchimento por campo - Use para cobrar qualidade no dia a dia*")
        
        # Filtrar colunas removendo DATA e adicionando coluna de Total no início
        colunas_filtradas = [col for col in colunas_existentes if 'DATA' not in col.upper()]
        
        # Criar lista final com Total de Processos no início
        cols_stats = st.columns(len(colunas_filtradas) + 1)
        
        # Primeira coluna: Total de Processos
        with cols_stats[0]:
            total_registros = len(df)
            st.metric(
                label="TOTAL PROCESSOS",
                value=f"{total_registros:,}",
                delta="100% base",
                help=f"📊 TOTAL DE PROCESSOS NO PERÍODO\n\n📋 Total de linhas/processos: {total_registros:,}\n📅 Período: {periodo_texto}\n\n💡 Esta é a base para calcular todos os percentuais de preenchimento dos outros campos."
            )
        
        # Demais colunas: Qualidade de preenchimento
        for idx, col in enumerate(colunas_filtradas):
            with cols_stats[idx + 1]:
                valores_preenchidos = df[col].notna().sum()
                percentual_preenchimento = (valores_preenchidos / total_registros) * 100
                celulas_vazias = total_registros - valores_preenchidos
                
                # Determinar status da qualidade
                if percentual_preenchimento >= 95:
                    status_cor = "ÓTIMO"
                elif percentual_preenchimento >= 80:
                    status_cor = "MÉDIO"
                else:
                    status_cor = "RUIM"
                
                st.metric(
                    label=col.replace('HORA', 'H.'),
                    value=f"{percentual_preenchimento:.1f}%",
                    delta=f"{valores_preenchidos:,} de {total_registros:,}",
                    help=f"QUALIDADE DE PREENCHIMENTO\n\nCampos preenchidos: {valores_preenchidos:,}\nCampos vazios: {celulas_vazias:,}\nQualidade: {status_cor}\n\nUse para cobrar o preenchimento correto das planilhas no dia a dia!\n\nMeta recomendada: >95% preenchimento"
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
