# Preparação para Deploy na Hostinger

Este documento contém instruções para preparar seu projeto para deploy na Hostinger.

## Arquivos Necessários

Para deploy na Hostinger, você precisará dos seguintes arquivos e pastas:

1. **Código-fonte da aplicação**:
   - `app.py` (arquivo principal)
   - Pasta `components/` com todos os módulos 
   - Pasta `assets/` com recursos visuais
   - `.streamlit/config.toml` já configurado

2. **Arquivos de configuração**:
   - `requirements.txt`: Lista todas as dependências necessárias
   - `run.sh`: Script para iniciar a aplicação (vamos criar em seguida)

3. **Arquivos de dados**:
   - `data.json`: Banco de dados de processos (se desejar migrar os dados existentes)
   - `users.json`: Banco de dados de usuários (se desejar migrar os usuários existentes)

## Passo a Passo de Preparação

### 1. Verifique a versão atualizada dos arquivos

Antes de iniciar o processo de deploy, certifique-se de ter as versões mais recentes dos seguintes arquivos:
- `components/event_log.py`: Correção dos botões de edição/exclusão
- `data.py`: Melhorias nas funções de manipulação de eventos
- `components/home.py`: Filtros de status atualizados
- `html_generator.py`: Correção dos contadores de status na exportação HTML

### 2. Crie um arquivo `requirements.txt`

Crie um arquivo chamado `requirements.txt` com o seguinte conteúdo:

```
streamlit==1.31.0
pandas==2.1.4
twilio==8.13.0
xlsxwriter==3.1.9
openpyxl==3.1.2
```

### 3. Crie um script de inicialização `run.sh`

Crie um arquivo chamado `run.sh` com o seguinte conteúdo (substitua `usuario` pelo seu nome de usuário na Hostinger):

```bash
#!/bin/bash
cd /home/usuario/public_html/jgr_app
source venv/bin/activate
streamlit run app.py --server.port 8501 --server.address 0.0.0.0
```

### 4. Organize todos os arquivos para deploy

Crie uma pasta chamada `deploy_jgr` em seu computador local e copie todos os seguintes arquivos e pastas:

- Pasta `components/`
- Pasta `assets/`
- Pasta `.streamlit/`
- `app.py`
- `data.py`
- `utils.py`
- `html_generator.py`
- `requirements.txt`
- `run.sh`
- `data.json` (se quiser manter os dados atuais)
- `users.json` (se quiser manter os usuários atuais)
- Quaisquer outros arquivos necessários para o funcionamento da aplicação

### 5. Compacte os arquivos

Compacte a pasta `deploy_jgr` em um arquivo ZIP para facilitar o upload para a Hostinger:

1. Clique com o botão direito na pasta `deploy_jgr`
2. Selecione "Compactar" ou "Enviar para > Pasta compactada"
3. Salve o arquivo ZIP em um local de fácil acesso

## Próximos Passos

Depois de preparar todos os arquivos necessários, siga o guia `guia_deploy_hostinger.md` para realizar o deploy na Hostinger.

## Observações Importantes

- Certifique-se de que a configuração na Hostinger suporta Python e permite a execução de processos em segundo plano.
- Considere usar o serviço Streamlit Cloud como alternativa se enfrentar dificuldades no deploy na Hostinger.
- Faça um backup completo da sua aplicação antes de realizar o deploy.
- Se dados confidenciais estiverem armazenados, certifique-se de que a conexão esteja protegida com HTTPS.