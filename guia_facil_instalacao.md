# Guia Rápido de Instalação Local - JGR Broker Follow-Up

## Requisitos
- Python 3.8 ou superior (verifique se já está instalado executando `python --version` no prompt de comando)
- Pasta do projeto extraída em C:\Users\JOSY RIBEIRO\Downloads\JGRFUP

## Passo 1: Abrir o Prompt de Comando como Administrador
1. Pressione a tecla Windows
2. Digite "cmd"
3. Clique com o botão direito em "Prompt de Comando"
4. Selecione "Executar como administrador"

## Passo 2: Navegar até a pasta do projeto
```
cd C:\Users\JOSY RIBEIRO\Downloads\JGRFUP
```

## Passo 3: Instalar as dependências necessárias
Execute este comando para instalar todas as bibliotecas necessárias:
```
pip install streamlit pandas openpyxl xlsxwriter
```

## Passo 4: Iniciar a aplicação
Execute este comando para iniciar o sistema:
```
streamlit run app.py
```

Após executar o comando acima, o sistema abrirá automaticamente em seu navegador padrão. Se não abrir, acesse: http://localhost:8501

## Passo 5: Criando um atalho na área de trabalho (opcional)
1. Crie um arquivo de texto na pasta do projeto com o nome `iniciar_jgr.bat`
2. Abra o arquivo e adicione o seguinte conteúdo:
```
@echo off
cd /d %~dp0
echo Iniciando JGR Broker Follow-Up...
python -m streamlit run app.py
pause
```
3. Salve o arquivo
4. Crie um atalho para este arquivo .bat na área de trabalho

## Solução de Problemas

### Se ocorrer erro "streamlit não é reconhecido como um comando"
Execute este comando alternativo:
```
python -m streamlit run app.py
```

### Se ocorrer erro de módulo não encontrado
Certifique-se de que todos os arquivos do projeto estão na pasta e que você instalou todas as dependências.

### Caso precise reinstalar completamente:
```
pip uninstall streamlit pandas openpyxl xlsxwriter -y
pip install streamlit pandas openpyxl xlsxwriter
```

## Arquivos de Dados
- Os dados são salvos automaticamente no arquivo `data.json`
- Usuários são salvos em `users.json`
- Os backups são criados automaticamente em arquivos com nome `data_backup_DATA_HORA.json`

Para qualquer dúvida adicional, entre em contato com o suporte.