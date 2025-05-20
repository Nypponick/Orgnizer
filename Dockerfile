FROM python:3.11-slim

WORKDIR /app

# Copiar apenas o arquivo de requisitos primeiro para aproveitar o cache do Docker
COPY required_packages.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copiar o resto dos arquivos da aplicação
COPY . .

# Garantir que os arquivos necessários estejam presentes
RUN ls -la /app/data.py  
RUN ls -la /app/components/

# Configurar PYTHONPATH para incluir diretório raiz
ENV PYTHONPATH="/app:${PYTHONPATH}"

# Expor a porta que o Streamlit usa
EXPOSE 8501

# Comando para iniciar a aplicação
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]