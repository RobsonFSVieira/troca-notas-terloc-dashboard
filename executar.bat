@echo off
echo ========================================
echo   DASHBOARD TROCA DE NOTAS TERLOC
echo ========================================
echo.
echo Escolha uma opcao:
echo.
echo 1. Executar Dashboard Interativo
echo 2. Gerar Relatorios Completos
echo 3. Analise Rapida da Planilha
echo 4. Sair
echo.
set /p opcao="Digite sua opcao (1-4): "

if "%opcao%"=="1" (
    echo.
    echo Iniciando dashboard interativo...
    echo O dashboard abrira automaticamente no seu navegador.
    echo.
    .venv\Scripts\streamlit.exe run dashboard.py
) else if "%opcao%"=="2" (
    echo.
    echo Gerando relatorios completos...
    .venv\Scripts\python.exe gerador_relatorios.py
    echo.
    echo Pressione qualquer tecla para continuar...
    pause >nul
) else if "%opcao%"=="3" (
    echo.
    echo Executando analise rapida...
    .venv\Scripts\python.exe analise_planilha.py
    echo.
    echo Pressione qualquer tecla para continuar...
    pause >nul
) else if "%opcao%"=="4" (
    echo.
    echo Saindo...
    exit /b
) else (
    echo.
    echo Opcao invalida. Tente novamente.
    echo.
    pause
    goto :inicio
)

echo.
echo Pressione qualquer tecla para sair...
pause >nul