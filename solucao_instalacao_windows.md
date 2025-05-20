# Solução para Instalação no Windows

Vejo que você está enfrentando alguns problemas para instalar as dependências. Vamos resolver isso com uma abordagem mais simples:

## Opção 1: Instalar pacotes pré-compilados (Recomendado)

Em vez de tentar compilar os pacotes do zero, vamos usar versões pré-compiladas:

1. Abra o PowerShell como administrador
2. Navegue até a pasta do projeto:
   ```
   cd "C:\Users\JOSY RIBEIRO\Downloads\JGRFUP"
   ```

3. Execute estes comandos um por um:
   ```
   pip install --upgrade pip
   pip install streamlit --no-cache-dir
   pip install pandas --no-cache-dir
   pip install openpyxl --no-cache-dir
   pip install xlsxwriter --no-cache-dir
   ```

4. Depois que todas as instalações estiverem concluídas, execute:
   ```
   streamlit run app.py
   ```

## Opção 2: Usar instalador de wheel pré-compilado

Se a Opção 1 não funcionar, você pode baixar arquivos wheel pré-compilados:

1. Baixe os arquivos wheel (.whl) para sua versão do Python em [https://www.lfd.uci.edu/~gohlke/pythonlibs/](https://www.lfd.uci.edu/~gohlke/pythonlibs/)
2. Você precisará baixar os arquivos .whl para:
   - numpy
   - pandas
   - streamlit (e suas dependências)

3. Instale cada arquivo wheel baixado usando:
   ```
   pip install caminho\para\arquivo.whl
   ```

## Opção 3: Usar Anaconda (mais simples)

Esta é provavelmente a maneira mais fácil:

1. Baixe e instale o Anaconda: [https://www.anaconda.com/download/](https://www.anaconda.com/download/)
2. Abra o Anaconda Prompt
3. Navegue até a pasta do projeto:
   ```
   cd "C:\Users\JOSY RIBEIRO\Downloads\JGRFUP"
   ```
4. Instale os pacotes necessários:
   ```
   conda install -c conda-forge streamlit pandas openpyxl xlsxwriter
   ```
5. Execute o aplicativo:
   ```
   streamlit run app.py
   ```

## Problema específico Visual Studio

O erro que você está vendo é porque alguns pacotes (como NumPy) precisam compilar código C++ durante a instalação, o que requer o Visual Studio Build Tools. Se quiser resolver isso diretamente:

1. Baixe o Visual Studio Build Tools: [https://visualstudio.microsoft.com/pt-br/visual-cpp-build-tools/](https://visualstudio.microsoft.com/pt-br/visual-cpp-build-tools/)
2. Durante a instalação, selecione "Desenvolvimento para desktop com C++"
3. Após a instalação, tente instalar os pacotes novamente

## Alternativa com executável Python

Como última alternativa, podemos criar um executável que já inclui o Python e todas as dependências. Isso elimina a necessidade de instalar qualquer coisa, mas requer mais trabalho para ser criado.