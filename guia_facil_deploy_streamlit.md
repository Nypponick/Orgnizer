# Guia Fácil de Deploy no Streamlit Cloud

Este guia simplificado explica como fazer o deploy do aplicativo JGR Broker no Streamlit Cloud para testes.

## Passo 1: Preparar um repositório no GitHub

1. Crie uma conta no GitHub (caso ainda não tenha)
2. Crie um novo repositório (pode ser privado)
3. Faça upload de todos os arquivos do projeto para o repositório

## Passo 2: Verificar arquivos essenciais

Certifique-se de que seu repositório contenha:

- `app.py` (arquivo principal)
- `data.py` e `data.json` (para gerenciamento de dados)
- `users.json` (para autenticação)
- `components/__init__.py` (pasta com o arquivo de inicialização)
- `assets/__init__.py` (pasta com o arquivo de inicialização)
- `streamlit_deploy_requirements.txt` (renomeie para `requirements.txt`)
- `.streamlit/config.toml` (configurações do Streamlit)

## Passo 3: Preparar o requirements.txt

Renomeie o arquivo `streamlit_deploy_requirements.txt` para `requirements.txt` e certifique-se de que ele contenha as dependências necessárias:

```
streamlit==1.36.0
pandas==2.1.4
openpyxl==3.1.2
xlsxwriter==3.1.9
twilio==8.10.0
```

## Passo 4: Fazer deploy no Streamlit Cloud

1. Acesse [share.streamlit.io](https://share.streamlit.io)
2. Faça login com sua conta do GitHub
3. Clique em "New app"
4. Selecione seu repositório
5. Configure:
   - **Repository**: seu-usuario/seu-repositorio
   - **Branch**: main
   - **Main file path**: app.py
   - **Python version**: 3.11

6. Clique em "Deploy!"

## Passo 5: Acessar o aplicativo

Após o deploy, você receberá um link para acessar o aplicativo, geralmente no formato:
`https://seu-usuario-seu-repositorio.streamlit.app`

## Observações importantes

- **Dados**: No Streamlit Cloud, os dados não são persistentes. A cada atualização os arquivos `data.json` e `users.json` voltarão ao estado do repositório.
- **Arquivos temporários**: A pasta `html_exports` será recriada a cada execução e seus arquivos não serão preservados.
- **Atualizações**: Para atualizar o aplicativo, basta fazer commit das alterações no repositório GitHub.

## Solução de problemas comuns

Se ocorrer erro de módulos não encontrados:
- Certifique-se de que as pastas `components` e `assets` tenham arquivos `__init__.py`
- Verifique se todos os arquivos estão na estrutura correta
- Alguns imports podem precisar ser ajustados para caminhos relativos

Para mais detalhes, consulte a documentação completa do Streamlit: [docs.streamlit.io](https://docs.streamlit.io/)