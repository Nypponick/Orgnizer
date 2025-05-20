# Guia de implantação no Streamlit Cloud

Este guia explica como implantar o aplicativo JGR Broker Importação no Streamlit Cloud.

## Pré-requisitos

1. Uma conta no GitHub
2. Uma conta no [Streamlit Cloud](https://streamlit.io/)

## Passo a passo

### 1. Prepare o repositório no GitHub

1. Crie um novo repositório no GitHub
2. Carregue todos os arquivos do projeto, mantendo a estrutura de pastas:
   ```
   meu_repo/
   ├── app.py                    # Arquivo principal do Streamlit
   ├── data.py                   # Manipulação de dados
   ├── data.json                 # Banco de dados JSON
   ├── users.json                # Usuários do sistema
   ├── utils.py                  # Utilitários
   ├── requirements.txt          # Dependências
   ├── components/               # Pasta de componentes
   │   ├── __init__.py           # IMPORTANTE: Este arquivo é necessário!
   │   ├── add_edit.py
   │   ├── archived.py
   │   ├── auth.py
   │   ├── client_view.py
   │   ├── event_log.py
   │   ├── home.py
   │   ├── settings.py
   │   ├── share.py
   │   └── view_details.py
   ├── assets/                   # Pasta de recursos estáticos
   │   ├── __init__.py           # IMPORTANTE: Este arquivo é necessário!
   │   ├── custom.css            # Estilos CSS personalizados
   │   ├── stock_photos.py       # Utilitário de imagens
   │   └── images/               # Subpasta de imagens
   │       └── jgr_logo.png      # Logo e outras imagens
   ├── .streamlit/               # Configuração do Streamlit
   │   └── config.toml
   └── html_exports/             # Pasta para exportações HTML (será criada automaticamente)
   ```

3. **IMPORTANTE**: Certifique-se de que as seguintes pastas tenham arquivos `__init__.py` para serem reconhecidas como pacotes Python:
   - `components/__init__.py` 
   - `assets/__init__.py`
   
   O conteúdo desses arquivos pode ser apenas um comentário:
   ```python
   # This file is intentionally left empty to make the directory a Python package
   ```

### 2. Crie um arquivo requirements.txt

Crie um arquivo `requirements.txt` na raiz do repositório com estas dependências:

```
streamlit==1.36.0
pandas==2.1.4
openpyxl==3.1.2
xlsxwriter==3.1.9
twilio==8.10.0
```

### 3. Configuração do Streamlit

Certifique-se de que você tenha a pasta `.streamlit` com um arquivo `config.toml` contendo:

```toml
[server]
headless = true
address = "0.0.0.0"
port = 5000
```

### 4. Verificar imports

Certifique-se de que todos os imports estão usando o formato correto. Por exemplo:

```python
from components.auth import display_login
from components.home import display_home
```

### 5. Implante no Streamlit Cloud

1. Acesse [share.streamlit.io](https://share.streamlit.io)
2. Faça login com sua conta
3. Clique em "New app"
4. Selecione o repositório com seu código
5. Na configuração:
   - **Repository**: Seu repositório GitHub
   - **Branch**: main (ou master)
   - **Main file path**: app.py
   - **Advanced settings**:
     - **Python version**: 3.11

6. Clique em "Deploy!"

### 6. Solução de problemas comuns

Se você vir o erro: `ModuleNotFoundError: No module named 'components'`:

1. Verifique se a pasta `components` contém um arquivo `__init__.py`
2. Verifique a estrutura de pastas no GitHub
3. Certifique-se de que o arquivo principal (app.py) esteja na raiz do repositório

Se o erro persistir, você pode tentar mudar os imports para relativos:

```python
# Em vez de
from components.auth import display_login

# Use
from .components.auth import display_login
```

### 7. Dados persistentes

O Streamlit Cloud não mantém dados entre atualizações. Para persistência de dados você precisará:

1. Conectar com um banco de dados externo, ou
2. Usar serviços de armazenamento como S3

Para seu caso, sugerimos a princípio manter data.json e users.json no repositório, e depois migrar para uma solução de banco de dados mais robusta quando necessário.