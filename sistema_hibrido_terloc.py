"""
🔄 SISTEMA HÍBRIDO TERLOC - Dados Locais + Upload
=================================================
Sistema que combina dados pré-carregados com upload opcional do usuário
"""

import streamlit as st
import pandas as pd
import os
from pathlib import Path
from datetime import datetime
import time
import hashlib
from io import BytesIO

class SistemaHibridoTerloc:
    def __init__(self):
        self.arquivo_padrao = Path('PLANILHA TROCA DE NOTA TERLOC.xlsx')
        self.arquivo_usuario = Path('dados_usuario_upload.xlsx')
        self.cache_dir = Path("cache_terloc_hibrido")
        self.cache_dir.mkdir(exist_ok=True)
        
        # Cache para dados padrão e usuário
        self.cache_padrao = self.cache_dir / "dados_padrao.parquet"
        self.cache_usuario = self.cache_dir / "dados_usuario.parquet"
        self.metadata_padrao = self.cache_dir / "metadata_padrao.txt"
        self.metadata_usuario = self.cache_dir / "metadata_usuario.txt"
    
    def calcular_hash_arquivo(self, arquivo_path):
        """Calcula hash do arquivo para detectar mudanças"""
        if not arquivo_path.exists():
            return None
        try:
            with open(arquivo_path, 'rb') as f:
                return hashlib.md5(f.read()).hexdigest()
        except Exception:
            return None
    
    def salvar_upload_usuario(self, uploaded_file):
        """Salva arquivo enviado pelo usuário"""
        try:
            with open(self.arquivo_usuario, 'wb') as f:
                f.write(uploaded_file.getbuffer())
            
            # Limpar cache do usuário para forçar recarregamento
            if self.cache_usuario.exists():
                self.cache_usuario.unlink()
            if self.metadata_usuario.exists():
                self.metadata_usuario.unlink()
            
            return True
        except Exception as e:
            st.error(f"Erro ao salvar arquivo: {e}")
            return False
    
    def carregar_dados_padrao(self, limite_registros=50000):
        """Carrega dados do arquivo padrão (pré-carregado)"""
        
        if not self.arquivo_padrao.exists():
            return None, "Arquivo padrão não encontrado"
        
        # Verificar cache
        hash_atual = self.calcular_hash_arquivo(self.arquivo_padrao)
        cache_valido = False
        
        if self.cache_padrao.exists() and self.metadata_padrao.exists():
            try:
                # Verificar se hash mudou
                with open(self.metadata_padrao, 'r') as f:
                    metadata = f.read()
                    if f"Hash: {hash_atual}" in metadata:
                        cache_valido = True
            except:
                pass
        
        if cache_valido:
            try:
                df = pd.read_parquet(self.cache_padrao)
                with open(self.metadata_padrao, 'r') as f:
                    metadata = f.read()
                data_cache = metadata.split('DataHora: ')[1].split('\n')[0] if 'DataHora:' in metadata else 'N/A'
                return df, f"Dados padrão (cache) - Última atualização: {data_cache}"
            except:
                pass
        
        # Carregar do arquivo
        try:
            inicio = time.time()
            
            # Tentar diferentes abas
            try:
                df = pd.read_excel(self.arquivo_padrao, sheet_name='PLANILHA ÚNICA', engine='openpyxl')
                fonte = 'PLANILHA ÚNICA'
            except:
                df = pd.read_excel(self.arquivo_padrao, sheet_name=0, engine='openpyxl')
                fonte = 'Primeira aba'
            
            # Aplicar limite
            if len(df) > limite_registros:
                df = df.head(limite_registros)
                fonte += f" (limitado a {limite_registros:,})"
            
            # Normalizar e salvar cache
            df = self.normalizar_dados(df)
            self.salvar_cache(df, fonte, self.cache_padrao, self.metadata_padrao, hash_atual)
            
            tempo = time.time() - inicio
            return df, f"Dados padrão carregados em {tempo:.1f}s"
            
        except Exception as e:
            return None, f"Erro ao carregar dados padrão: {str(e)[:50]}"
    
    def carregar_dados_usuario(self, limite_registros=50000):
        """Carrega dados do arquivo enviado pelo usuário"""
        
        if not self.arquivo_usuario.exists():
            return None, "Nenhum arquivo de usuário encontrado"
        
        try:
            inicio = time.time()
            
            # Verificar cache
            hash_atual = self.calcular_hash_arquivo(self.arquivo_usuario)
            cache_valido = False
            
            if self.cache_usuario.exists() and self.metadata_usuario.exists():
                try:
                    with open(self.metadata_usuario, 'r') as f:
                        metadata = f.read()
                        if f"Hash: {hash_atual}" in metadata:
                            cache_valido = True
                except:
                    pass
            
            if cache_valido:
                try:
                    df = pd.read_parquet(self.cache_usuario)
                    with open(self.metadata_usuario, 'r') as f:
                        metadata = f.read()
                    data_upload = metadata.split('DataHora: ')[1].split('\n')[0] if 'DataHora:' in metadata else 'N/A'
                    return df, f"Dados do usuário (cache) - Upload: {data_upload}"
                except:
                    pass
            
            # Carregar do arquivo
            try:
                df = pd.read_excel(self.arquivo_usuario, sheet_name='PLANILHA ÚNICA', engine='openpyxl')
                fonte = 'Upload do usuário - PLANILHA ÚNICA'
            except:
                df = pd.read_excel(self.arquivo_usuario, sheet_name=0, engine='openpyxl')
                fonte = 'Upload do usuário - Primeira aba'
            
            # Aplicar limite
            if len(df) > limite_registros:
                df = df.head(limite_registros)
                fonte += f" (limitado a {limite_registros:,})"
            
            # Normalizar e salvar cache
            df = self.normalizar_dados(df)
            self.salvar_cache(df, fonte, self.cache_usuario, self.metadata_usuario, hash_atual)
            
            tempo = time.time() - inicio
            return df, f"Dados do usuário carregados em {tempo:.1f}s"
            
        except Exception as e:
            return None, f"Erro ao carregar dados do usuário: {str(e)[:50]}"
    
    def carregar_mapeamento_normalizacao(self):
        """Carrega mapeamentos de normalização do arquivo txt"""
        try:
            arquivo_mapeamento = Path('Mapeamento de Normalização de Nomes.txt')
            if not arquivo_mapeamento.exists():
                return {}, {}
            
            with open(arquivo_mapeamento, 'r', encoding='utf-8') as f:
                conteudo = f.read()
            
            mapeamento_clientes = {}
            mapeamento_clientes_venda = {}
            
            # Processar seções
            secoes = conteudo.split('2. Cliente de Venda')
            secao_clientes = secoes[0].replace('1. Clientes', '').strip()
            secao_clientes_venda = secoes[1].strip() if len(secoes) > 1 else ''
            
            # Processar clientes
            for bloco in secao_clientes.split('Nome Padrão:')[1:]:
                linhas = [l.strip() for l in bloco.strip().split('\n') if l.strip()]
                if linhas:
                    # Primeira linha contém: "NOME PADRAO Variações:"
                    primeira_linha = linhas[0].strip()
                    if ' Variações:' in primeira_linha:
                        nome_padrao = primeira_linha.replace(' Variações:', '').strip()
                    else:
                        nome_padrao = primeira_linha
                    
                    # Processar variações (a partir da linha 1)
                    for linha in linhas[1:]:
                        if linha and linha != 'Variações:':
                            variacao = linha.upper()
                            mapeamento_clientes[variacao] = nome_padrao
            
            # Processar clientes de venda
            for bloco in secao_clientes_venda.split('Nome Padrão:')[1:]:
                linhas = [l.strip() for l in bloco.strip().split('\n') if l.strip()]
                if linhas:
                    # Primeira linha contém: "NOME PADRAO Variações:"
                    primeira_linha = linhas[0].strip()
                    if ' Variações:' in primeira_linha:
                        nome_padrao = primeira_linha.replace(' Variações:', '').strip()
                    else:
                        nome_padrao = primeira_linha
                    
                    # Processar variações (a partir da linha 1)
                    for linha in linhas[1:]:
                        if linha and linha != 'Variações:':
                            variacao = linha.upper()
                            mapeamento_clientes_venda[variacao] = nome_padrao
            
            return mapeamento_clientes, mapeamento_clientes_venda
        except Exception as e:
            try:
                import streamlit as st
                st.warning(f"Erro ao carregar mapeamento: {e}")
            except:
                print(f"Erro ao carregar mapeamento: {e}")
            return {}, {}

    def normalizar_nome_cliente(self, nome):
        """Normaliza nomes de clientes usando arquivo de mapeamento"""
        if pd.isna(nome) or nome == '':
            return 'NÃO INFORMADO'
        
        # Converter para string e limpar
        nome_limpo = str(nome).strip().upper()
        
        # Remover acentos e caracteres especiais
        nome_limpo = (nome_limpo.replace('Ã', 'A').replace('Õ', 'O').replace('Ç', 'C')
                                .replace('É', 'E').replace('Ê', 'E').replace('Í', 'I')
                                .replace('Ó', 'O').replace('Ô', 'O').replace('Ú', 'U')
                                .replace('Ù', 'U').replace('Û', 'U').replace('Ü', 'U'))
        
        # Carregar mapeamento
        mapeamento_clientes, _ = self.carregar_mapeamento_normalizacao()
        
        # Verificar mapeamento direto
        if nome_limpo in mapeamento_clientes:
            return mapeamento_clientes[nome_limpo]
        
        # Fallback para lógica antiga se não encontrar no mapeamento
        # ADUFERTIL - Capturar todas as variações
        if any(variacao in nome_limpo for variacao in ['ADUFERTIL', 'ADULFERTIL', 'ADUFETIL', 'ADUFERIL']):
            return 'ADUFERTIL JUNDIAI'
        
        # ELEKEIROZ - Capturar TODAS as variações com erros de digitação
        if any(variacao in nome_limpo for variacao in ['ELEKEIROZ', 'ELEIKEIROZ', 'ELEQUEIROZ', 'ELEQUEIOZ', 'ELKEIROZ']):
            return 'ELEKEIROZ'
        
        # MOSAIC CUBATÃO
        if 'MOSAIC' in nome_limpo and ('CUBATAO' in nome_limpo or 'CUBATÃO' in nome_limpo):
            return 'MOSAIC CUBATÃO'
        
        # MOSAIC UBERABA
        if 'MOSAIC' in nome_limpo and ('UBERABA' in nome_limpo or 'UBERADA' in nome_limpo):
            return 'MOSAIC UBERABA'
        
        # MOSAIC genérico - mapear para CUBATÃO
        if nome_limpo == 'MOSAIC':
            return 'MOSAIC CUBATÃO'
        
        # CSRD
        if 'CSRD' in nome_limpo:
            return 'CSRD'
        
        # JBS
        if 'JBS' in nome_limpo:
            return 'JBS'
        
        # K+S
        if 'K+S' in nome_limpo:
            return 'K+S'
        
        # NITEX
        if 'NITEX' in nome_limpo:
            return 'NITEX'
        
        # QUIMIVITA
        if 'QUIMIVITA' in nome_limpo:
            return 'QUIMIVITA'
        
        # Se não encontrou padrão conhecido, retorna normalizado
        return nome_limpo.replace('-', '/').replace('  ', ' ').strip()

    def normalizar_cliente_venda(self, nome):
        """Normaliza nomes de clientes de venda usando arquivo de mapeamento"""
        if pd.isna(nome) or nome == '':
            return 'NÃO INFORMADO'
        
        # Converter para string e limpar
        nome_limpo = str(nome).strip().upper()
        
        # Remover acentos e caracteres especiais
        nome_limpo = (nome_limpo.replace('Ã', 'A').replace('Õ', 'O').replace('Ç', 'C')
                                .replace('É', 'E').replace('Ê', 'E').replace('Í', 'I')
                                .replace('Ó', 'O').replace('Ô', 'O').replace('Ú', 'U')
                                .replace('Ù', 'U').replace('Û', 'U').replace('Ü', 'U'))
        
        # Carregar mapeamento
        _, mapeamento_clientes_venda = self.carregar_mapeamento_normalizacao()
        
        # Verificar mapeamento direto
        if nome_limpo in mapeamento_clientes_venda:
            return mapeamento_clientes_venda[nome_limpo]
        
        # Fallback para lógica de detecção de padrões
        
        # ADUBOS ARAGUAIA - qualquer variação (Anápolis ou Catalão)
        if 'ADUBOS' in nome_limpo and ('ARAG' in nome_limpo or 'ANAPOLIS' in nome_limpo):
            return 'ADUBOS ARAGUAIA ANAPOLIS'
        if 'ADUBOS' in nome_limpo and ('CATALAO' in nome_limpo or 'CATALÃO' in nome_limpo):
            return 'ADUBOS ARAGUAIA CATALÃO'
        
        # ADUFERTIL ALFENAS - qualquer variação
        if any(palavra in nome_limpo for palavra in ['ADUFERTIL', 'ADULFERTIL']) and 'ALFENAS' in nome_limpo:
            return 'ADUFERTIL ALFENAS'
        
        # COFCO variações
        if 'COFCO' in nome_limpo:
            if 'CATANDUVA' in nome_limpo:
                return 'COFCO CATANDUVA'
            elif 'MERIDIANO' in nome_limpo:
                return 'COFCO MERIDIANO'
            elif 'POTIRENDABA' in nome_limpo or 'POTIRENDA' in nome_limpo:
                return 'COFCO POTIRENDABA'
            elif 'SEBASTIANOPOLIS' in nome_limpo or 'SEBASTIANÓPOLIS' in nome_limpo:
                return 'COFCO SEBASTIANÓPOLIS'
        
        # FASS variações
        if 'FASS' in nome_limpo:
            if any(termo in nome_limpo for termo in ['NOVA IND', 'INDEPENDENC', 'N.INDEPEND']):
                return 'FASS NOVA INDEPENDÊNCIA'
            elif 'SERTAOZINHO' in nome_limpo or 'SERTÃOZINHO' in nome_limpo:
                return 'FASS SERTÃOZINHO'
        
        # ICL variações
        if 'ICL' in nome_limpo:
            if 'JACAREI' in nome_limpo or 'JACAREÍ' in nome_limpo:
                return 'ICL JACAREÍ'
            elif 'UBERLANDIA' in nome_limpo or 'UBERLÂNDIA' in nome_limpo:
                return 'ICL UBERLÂNDIA'
        
        # SAFRA variações
        if 'SAFRA' in nome_limpo and 'ALFENAS' in nome_limpo:
            return 'SAFRA ALFENAS'
        
        # SAFRA genérico - mapear para ALFENAS
        if nome_limpo == 'SAFRA':
            return 'SAFRA ALFENAS'
        
        # USINA variações
        if 'USINA' in nome_limpo:
            if 'SANTA ADEL' in nome_limpo:
                return 'USINA SANTA ADÉLIA'
            elif 'SAO MANOEL' in nome_limpo or 'SÃO MANOEL' in nome_limpo or 'SAO MANUEL' in nome_limpo or 'SÃO MANUEL' in nome_limpo:
                return 'USINA SÃO MANOEL'
        
        # Se não encontrou padrão, retorna normalizado
        return nome_limpo.replace('-', '/').replace('  ', ' ').strip()

    def normalizar_dados(self, df):
        """Normaliza dados para compatibilidade E aplica normalização de nomes"""
        try:
            # LIMPEZA DE COLUNAS DESNECESSÁRIAS (CRÍTICO PARA PERFORMANCE!)
            # Remover colunas "Unnamed" que estão vazias ou quase vazias
            colunas_para_manter = []
            for col in df.columns:
                if not col.startswith('Unnamed:'):
                    colunas_para_manter.append(col)
                else:
                    # Verificar se a coluna Unnamed tem dados úteis
                    if not df[col].isna().all() and df[col].fillna('').astype(str).str.strip().ne('').sum() > 10:
                        colunas_para_manter.append(col)
            
            # Manter apenas colunas úteis
            df = df[colunas_para_manter].copy()
            
            try:
                import streamlit as st
                st.info(f"📊 Colunas mantidas: {len(colunas_para_manter)} de {len(df.columns) + len([c for c in df.columns if c.startswith('Unnamed:')])}")
            except:
                print(f"📊 Colunas mantidas: {len(colunas_para_manter)}")
            
            # Normalização básica de tipos
            for col in df.columns:
                if df[col].dtype == 'object':
                    df[col] = df[col].fillna('').astype(str)
                elif df[col].dtype in ['int64', 'float64']:
                    df[col] = df[col].replace([float('inf'), float('-inf')], 0)
                    df[col] = df[col].fillna(0)
            
            # NORMALIZAÇÃO DE NOMES DE CLIENTES (CRÍTICO!)
            if 'CLIENTE' in df.columns:
                try:
                    import streamlit as st
                    st.info("🔄 Normalizando nomes de clientes...")
                except:
                    print("🔄 Normalizando nomes de clientes...")
                df['CLIENTE'] = df['CLIENTE'].apply(self.normalizar_nome_cliente)
            
            if 'CLIENTE DE VENDA' in df.columns:
                try:
                    import streamlit as st
                    st.info("🔄 Normalizando clientes de venda...")
                except:
                    print("🔄 Normalizando clientes de venda...")
                df['CLIENTE DE VENDA'] = df['CLIENTE DE VENDA'].apply(self.normalizar_cliente_venda)
            
            # Processar datas se existirem
            if 'DATA' in df.columns:
                df['data_convertida'] = pd.to_datetime(df['DATA'], errors='coerce')
            
            return df
        except Exception as e:
            try:
                import streamlit as st
                st.warning(f"Erro na normalização: {str(e)[:100]}")
            except:
                print(f"Erro na normalização: {str(e)[:100]}")
            return df
    
    def salvar_cache(self, df, fonte, cache_file, metadata_file, hash_arquivo):
        """Salva cache com informações"""
        try:
            df.to_parquet(cache_file, compression='snappy')
            
            metadata = f"""Fonte: {fonte}
DataHora: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}
Registros: {len(df):,}
Colunas: {len(df.columns)}
Hash: {hash_arquivo}"""
            
            with open(metadata_file, 'w', encoding='utf-8') as f:
                f.write(metadata)
            
            return True
        except Exception as e:
            st.warning(f"Cache não salvo: {str(e)[:40]}")
            return False
    
    def carregar_dados_inteligente(self, limite_registros=50000):
        """Carrega dados priorizando usuário, fallback para padrão"""
        
        # Tentar carregar dados do usuário primeiro
        df_usuario, msg_usuario = self.carregar_dados_usuario(limite_registros)
        
        if df_usuario is not None and not df_usuario.empty:
            st.success(f"✅ {msg_usuario}")
            st.info("📊 Usando dados enviados pelo usuário")
            return df_usuario
        
        # Fallback para dados padrão
        df_padrao, msg_padrao = self.carregar_dados_padrao(limite_registros)
        
        if df_padrao is not None and not df_padrao.empty:
            st.success(f"✅ {msg_padrao}")
            st.info("📁 Usando dados padrão do sistema")
            return df_padrao
        
        # Nenhum dado disponível
        st.error("❌ Nenhum dado disponível")
        st.warning("💡 Faça upload de uma planilha para começar")
        return pd.DataFrame()
    
    def limpar_dados_usuario(self):
        """Remove dados do usuário"""
        try:
            if self.arquivo_usuario.exists():
                self.arquivo_usuario.unlink()
            if self.cache_usuario.exists():
                self.cache_usuario.unlink()
            if self.metadata_usuario.exists():
                self.metadata_usuario.unlink()
            return True
        except:
            return False

