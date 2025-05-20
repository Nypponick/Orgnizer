# Guia Simplificado para Hospedar o Sistema de Importação JGR

Este guia explica como hospedar o sistema de acompanhamento de importação da JGR Broker de forma simples, sem necessidade de conhecimentos técnicos avançados.

## Opção 1: Streamlit Community Cloud (Mais Fácil)

### O que você precisa:
- Uma conta de e-mail
- Acesso à internet

### Passos:

#### 1. Prepare seu código
- Baixe todo o código do sistema para seu computador
- Certifique-se de que todos os arquivos estão juntos em uma mesma pasta

#### 2. Crie uma conta no GitHub
- Acesse [github.com](https://github.com)
- Clique em "Sign up" e siga as instruções para criar uma conta gratuita
- Use seu e-mail e crie uma senha

#### 3. Crie um repositório para seu projeto
- Após fazer login no GitHub, clique no botão "+" no canto superior direito
- Selecione "New repository"
- Dê um nome ao repositório (por exemplo "jgr-importacao")
- Marque a opção "Private" para manter seu código privado
- Clique em "Create repository"

#### 4. Faça upload dos arquivos
- Na página do seu novo repositório, clique no botão "Add file" e selecione "Upload files"
- Arraste todos os arquivos do projeto para a área indicada ou use o navegador de arquivos
- Quando terminar, clique em "Commit changes" na parte inferior da página

#### 5. Crie uma conta no Streamlit Community Cloud
- Acesse [streamlit.io/cloud](https://streamlit.io/cloud)
- Clique em "Sign up" e faça login com sua conta do GitHub que acabou de criar

#### 6. Implante o aplicativo
- Após fazer login no Streamlit Cloud, clique em "New app"
- Em "Repository", selecione o repositório que você criou
- Em "Branch", escolha "main"
- Em "Main file path", digite "app.py"
- Em "App name", escolha um nome para seu aplicativo
- Clique em "Deploy"

#### 7. Configure seu aplicativo
- Após a implantação (pode demorar alguns minutos), clique no botão "Settings" no canto superior direito do aplicativo
- Em "Secrets", adicione suas credenciais se necessário (como TWILIO_ACCOUNT_SID, etc.)
- Exemplo:
  ```
  TWILIO_ACCOUNT_SID = "seu_sid_aqui"
  TWILIO_AUTH_TOKEN = "seu_token_aqui"
  TWILIO_PHONE_NUMBER = "seu_numero_aqui"
  ```

Pronto! Seu aplicativo agora está hospedado e acessível através do link fornecido pelo Streamlit Cloud (algo como https://seu-app-nome.streamlit.app).

## Opção 2: PythonAnywhere (Alternativa Simples)

Se preferir outra opção, o PythonAnywhere também é relativamente fácil de configurar:

### O que você precisa:
- Uma conta de e-mail
- Cartão de crédito para o plano pago (o plano gratuito tem limitações)

### Passos:

#### 1. Crie uma conta no PythonAnywhere
- Acesse [pythonanywhere.com](https://www.pythonanywhere.com)
- Clique em "Pricing & signup" e escolha um plano (recomendamos o "Hacker" para começar)
- Siga as instruções para criar sua conta

#### 2. Configure seu ambiente
- No painel do PythonAnywhere, clique em "Consoles" e depois em "Bash"
- No console, digite os seguintes comandos:
  ```
  mkdir -p ~/jgr_importacao
  cd ~/jgr_importacao
  python -m venv venv
  source venv/bin/activate
  ```

#### 3. Faça upload dos arquivos
- Volte ao painel principal e clique em "Files"
- Navegue até a pasta "jgr_importacao" que você criou
- Use o botão "Upload a file" para fazer upload de todos os arquivos do projeto

#### 4. Instale as dependências
- Volte ao console Bash e digite:
  ```
  cd ~/jgr_importacao
  source venv/bin/activate
  pip install streamlit pandas twilio xlsxwriter
  ```

#### 5. Configure uma aplicação web
- No painel, clique em "Web"
- Clique em "Add a new web app"
- Escolha "Manual configuration"
- Selecione a versão mais recente do Python
- Na seção "Code", defina o diretório como "/home/seu_username/jgr_importacao"
- Em "WSGI configuration file", adicione o código para executar o Streamlit

#### 6. Configure o Streamlit
- Em "Files", crie um arquivo chamado "run_streamlit.py" com o seguinte conteúdo:
  ```python
  import os
  os.system('cd /home/seu_username/jgr_importacao && source venv/bin/activate && streamlit run app.py --server.port 8501 --server.address 0.0.0.0')
  ```

#### 7. Configure um serviço Always-on
- No painel, clique em "Tasks"
- Adicione uma tarefa que execute o script "run_streamlit.py"

Seu aplicativo estará disponível no URL fornecido pelo PythonAnywhere (algo como seu_username.pythonanywhere.com).

## Observações Importantes:

- **Dados**: Os dados do sistema (processos, usuários) são armazenados em arquivos JSON, que ficarão no servidor. Faça backup periódicos.
- **Atualizações**: Para atualizar o aplicativo, você precisará fazer upload dos novos arquivos e reiniciar o serviço.
- **Privacidade**: Considere usar HTTPS para proteger os dados transferidos (o Streamlit Cloud já fornece isso automaticamente).
- **Suporte**: Em caso de dúvidas ou problemas, considere contratar um profissional para ajudar com a configuração inicial.

## Recomendação Final

Para a maioria dos usuários sem conhecimento técnico, recomendamos fortemente a **Opção 1 (Streamlit Community Cloud)** por ser:

- Mais simples de configurar
- Não requer manutenção de servidor
- Inclui HTTPS automaticamente
- Atualizações mais fáceis
- Específico para aplicativos Streamlit