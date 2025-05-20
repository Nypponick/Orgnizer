# Instalação Local na Pasta ImportTrackerDashboard

Criei três arquivos para facilitar a instalação e execução do sistema na pasta `C:\Users\JOSY RIBEIRO\Downloads\JGRFUP\ImportTrackerDashboard`:

## 1. Instalação Fácil

Para instalar o sistema com todos os pacotes necessários:

1. Copie os seguintes arquivos para a pasta `ImportTrackerDashboard`:
   - `instalar_local.bat`
   - `iniciar_app_local.bat`
   - `required_packages.txt`
   - `instalar_sem_compilacao.bat`

2. Dê um duplo clique no arquivo `instalar_local.bat` ou `instalar_sem_compilacao.bat`
   - O arquivo `instalar_local.bat` tentará instalar normalmente
   - O arquivo `instalar_sem_compilacao.bat` instalará somente versões pré-compiladas

3. Aguarde a instalação ser concluída (isso pode demorar alguns minutos)

## 2. Iniciar o Aplicativo

Após a instalação concluída:

1. Dê um duplo clique no arquivo `iniciar_app_local.bat`
2. O sistema abrirá automaticamente no seu navegador padrão

## 3. Solução de Problemas

Se você encontrar problemas durante a instalação:

### Se ocorrer erro de compilação:
- Use o arquivo `instalar_sem_compilacao.bat` em vez do `instalar_local.bat`
- Este arquivo usa apenas pacotes pré-compilados e não tenta compilar nada

### Se acontecer erro "não é reconhecido como um comando interno":
- Verifique se o Python está instalado corretamente
- Você pode testar digitando `python --version` no Prompt de Comando

### Se a pasta "venv" for criada, mas as instalações falharem:
- Tente executar o arquivo .bat como administrador (clique com o botão direito -> "Executar como administrador")

## 4. Observações Importantes

- Estes arquivos criam um ambiente virtual Python dentro da pasta do projeto
- Isso significa que as dependências serão instaladas apenas nesta pasta, não afetando o restante do sistema
- Quando você executa o `iniciar_app_local.bat`, o sistema usa apenas as dependências desta pasta

Para mais informações ou em caso de problemas, consulte os outros guias de instalação:
- `solucao_instalacao_windows.md`
- `instrucoes_criar_executavel.md`