# Instância global
sistema_hibrido = SistemaHibridoTerloc()

def interface_upload_streamlit():
    """Interface de upload no Streamlit"""
    
    st.sidebar.markdown("---")
    st.sidebar.header("📤 Atualizar Dados")
    
    # Status atual
    if sistema_hibrido.arquivo_usuario.exists():
        st.sidebar.success("✅ Dados do usuário disponíveis")
        if st.sidebar.button("🗑️ Remover dados do usuário"):
            if sistema_hibrido.limpar_dados_usuario():
                st.sidebar.success("Dados removidos!")
                st.rerun()
            else:
                st.sidebar.error("Erro ao remover")
    else:
        st.sidebar.info("📁 Usando dados padrão")
    
    # Upload de arquivo
    uploaded_file = st.sidebar.file_uploader(
        "Carregar nova planilha",
        type=['xlsx', 'xls'],
        help="Envie uma planilha Excel para atualizar os dados",
        key="upload_planilha"
    )
    
    if uploaded_file is not None:
        with st.sidebar:
            st.info("📋 Arquivo recebido...")
            
            # Mostrar informações do arquivo
            st.write(f"**Nome:** {uploaded_file.name}")
            st.write(f"**Tamanho:** {uploaded_file.size:,} bytes")
            
            if st.button("✅ Confirmar Upload", type="primary"):
                with st.spinner("Salvando arquivo..."):
                    if sistema_hibrido.salvar_upload_usuario(uploaded_file):
                        st.success("✅ Arquivo salvo com sucesso!")
                        st.balloons()
                        time.sleep(2)
                        st.rerun()
                    else:
                        st.error("❌ Erro ao salvar arquivo")

def carregar_dados_streamlit(limite_registros=50000):
    """Função principal para uso no Streamlit"""
    return sistema_hibrido.carregar_dados_inteligente(limite_registros)

if __name__ == "__main__":
    print("🔄 TESTE DO SISTEMA HÍBRIDO")
    print("=" * 40)
    
    # Teste do sistema
    df = sistema_hibrido.carregar_dados_inteligente()
    
    if not df.empty:
        print(f"\n📊 RESULTADO:")
        print(f"   Registros: {len(df):,}")
        print(f"   Colunas: {len(df.columns)}")
        print(f"   Primeiras colunas: {list(df.columns)[:3]}")
    else:
        print("❌ Nenhum dado carregado")
    
    input("\nPressione Enter para sair...")