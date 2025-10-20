import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import json
import os

class GeradorRelatorios:
    def __init__(self, arquivo_excel):
        self.arquivo_excel = arquivo_excel
        self.dados = None
        self.dados_processados = None
        self.carregar_dados()
    
    def carregar_dados(self):
        """Carrega e processa os dados"""
        try:
            self.dados = pd.read_excel(self.arquivo_excel)
            self.processar_dados()
            print("✅ Dados carregados e processados com sucesso!")
        except Exception as e:
            print(f"❌ Erro ao carregar dados: {str(e)}")
    
    def processar_dados(self):
        """Processa e enriquece os dados"""
        # Limpar dados
        self.dados_processados = self.dados[['TERLOC', 'E-MAIL']].copy()
        self.dados_processados = self.dados_processados.dropna(subset=['TERLOC'])
        
        # Adicionar colunas derivadas
        self.dados_processados['TEM_EMAIL'] = self.dados_processados['E-MAIL'].notna()
        self.dados_processados['DOMINIO_EMAIL'] = self.dados_processados['E-MAIL'].str.extract(r'@(.+)')
        
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
        
        self.dados_processados['CATEGORIA'] = self.dados_processados['TERLOC'].apply(categorizar_terloc)
        
        # Adicionar mais informações
        self.dados_processados['TAMANHO_NOME'] = self.dados_processados['TERLOC'].str.len()
        self.dados_processados['TEM_NUMERO'] = self.dados_processados['TERLOC'].str.contains(r'\d+', na=False)
    
    def gerar_estatisticas(self):
        """Gera estatísticas completas"""
        if self.dados_processados is None:
            return None
        
        stats = {
            'data_analise': datetime.now().strftime('%d/%m/%Y %H:%M:%S'),
            'total_registros': len(self.dados_processados),
            'emails_cadastrados': int(self.dados_processados['TEM_EMAIL'].sum()),
            'emails_faltando': int((~self.dados_processados['TEM_EMAIL']).sum()),
            'taxa_completude': float(self.dados_processados['TEM_EMAIL'].mean() * 100),
            'distribuicao_categorias': dict(self.dados_processados['CATEGORIA'].value_counts()),
            'dominios_email': dict(self.dados_processados['DOMINIO_EMAIL'].value_counts().dropna()),
            'terlocs_unicos': int(self.dados_processados['TERLOC'].nunique()),
            'emails_unicos': int(self.dados_processados['E-MAIL'].nunique()),
            'tamanho_medio_nome': float(self.dados_processados['TAMANHO_NOME'].mean()),
            'terlocs_com_numero': int(self.dados_processados['TEM_NUMERO'].sum())
        }
        
        return stats
    
    def gerar_relatorio_html(self, nome_arquivo="relatorio_terloc.html"):
        """Gera relatório em HTML"""
        stats = self.gerar_estatisticas()
        if not stats:
            return False
        
        html_content = f"""
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Relatório TERLOC - {stats['data_analise']}</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f5;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background-color: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        .header {{
            text-align: center;
            color: #2c3e50;
            border-bottom: 3px solid #3498db;
            padding-bottom: 20px;
            margin-bottom: 30px;
        }}
        .metric-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin: 20px 0;
        }}
        .metric-card {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            border-radius: 10px;
            text-align: center;
        }}
        .metric-value {{
            font-size: 2.5em;
            font-weight: bold;
            margin: 10px 0;
        }}
        .metric-label {{
            font-size: 1.1em;
            opacity: 0.9;
        }}
        .section {{
            margin: 30px 0;
            padding: 20px;
            background-color: #f8f9fa;
            border-radius: 8px;
        }}
        .section h2 {{
            color: #2c3e50;
            border-left: 4px solid #3498db;
            padding-left: 15px;
        }}
        .progress-bar {{
            width: 100%;
            height: 20px;
            background-color: #ecf0f1;
            border-radius: 10px;
            overflow: hidden;
            margin: 10px 0;
        }}
        .progress-fill {{
            height: 100%;
            background: linear-gradient(90deg, #2ecc71, #27ae60);
            transition: width 0.3s ease;
        }}
        .category-list {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
        }}
        .category-item {{
            background: white;
            padding: 15px;
            border-radius: 8px;
            border-left: 4px solid #3498db;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
        }}
        th, td {{
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #ddd;
        }}
        th {{
            background-color: #3498db;
            color: white;
        }}
        .status-ok {{ color: #27ae60; font-weight: bold; }}
        .status-missing {{ color: #e74c3c; font-weight: bold; }}
        .footer {{
            text-align: center;
            margin-top: 40px;
            padding-top: 20px;
            border-top: 1px solid #bdc3c7;
            color: #7f8c8d;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📊 Relatório de Análise - Troca de Notas TERLOC</h1>
            <p>Data: {stats['data_analise']}</p>
        </div>
        
        <div class="metric-grid">
            <div class="metric-card">
                <div class="metric-value">{stats['total_registros']}</div>
                <div class="metric-label">Total de TERLOCs</div>
            </div>
            <div class="metric-card">
                <div class="metric-value">{stats['emails_cadastrados']}</div>
                <div class="metric-label">E-mails Cadastrados</div>
            </div>
            <div class="metric-card">
                <div class="metric-value">{stats['emails_faltando']}</div>
                <div class="metric-label">E-mails Faltando</div>
            </div>
            <div class="metric-card">
                <div class="metric-value">{stats['taxa_completude']:.1f}%</div>
                <div class="metric-label">Taxa de Completude</div>
            </div>
        </div>
        
        <div class="section">
            <h2>📈 Análise de Completude</h2>
            <p>Taxa de e-mails cadastrados:</p>
            <div class="progress-bar">
                <div class="progress-fill" style="width: {stats['taxa_completude']:.1f}%;"></div>
            </div>
            <p><strong>{stats['taxa_completude']:.1f}%</strong> dos TERLOCs possuem e-mail cadastrado.</p>
        </div>
        
        <div class="section">
            <h2>📊 Distribuição por Categoria</h2>
            <div class="category-list">
"""
        
        for categoria, quantidade in stats['distribuicao_categorias'].items():
            percentual = (quantidade / stats['total_registros']) * 100
            html_content += f"""
                <div class="category-item">
                    <strong>{categoria}</strong><br>
                    {quantidade} TERLOCs ({percentual:.1f}%)
                </div>
"""
        
        html_content += f"""
            </div>
        </div>
        
        <div class="section">
            <h2>📧 Domínios de E-mail</h2>
            <table>
                <thead>
                    <tr>
                        <th>Domínio</th>
                        <th>Quantidade</th>
                        <th>Percentual</th>
                    </tr>
                </thead>
                <tbody>
"""
        
        for dominio, quantidade in stats['dominios_email'].items():
            percentual = (quantidade / stats['emails_cadastrados']) * 100
            html_content += f"""
                    <tr>
                        <td>{dominio}</td>
                        <td>{quantidade}</td>
                        <td>{percentual:.1f}%</td>
                    </tr>
"""
        
        html_content += """
                </tbody>
            </table>
        </div>
        
        <div class="section">
            <h2>📋 Lista Completa de TERLOCs</h2>
            <table>
                <thead>
                    <tr>
                        <th>TERLOC</th>
                        <th>E-mail</th>
                        <th>Categoria</th>
                        <th>Status</th>
                    </tr>
                </thead>
                <tbody>
"""
        
        for _, row in self.dados_processados.iterrows():
            status_class = "status-ok" if row['TEM_EMAIL'] else "status-missing"
            status_text = "✅ Cadastrado" if row['TEM_EMAIL'] else "❌ Faltando"
            email_display = row['E-MAIL'] if pd.notna(row['E-MAIL']) else "-"
            
            html_content += f"""
                    <tr>
                        <td>{row['TERLOC']}</td>
                        <td>{email_display}</td>
                        <td>{row['CATEGORIA']}</td>
                        <td class="{status_class}">{status_text}</td>
                    </tr>
"""
        
        html_content += f"""
                </tbody>
            </table>
        </div>
        
        <div class="footer">
            <p>Relatório gerado automaticamente • {stats['data_analise']}</p>
        </div>
    </div>
</body>
</html>
"""
        
        with open(nome_arquivo, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f"✅ Relatório HTML gerado: {nome_arquivo}")
        return True
    
    def gerar_relatorio_json(self, nome_arquivo="dados_terloc.json"):
        """Gera relatório em JSON"""
        stats = self.gerar_estatisticas()
        if not stats:
            return False
        
        # Adicionar dados detalhados
        dados_json = {
            'estatisticas': stats,
            'dados_detalhados': self.dados_processados.to_dict('records')
        }
        
        with open(nome_arquivo, 'w', encoding='utf-8') as f:
            json.dump(dados_json, f, indent=2, ensure_ascii=False, default=str)
        
        print(f"✅ Dados JSON gerados: {nome_arquivo}")
        return True
    
    def gerar_graficos(self, pasta_destino="graficos"):
        """Gera gráficos e salva como imagens"""
        if not os.path.exists(pasta_destino):
            os.makedirs(pasta_destino)
        
        plt.style.use('seaborn-v0_8')
        
        # Gráfico 1: Distribuição por categoria
        plt.figure(figsize=(10, 6))
        dist_cat = self.dados_processados['CATEGORIA'].value_counts()
        plt.pie(dist_cat.values, labels=dist_cat.index, autopct='%1.1f%%', startangle=90)
        plt.title('Distribuição de TERLOCs por Categoria', fontsize=16, fontweight='bold')
        plt.axis('equal')
        plt.tight_layout()
        plt.savefig(f'{pasta_destino}/distribuicao_categorias.png', dpi=300, bbox_inches='tight')
        plt.close()
        
        # Gráfico 2: Status dos e-mails
        plt.figure(figsize=(8, 6))
        status_counts = self.dados_processados['TEM_EMAIL'].value_counts()
        labels = ['E-mail Cadastrado', 'E-mail Faltando']
        colors = ['#2ecc71', '#e74c3c']
        
        bars = plt.bar(labels, [status_counts.get(True, 0), status_counts.get(False, 0)], color=colors)
        plt.title('Status dos E-mails Cadastrados', fontsize=16, fontweight='bold')
        plt.ylabel('Quantidade')
        
        # Adicionar valores nas barras
        for bar in bars:
            height = bar.get_height()
            plt.text(bar.get_x() + bar.get_width()/2., height + 0.5,
                    f'{int(height)}', ha='center', va='bottom', fontweight='bold')
        
        plt.tight_layout()
        plt.savefig(f'{pasta_destino}/status_emails.png', dpi=300, bbox_inches='tight')
        plt.close()
        
        # Gráfico 3: Tamanho dos nomes TERLOC
        plt.figure(figsize=(10, 6))
        plt.hist(self.dados_processados['TAMANHO_NOME'], bins=15, alpha=0.7, color='skyblue', edgecolor='black')
        plt.title('Distribuição do Tamanho dos Nomes TERLOC', fontsize=16, fontweight='bold')
        plt.xlabel('Número de Caracteres')
        plt.ylabel('Frequência')
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        plt.savefig(f'{pasta_destino}/tamanho_nomes.png', dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"✅ Gráficos gerados na pasta: {pasta_destino}")
        return True
    
    def gerar_relatorio_completo(self):
        """Gera todos os tipos de relatório"""
        print("🚀 Iniciando geração de relatórios completos...")
        
        # Criar pasta para relatórios
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        pasta_relatorio = f"relatorio_{timestamp}"
        
        if not os.path.exists(pasta_relatorio):
            os.makedirs(pasta_relatorio)
        
        # Gerar relatórios
        self.gerar_relatorio_html(f"{pasta_relatorio}/relatorio.html")
        self.gerar_relatorio_json(f"{pasta_relatorio}/dados.json")
        self.gerar_graficos(f"{pasta_relatorio}/graficos")
        
        # Gerar CSV limpo
        self.dados_processados.to_csv(f"{pasta_relatorio}/dados_processados.csv", 
                                    index=False, encoding='utf-8-sig')
        
        # Gerar resumo executivo
        stats = self.gerar_estatisticas()
        resumo = f"""
RELATÓRIO EXECUTIVO - TROCA DE NOTAS TERLOC
===========================================
Data: {stats['data_analise']}

MÉTRICAS PRINCIPAIS:
• Total de TERLOCs: {stats['total_registros']}
• E-mails cadastrados: {stats['emails_cadastrados']} ({stats['taxa_completude']:.1f}%)
• E-mails faltando: {stats['emails_faltando']} ({100-stats['taxa_completude']:.1f}%)

DISTRIBUIÇÃO POR CATEGORIA:
"""
        for categoria, quantidade in stats['distribuicao_categorias'].items():
            percentual = (quantidade / stats['total_registros']) * 100
            resumo += f"• {categoria}: {quantidade} ({percentual:.1f}%)\n"
        
        resumo += f"""
ANÁLISE:
• Taxa de completude: {stats['taxa_completude']:.1f}%
• Tamanho médio do nome: {stats['tamanho_medio_nome']:.1f} caracteres
• TERLOCs com números: {stats['terlocs_com_numero']}

RECOMENDAÇÕES:
1. Completar cadastro dos {stats['emails_faltando']} e-mails faltantes
2. Validar e-mails existentes
3. Padronizar nomenclatura
4. Estabelecer processo de atualização regular
"""
        
        with open(f"{pasta_relatorio}/resumo_executivo.txt", 'w', encoding='utf-8') as f:
            f.write(resumo)
        
        print(f"✅ Relatórios completos gerados na pasta: {pasta_relatorio}")
        return pasta_relatorio

def main():
    # Verificar se o arquivo existe
    arquivo_excel = "PLANILHA TROCA DE NOTA TERLOC.xlsx"
    
    if not os.path.exists(arquivo_excel):
        print(f"❌ Arquivo não encontrado: {arquivo_excel}")
        return
    
    # Criar gerador de relatórios
    gerador = GeradorRelatorios(arquivo_excel)
    
    # Gerar relatórios completos
    pasta_relatorio = gerador.gerar_relatorio_completo()
    
    print(f"\n🎉 Processo concluído!")
    print(f"📁 Verifique a pasta: {pasta_relatorio}")

if __name__ == "__main__":
    main()