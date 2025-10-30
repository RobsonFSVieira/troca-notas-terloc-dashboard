"""
🚀 TEMPLATE DO SISTEMA HÍBRIDO DE CARREGAMENTO
==============================================
Sistema otimizado desenvolvido no projeto Troca de Notas Terloc

INSTRUÇÕES DE USO:
1. Copie este arquivo para seu projeto
2. Renomeie para: sistema_hibrido_[SEU_PROJETO].py
3. Altere as configurações marcadas com "# ALTERAR"
4. Implemente suas regras de normalização
5. Execute: python sistema_hibrido_[SEU_PROJETO].py

BENEFÍCIOS:
- Carregamento ultra-rápido (cache inteligente)
- Otimização automática de colunas
- Normalização de dados
- Detecção de mudanças no arquivo
"""

import pandas as pd
import numpy as np
from pathlib import Path
import os
from datetime import datetime
import streamlit as st

class SistemaHibridoCarregamento:
    def __init__(self, nome_projeto="seu_projeto"):  # ALTERAR: Nome do seu projeto
        self.nome_projeto = nome_projeto
        self.pasta_cache = f"cache_{nome_projeto}_hibrido"
        self.arquivo_excel = None
        self.criar_pasta_cache()
    
    def criar_pasta_cache(self):
        """Cria pasta de cache se não existir"""
        if not os.path.exists(self.pasta_cache):
            os.makedirs(self.pasta_cache)
    
    def detectar_mudancas_arquivo(self):
        """Detecta se o arquivo Excel foi modificado"""
        if not self.arquivo_excel or not os.path.exists(self.arquivo_excel):
            return True
        
        arquivo_cache_info = os.path.join(self.pasta_cache, "arquivo_info.txt")
        
        # Informações atuais do arquivo
        stat_atual = os.path.stat(self.arquivo_excel)
        info_atual = f"{stat_atual.st_mtime}_{stat_atual.st_size}"
        
        # Verificar se há informações salvas
        if os.path.exists(arquivo_cache_info):
            with open(arquivo_cache_info, 'r') as f:
                info_anterior = f.read().strip()
            
            if info_atual == info_anterior:
                return False  # Arquivo não mudou
        
        # Salvar nova informação
        with open(arquivo_cache_info, 'w') as f:
            f.write(info_atual)
        
        return True  # Arquivo mudou ou primeira execução
    
    def limpar_e_otimizar_colunas(self, df):
        """Remove colunas vazias e otimiza estrutura"""
        print("🔧 Otimizando colunas...")
        colunas_antes = len(df.columns)
        
        # Remover colunas completamente vazias
        df = df.dropna(axis=1, how='all')
        
        # Remover colunas "Unnamed" que estão quase vazias
        colunas_para_remover = []
        for col in df.columns:
            if 'Unnamed:' in str(col):
                # Contar valores não vazios
                valores_nao_vazios = df[col].count()
                if valores_nao_vazios < 10:  # Menos de 10 valores úteis
                    colunas_para_remover.append(col)
        
        df = df.drop(columns=colunas_para_remover)
        
        colunas_depois = len(df.columns)
        print(f"✅ Colunas otimizadas: {colunas_antes} → {colunas_depois}")
        
        return df
    
    def normalizar_nome_cliente(self, nome):
        """
        ALTERAR: Implementar suas regras de normalização de nomes
        Exemplo baseado no projeto Troca de Notas Terloc
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
        
        # ALTERAR: Implementar suas regras específicas aqui
        # Exemplos:
        
        # Regra 1: Normalizar empresa fictícia
        # if 'EMPRESA1' in nome_limpo or 'EMP1' in nome_limpo:
        #     return 'EMPRESA1 PADRÃO'
        
        # Regra 2: Normalizar outra empresa
        # if 'EMPRESA2' in nome_limpo:
        #     if 'FILIAL1' in nome_limpo:
        #         return 'EMPRESA2 FILIAL1'
        #     elif 'FILIAL2' in nome_limpo:
        #         return 'EMPRESA2 FILIAL2'
        #     else:
        #         return 'EMPRESA2 MATRIZ'
        
        # Se não encontrou padrão, retorna normalizado
        return nome_limpo.replace('-', '/').replace('  ', ' ').strip()
    
    def normalizar_dados(self, df):
        """
        ALTERAR: Implementar suas regras de normalização de dados
        """
        print("🔧 Normalizando dados...")
        
        # 1. ALTERAR: Normalizar coluna de clientes (se existir)
        if 'CLIENTE' in df.columns:
            df['CLIENTE'] = df['CLIENTE'].apply(self.normalizar_nome_cliente)
        
        # 2. ALTERAR: Normalizar outras colunas de nomes (exemplos)
        # if 'FORNECEDOR' in df.columns:
        #     df['FORNECEDOR'] = df['FORNECEDOR'].apply(self.normalizar_nome_cliente)
        
        # if 'VENDEDOR' in df.columns:
        #     df['VENDEDOR'] = df['VENDEDOR'].apply(self.normalizar_nome_cliente)
        
        # 3. Padronizar datas (busca automática por colunas com "DATA")
        colunas_data = [col for col in df.columns if 'DATA' in col.upper()]
        for col in colunas_data:
            df[col] = pd.to_datetime(df[col], errors='coerce')
        
        # 4. Limpar valores numéricos
        colunas_numericas = df.select_dtypes(include=[np.number]).columns
        for col in colunas_numericas:
            df[col] = df[col].fillna(0)
        
        # 5. ALTERAR: Suas regras específicas aqui
        # Exemplo: padronizar status
        # if 'STATUS' in df.columns:
        #     df['STATUS'] = df['STATUS'].str.upper().fillna('NÃO INFORMADO')
        
        print("✅ Dados normalizados")
        return df
    
    def carregar_dados_excel(self, limite_registros=50000):
        """Carrega dados do Excel com otimizações"""
        print(f"📊 Carregando dados de {self.arquivo_excel}...")
        
        try:
            # Ler apenas as linhas necessárias
            df = pd.read_excel(
                self.arquivo_excel, 
                nrows=limite_registros,
                engine='openpyxl'
            )
            
            print(f"✅ Dados carregados: {len(df)} registros, {len(df.columns)} colunas")
            return df
            
        except Exception as e:
            print(f"❌ Erro ao carregar Excel: {e}")
            return pd.DataFrame()
    
    def salvar_cache(self, df):
        """Salva dados no cache usando Parquet"""
        arquivo_cache = os.path.join(self.pasta_cache, "dados_otimizados.parquet")
        
        try:
            df.to_parquet(arquivo_cache, engine='pyarrow', compression='snappy')
            print(f"💾 Cache salvo: {arquivo_cache}")
        except Exception as e:
            print(f"⚠️ Erro ao salvar cache: {e}")
    
    def carregar_cache(self):
        """Carrega dados do cache"""
        arquivo_cache = os.path.join(self.pasta_cache, "dados_otimizados.parquet")
        
        if os.path.exists(arquivo_cache):
            try:
                print("⚡ Carregando dados do cache...")
                df = pd.read_parquet(arquivo_cache)
                print(f"✅ Cache carregado: {len(df)} registros, {len(df.columns)} colunas")
                return df
            except Exception as e:
                print(f"⚠️ Erro ao carregar cache: {e}")
                return None
        
        return None
    
    def carregar_dados_inteligente(self, arquivo_excel, limite_registros=50000):
        """Carregamento inteligente com cache"""
        self.arquivo_excel = arquivo_excel
        
        # Verificar se arquivo existe
        if not os.path.exists(arquivo_excel):
            print(f"❌ Arquivo não encontrado: {arquivo_excel}")
            return pd.DataFrame()
        
        # Verificar se precisa reprocessar
        precisa_reprocessar = self.detectar_mudancas_arquivo()
        
        if not precisa_reprocessar:
            # Tentar carregar do cache
            df_cache = self.carregar_cache()
            if df_cache is not None:
                return df_cache
        
        print("🔄 Reprocessando dados...")
        
        # Carregar dados do Excel
        df = self.carregar_dados_excel(limite_registros)
        
        if df.empty:
            return df
        
        # Otimizar colunas
        df = self.limpar_e_otimizar_colunas(df)
        
        # Normalizar dados
        df = self.normalizar_dados(df)
        
        # Salvar cache
        self.salvar_cache(df)
        
        return df

# FUNÇÃO PARA STREAMLIT
@st.cache_data(ttl=3600)  # Cache por 1 hora
def carregar_dados_streamlit(arquivo_excel, limite_registros=50000):
    """
    Função otimizada para Streamlit
    ALTERAR: Mudar nome do projeto na linha abaixo
    """
    sistema = SistemaHibridoCarregamento("seu_projeto")  # ALTERAR AQUI
    return sistema.carregar_dados_inteligente(arquivo_excel, limite_registros)

# TESTE DO SISTEMA
if __name__ == "__main__":
    print("🔄 TESTE DO SISTEMA HÍBRIDO")
    print("=" * 40)
    
    # ALTERAR: Definir seu arquivo Excel aqui
    arquivo_excel = "SEU_ARQUIVO.xlsx"  # ALTERAR CAMINHO
    
    if os.path.exists(arquivo_excel):
        sistema = SistemaHibridoCarregamento("seu_projeto")  # ALTERAR NOME
        dados = sistema.carregar_dados_inteligente(arquivo_excel)
        
        print("\n📊 RESULTADO:")
        print(f"   Registros: {len(dados):,}")
        print(f"   Colunas: {len(dados.columns)}")
        print(f"   Primeiras colunas: {list(dados.columns[:3])}")
        
        # Mostrar estatísticas básicas
        if len(dados) > 0:
            print("\n📋 COLUNAS DISPONÍVEIS:")
            for i, col in enumerate(dados.columns, 1):
                print(f"   {i:2d}. {col}")
        
    else:
        print(f"❌ Arquivo não encontrado: {arquivo_excel}")
        print(f"📁 Diretório atual: {os.getcwd()}")
        print("\n💡 PRÓXIMOS PASSOS:")
        print("1. Altere a variável 'arquivo_excel' para o caminho correto")
        print("2. Implemente suas regras de normalização")
        print("3. Execute novamente para testar")
    
    input("\nPressione Enter para sair...")