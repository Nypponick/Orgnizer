# Instruções Simples de Instalação - JGR Broker Follow-Up

## O que você precisa ter instalado
1. Python (versão 3.8 ou superior)
2. Todas as dependências (instaladas pelo pip no passo 3 abaixo)

## Como instalar passo a passo

### Passo 1: Verifique se o Python está instalado
Abra o prompt de comando e digite:
```
python --version
```
Você deve ver algo como "Python 3.x.x". Se não aparecer, significa que o Python não está instalado ou não está no PATH.

### Passo 2: Abra o prompt de comando na pasta do projeto
1. Abra o prompt de comando
2. Digite: `cd C:\Users\JOSY RIBEIRO\Downloads\JGRFUP`
3. Pressione Enter

### Passo 3: Instale as dependências necessárias
Digite este comando:
```
pip install streamlit pandas openpyxl xlsxwriter
```
Aguarde até que todas as dependências sejam instaladas.

### Passo 4: Inicie o aplicativo
Digite este comando:
```
streamlit run app.py
```
O aplicativo deve abrir automaticamente em seu navegador.

### Passo 5: (Opcional) Use o arquivo .bat para iniciar facilmente
Na pasta do projeto, dê um duplo clique no arquivo `iniciar_jgr.bat` para iniciar o aplicativo sem precisar usar o prompt de comando.

## Problemas comuns:

1. **Erro "python não é reconhecido como um comando"**:
   - O Python não está no PATH
   - Solução: Reinstale o Python e certifique-se de marcar a opção "Add Python to PATH" durante a instalação

2. **Erro "streamlit não é reconhecido como um comando"**:
   - Tente usar: `python -m streamlit run app.py`

3. **Erro "módulo não encontrado"**:
   - Certifique-se de que todos os arquivos do projeto estão presentes na pasta
   - Verifique se todas as dependências foram instaladas corretamente

4. **Aplicativo abre mas aparece tela em branco ou erro**:
   - Verifique se os arquivos `data.json` e `users.json` existem na pasta do projeto
   - Se não existirem, o sistema criará novos arquivos vazios

## Observações importantes:
- Os dados são salvos localmente nos arquivos `data.json` e `users.json`
- O sistema faz backups automáticos periodicamente
- Para acessar o sistema, use o usuário administrador padrão: 
  - Username: `admin`
  - Senha: `admin`