import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import streamlit as st
from datetime import datetime
import os

class AnalisadorPlanilha:
    def __init__(self, caminho_arquivo):
        self.caminho_arquivo = caminho_arquivo
        self.dados = None
        self.info_planilha = {}
        
    def carregar_dados(self):
        """Carrega os dados da planilha Excel"""
        try:
            # Tenta carregar a planilha
            self.dados = pd.read_excel(self.caminho_arquivo)
            print("✅ Planilha carregada com sucesso!")
            return True
        except Exception as e:
            print(f"❌ Erro ao carregar a planilha: {str(e)}")
            return False
    
    def analisar_estrutura(self):
        """Analisa a estrutura básica da planilha"""
        if self.dados is None:
            print("❌ Dados não carregados. Execute carregar_dados() primeiro.")
            return None
        
        self.info_planilha = {
            'total_linhas': len(self.dados),
            'total_colunas': len(self.dados.columns),
            'colunas': list(self.dados.columns),
            'tipos_dados': dict(self.dados.dtypes),
            'valores_nulos': dict(self.dados.isnull().sum()),
            'memoria_uso': self.dados.memory_usage(deep=True).sum() / 1024**2  # MB
        }
        
        return self.info_planilha
    
    def exibir_resumo(self):
        """Exibe um resumo da planilha"""
        if not self.info_planilha:
            self.analisar_estrutura()
        
        print("="*60)
        print("📊 ANÁLISE DA PLANILHA TROCA DE NOTA TERLOC")
        print("="*60)
        print(f"📋 Total de registros: {self.info_planilha['total_linhas']:,}")
        print(f"📊 Total de colunas: {self.info_planilha['total_colunas']}")
        print(f"💾 Uso de memória: {self.info_planilha['memoria_uso']:.2f} MB")
        print("\n📋 COLUNAS ENCONTRADAS:")
        print("-" * 40)
        
        for i, coluna in enumerate(self.info_planilha['colunas'], 1):
            tipo = str(self.info_planilha['tipos_dados'][coluna])
            nulos = self.info_planilha['valores_nulos'][coluna]
            print(f"{i:2d}. {coluna} ({tipo}) - {nulos} valores nulos")
        
        print("\n📋 PRIMEIRAS 5 LINHAS:")
        print("-" * 40)
        print(self.dados.head())
        
        print("\n📊 ESTATÍSTICAS DESCRITIVAS:")
        print("-" * 40)
        print(self.dados.describe(include='all'))
    
    def exportar_resumo(self, nome_arquivo="resumo_planilha.txt"):
        """Exporta o resumo para um arquivo texto"""
        if not self.info_planilha:
            self.analisar_estrutura()
        
        with open(nome_arquivo, 'w', encoding='utf-8') as f:
            f.write("ANÁLISE DA PLANILHA TROCA DE NOTA TERLOC\n")
            f.write("="*60 + "\n")
            f.write(f"Data da análise: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n")
            f.write(f"Arquivo analisado: {self.caminho_arquivo}\n\n")
            
            f.write(f"Total de registros: {self.info_planilha['total_linhas']:,}\n")
            f.write(f"Total de colunas: {self.info_planilha['total_colunas']}\n")
            f.write(f"Uso de memória: {self.info_planilha['memoria_uso']:.2f} MB\n\n")
            
            f.write("COLUNAS ENCONTRADAS:\n")
            f.write("-" * 40 + "\n")
            for i, coluna in enumerate(self.info_planilha['colunas'], 1):
                tipo = str(self.info_planilha['tipos_dados'][coluna])
                nulos = self.info_planilha['valores_nulos'][coluna]
                f.write(f"{i:2d}. {coluna} ({tipo}) - {nulos} valores nulos\n")
            
            f.write("\nPRIMEIRAS 5 LINHAS:\n")
            f.write("-" * 40 + "\n")
            f.write(str(self.dados.head()))
        
        print(f"✅ Resumo exportado para: {nome_arquivo}")

def main():
    # Caminho para a planilha
    caminho_planilha = "PLANILHA TROCA DE NOTA TERLOC.xlsx"
    
    if not os.path.exists(caminho_planilha):
        print(f"❌ Arquivo não encontrado: {caminho_planilha}")
        return
    
    # Criar analisador
    analisador = AnalisadorPlanilha(caminho_planilha)
    
    # Carregar e analisar dados
    if analisador.carregar_dados():
        analisador.exibir_resumo()
        analisador.exportar_resumo()
        
        # Salvar dados em formato CSV para facilitar análises futuras
        analisador.dados.to_csv("dados_terloc.csv", index=False, encoding='utf-8-sig')
        print("✅ Dados exportados para: dados_terloc.csv")

if __name__ == "__main__":
    main()