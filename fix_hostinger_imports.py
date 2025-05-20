"""
Script para corrigir problemas de importação de módulos na Hostinger.
Adicione este arquivo no diretório raiz da aplicação para garantir que os módulos locais sejam encontrados.
"""
import os
import sys
import inspect

# Obter o diretório do script atual
current_dir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))

# Adicionar o diretório atual ao path para que os módulos locais possam ser importados
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

# Imprimir informações de diagnóstico
print("="*50)
print("INICIANDO DIAGNÓSTICO DE IMPORTAÇÃO")
print("="*50)
print(f"Diretório atual: {current_dir}")
print(f"PYTHONPATH: {sys.path}")
print(f"Conteúdo do diretório atual: {os.listdir(current_dir)}")

# Verificar se data.py existe e pode ser importado
try:
    import data
    print(f"✓ Módulo data importado com sucesso: {data.__file__}")
except ImportError as e:
    print(f"✗ Erro ao importar o módulo data: {e}")
    # Tentar localizar o arquivo manualmente
    if os.path.exists(os.path.join(current_dir, 'data.py')):
        print(f"  O arquivo data.py existe no diretório atual, mas não pode ser importado.")
    else:
        print(f"  O arquivo data.py NÃO existe no diretório atual.")

# Verificar outros módulos importantes
try:
    import components
    print(f"✓ Módulo components importado com sucesso: {components.__file__}")
except ImportError as e:
    print(f"✗ Erro ao importar o módulo components: {e}")
    
try:
    import utils
    print(f"✓ Módulo utils importado com sucesso: {utils.__file__}")
except ImportError as e:
    print(f"✗ Erro ao importar o módulo utils: {e}")

print("="*50)
print("FIM DO DIAGNÓSTICO DE IMPORTAÇÃO")
print("="*50)