# Instruções para Criar Executável Independente

Este guia explica como criar um executável independente do JGR Broker Importação que não requer instalação do Python ou de outras dependências.

## Pré-requisitos

1. Visual Studio Build Tools (para compilar as dependências)
   - Baixe em: [https://visualstudio.microsoft.com/pt-br/visual-cpp-build-tools/](https://visualstudio.microsoft.com/pt-br/visual-cpp-build-tools/)
   - Durante a instalação, selecione "Desenvolvimento para Desktop com C++"

2. Python já instalado (versão 3.8 ou superior)

## Passos para Criar o Executável

### Passo 1: Instalar o PyInstaller e dependências

Abra o PowerShell como administrador e navegue até a pasta do projeto:
```
cd "C:\Users\JOSY RIBEIRO\Downloads\JGRFUP"
```

Instale o PyInstaller:
```
pip install pyinstaller
```

Instale as dependências necessárias:
```
pip install streamlit pandas openpyxl xlsxwriter
```

### Passo 2: Usar o script de criação automática

Execute o script `create_exe.py` que preparamos:
```
python create_exe.py
```

Este script vai:
1. Criar o arquivo de especificação necessário
2. Gerar um ícone simples (se não existir)
3. Executar o PyInstaller
4. Criar um arquivo .bat para iniciar facilmente o executável

### Passo 3: Testando o executável

Após a conclusão, você encontrará:
- O executável na pasta `dist/JGRBrokerImportacao/`
- Um arquivo `iniciar_executavel.bat` na pasta principal

Para testar, dê um duplo clique no arquivo `iniciar_executavel.bat`.

## Distribuindo o Executável

Para compartilhar o programa com outros usuários:

1. Copie toda a pasta `dist/JGRBrokerImportacao/` para um pen drive ou compartilhe via nuvem
2. O usuário final só precisa executar o arquivo `JGRBrokerImportacao.exe` dentro desta pasta
3. Não é necessário instalar Python ou qualquer outra dependência

## Resolução de Problemas

Se encontrar erros durante a criação do executável:

1. **Erro de compilação do NumPy/Pandas**: Certifique-se de que o Visual Studio Build Tools está instalado corretamente
2. **Erro "module not found"**: Verifique se todas as dependências foram instaladas
3. **Arquivo executável não inicia**: Certifique-se de que todos os arquivos da pasta `dist/JGRBrokerImportacao/` estão presentes

Se preferir não lidar com a criação do executável, considere usar a opção Anaconda mencionada no arquivo `solucao_instalacao_windows.md`.