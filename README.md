# 📊 Dashboard e Relatórios - Troca de Notas TERLOC

Este projeto foi desenvolvido para analisar e visualizar dados da planilha "PLANILHA TROCA DE NOTA TERLOC.xlsx", gerando relatórios completos e um dashboard interativo.

## 🚀 Funcionalidades

### 1. Dashboard Interativo (`dashboard.py`)
- **Visualização em tempo real** dos dados
- **Métricas principais**: Total de TERLOCs, e-mails cadastrados, taxa de completude
- **Gráficos interativos**: Distribuição por categoria, status de e-mails
- **Filtros dinâmicos**: Por categoria e status de e-mail
- **Tabela detalhada** com todos os registros
- **Relatório para download** em formato texto

### 2. Gerador de Relatórios (`gerador_relatorios.py`)
- **Relatório HTML**: Página web completa com gráficos e tabelas
- **Dados JSON**: Exportação estruturada para integração com outros sistemas
- **Gráficos em PNG**: Visualizações salvas como imagens
- **CSV processado**: Dados limpos e categorizados
- **Resumo executivo**: Análise textual com recomendações

### 3. Análise Básica (`analise_planilha.py`)
- **Análise estrutural** da planilha
- **Estatísticas descritivas**
- **Exportação simples** para CSV

## 📋 Pré-requisitos

- Python 3.7 ou superior
- Arquivo "PLANILHA TROCA DE NOTA TERLOC.xlsx" no diretório do projeto

## 🔧 Instalação

1. **Clone ou baixe os arquivos** do projeto
2. **Instale as dependências**:
   ```bash
   pip install pandas openpyxl plotly streamlit numpy matplotlib seaborn
   ```

## 🎯 Como Usar

### Executar Dashboard Interativo
```bash
streamlit run dashboard.py
```
- Abre automaticamente no navegador (geralmente em http://localhost:8501)
- Interface interativa com filtros e visualizações em tempo real

### Gerar Relatórios Completos
```bash
python gerador_relatorios.py
```
- Cria uma pasta com timestamp contendo todos os relatórios
- Inclui HTML, JSON, gráficos PNG e CSV

### Análise Rápida
```bash
python analise_planilha.py
```
- Exibe análise básica no terminal
- Gera arquivo CSV simples

## 📊 Estrutura dos Dados

A planilha contém as seguintes informações principais:
- **TERLOC**: Nome/código do TERLOC
- **E-MAIL**: Endereço de e-mail associado
- **Categorias automáticas**: Expedição, Compras, Vendas, Administrativo, Operacional

## 📈 Métricas Calculadas

- **Taxa de Completude**: Percentual de TERLOCs com e-mail cadastrado
- **Distribuição por Categoria**: Agrupamento automático baseado no nome
- **Análise de Domínios**: Verificação dos domínios de e-mail
- **Estatísticas de Nomenclatura**: Tamanho médio, presença de números

## 🎨 Dashboard - Funcionalidades

### Métricas Principais
- Total de TERLOCs cadastrados
- Quantidade de e-mails preenchidos
- E-mails faltando
- Domínios únicos encontrados

### Visualizações
- **Gráfico de Pizza**: Distribuição por categorias
- **Gráfico de Barras**: Status dos e-mails (cadastrados vs faltando)
- **Tabela Interativa**: Dados detalhados com filtros

### Filtros Disponíveis
- **Por Categoria**: Expedição, Compras, Vendas, etc.
- **Por Status de E-mail**: Com e-mail, sem e-mail, todos

## 📄 Tipos de Relatório Gerados

### 1. Relatório HTML
- Página web completa e responsiva
- Gráficos integrados
- Tabelas formatadas
- Pronto para compartilhamento

### 2. Dados JSON
- Estrutura completa dos dados
- Estatísticas calculadas
- Formato ideal para APIs e integrações

### 3. Gráficos PNG
- `distribuicao_categorias.png`: Pizza com categorias
- `status_emails.png`: Barras com status de e-mails
- `tamanho_nomes.png`: Histograma do tamanho dos nomes

### 4. CSV Processado
- Dados limpos e categorizados
- Colunas derivadas incluídas
- Encoding UTF-8 com BOM

## 🔍 Análises Automáticas

### Categorização Inteligente
Os TERLOCs são automaticamente categorizados baseado em palavras-chave:
- **Expedição**: Contém "EXP" ou "EXPEDI"
- **Compras**: Contém "COMPRAS" ou "COMPRA"
- **Vendas**: Contém "VENDAS" ou "VENDA"
- **Administrativo**: Contém "ADMIN" ou "ADMINISTRA"
- **Operacional**: Demais casos

### Validações Automáticas
- Verificação de e-mails válidos
- Análise de domínios
- Detecção de duplicatas
- Identificação de padrões

## 📊 Interpretação dos Resultados

### Taxa de Completude
- **≥90%**: Excelente - Base de dados bem completa
- **70-89%**: Bom - Algumas lacunas a preencher
- **<70%**: Atenção - Muitos e-mails faltando

### Recomendações Automáticas
O sistema gera recomendações baseadas na análise:
1. Priorização de cadastros faltantes
2. Validação de e-mails existentes
3. Padronização de nomenclatura
4. Processo de atualização regular

## 🛠️ Personalização

### Modificar Categorias
Edite a função `categorizar_terloc()` nos arquivos para personalizar as categorias.

### Adicionar Métricas
Inclua novas análises nos métodos de estatísticas dos arquivos Python.

### Customizar Dashboard
Modifique cores, layout e componentes no arquivo `dashboard.py`.

## 📁 Estrutura de Arquivos Gerados

```
relatorio_YYYYMMDD_HHMMSS/
├── relatorio.html          # Relatório web completo
├── dados.json             # Dados estruturados
├── dados_processados.csv  # CSV limpo
├── resumo_executivo.txt   # Análise textual
└── graficos/
    ├── distribuicao_categorias.png
    ├── status_emails.png
    └── tamanho_nomes.png
```

## 🚨 Solução de Problemas

### Erro de Codificação
Se aparecerem caracteres especiais incorretos, verifique se o terminal suporta UTF-8.

### Arquivo não encontrado
Certifique-se de que "PLANILHA TROCA DE NOTA TERLOC.xlsx" está no mesmo diretório dos scripts.

### Dependências
Se alguma biblioteca não estiver instalada:
```bash
pip install -r requirements.txt
```

## 📞 Suporte

Para dúvidas ou problemas:
1. Verifique se todos os arquivos estão no diretório correto
2. Confirme que as dependências estão instaladas
3. Execute primeiro `analise_planilha.py` para validar os dados

## 🔄 Atualizações Futuras

- Integração com banco de dados
- Exportação para PowerBI
- Notificações automáticas
- API REST para consultas
- Interface web própria (sem Streamlit)

---
*Desenvolvido para análise eficiente da planilha Troca de Notas TERLOC*