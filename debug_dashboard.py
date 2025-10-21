import streamlit as st
import pandas as pd
import time

st.title("🔍 Debug Dashboard - TERLOC")

# Teste 1: Verificar se o arquivo existe
st.markdown("## 1️⃣ Testando carregamento do arquivo...")

try:
    arquivo_excel = 'PLANILHA TROCA DE NOTA TERLOC.xlsx'
    
    # Teste básico de existência
    import os
    if os.path.exists(arquivo_excel):
        st.success(f"✅ Arquivo encontrado: {arquivo_excel}")
        
        # Verificar tamanho do arquivo
        tamanho_mb = os.path.getsize(arquivo_excel) / (1024 * 1024)
        st.info(f"📁 Tamanho do arquivo: {tamanho_mb:.1f} MB")
        
    else:
        st.error(f"❌ Arquivo não encontrado: {arquivo_excel}")
        
except Exception as e:
    st.error(f"❌ Erro ao verificar arquivo: {e}")

# Teste 2: Listar abas
st.markdown("## 2️⃣ Listando abas da planilha...")

try:
    start_time = time.time()
    excel_file = pd.ExcelFile(arquivo_excel)
    load_time = time.time() - start_time
    
    st.success(f"✅ Abas carregadas em {load_time:.2f} segundos")
    st.write("📋 Abas disponíveis:", excel_file.sheet_names)
    
except Exception as e:
    st.error(f"❌ Erro ao listar abas: {e}")

# Teste 3: Verificar dados da aba PLANILHA ÚNICA
st.markdown("## 3️⃣ Testando carregamento da aba 'PLANILHA ÚNICA'...")

try:
    start_time = time.time()
    
    # Carregar apenas 100 linhas para teste
    df_sample = pd.read_excel(arquivo_excel, sheet_name='PLANILHA ÚNICA', nrows=100)
    load_time = time.time() - start_time
    
    st.success(f"✅ Amostra carregada em {load_time:.2f} segundos")
    st.write(f"📊 Linhas na amostra: {len(df_sample)}")
    st.write(f"📋 Colunas: {len(df_sample.columns)}")
    
    # Mostrar colunas
    with st.expander("Ver colunas"):
        st.write(list(df_sample.columns))
    
    # Mostrar primeiras linhas
    with st.expander("Ver dados"):
        st.dataframe(df_sample.head())
        
    # Verificar coluna DATA
    if 'DATA' in df_sample.columns:
        datas_validas = df_sample['DATA'].dropna()
        if len(datas_validas) > 0:
            st.info(f"📅 Dados encontrados na coluna DATA: {len(datas_validas)} registros")
            
            # Converter para datetime e verificar período
            datas_convertidas = pd.to_datetime(datas_validas, errors='coerce')
            datas_validas_dt = datas_convertidas.dropna()
            
            if len(datas_validas_dt) > 0:
                data_min = datas_validas_dt.min()
                data_max = datas_validas_dt.max()
                st.success(f"📊 Período dos dados: {data_min.date()} até {data_max.date()}")
            else:
                st.warning("⚠️ Datas não puderam ser convertidas para datetime")
        else:
            st.warning("⚠️ Nenhuma data válida encontrada na coluna DATA")
    else:
        st.error("❌ Coluna 'DATA' não encontrada")
        
except Exception as e:
    st.error(f"❌ Erro ao carregar dados: {e}")
    import traceback
    st.code(traceback.format_exc())

# Teste 4: Carregar dados completos (se solicitado)
if st.button("🚀 Testar carregamento completo da aba"):
    st.markdown("## 4️⃣ Carregando dados completos...")
    
    try:
        start_time = time.time()
        with st.spinner("Carregando todos os dados..."):
            df_completo = pd.read_excel(arquivo_excel, sheet_name='PLANILHA ÚNICA')
        
        load_time = time.time() - start_time
        
        st.success(f"✅ Dados completos carregados em {load_time:.2f} segundos")
        st.write(f"📊 Total de registros: {len(df_completo):,}")
        st.write(f"📋 Total de colunas: {len(df_completo.columns)}")
        
        # Verificar período dos dados
        if 'DATA' in df_completo.columns:
            datas_validas = pd.to_datetime(df_completo['DATA'], errors='coerce').dropna()
            if len(datas_validas) > 0:
                data_min = datas_validas.min()
                data_max = datas_validas.max()
                st.info(f"📅 Período completo: {data_min.date()} até {data_max.date()}")
                
                # Contar registros por mês
                df_completo['MES'] = datas_validas.dt.month
                contagem_mes = df_completo['MES'].value_counts().sort_index()
                st.write("📈 Registros por mês:")
                st.bar_chart(contagem_mes)
        
    except Exception as e:
        st.error(f"❌ Erro no carregamento completo: {e}")
        import traceback
        st.code(traceback.format_exc())

st.markdown("---")
st.markdown("🔍 **Debug concluído!** Use este diagnóstico para identificar onde está o problema.")