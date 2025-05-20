# Guia de Deploy na Hostinger (Docker)

Este guia apresenta os passos detalhados para realizar o deploy da aplicação JGR Broker Import na Hostinger utilizando Docker.

## Pré-requisitos

- Hospedagem na Hostinger com suporte a Docker
- Arquivos da aplicação preparados conforme `preparar_para_deploy.md`
- Acesso SSH à sua hospedagem (recomendado)

## Passo 1: Criar um novo site na Hostinger

1. Faça login no painel de controle da Hostinger
2. Vá para a seção "Websites" ou "Hospedagem"
3. Clique em "Criar Website" ou opção similar
4. Escolha **Docker** como ambiente de servidor (importante!)
5. Complete a configuração conforme solicitado

## Passo 2: Criar o Dockerfile

Crie um arquivo chamado `Dockerfile` com o seguinte conteúdo e inclua-o na pasta de deploy:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8501

CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

## Passo 3: Criar o docker-compose.yml

Crie um arquivo chamado `docker-compose.yml` com o seguinte conteúdo e inclua-o na pasta de deploy:

```yaml
version: '3'

services:
  streamlit-app:
    build: .
    ports:
      - "8501:8501"
    volumes:
      - ./data.json:/app/data.json
      - ./users.json:/app/users.json
    restart: always
```

## Passo 4: Upload dos arquivos

### Opção 1: Através do painel da Hostinger (File Manager)

1. No painel da Hostinger, vá para "File Manager" ou "Gerenciador de Arquivos"
2. Navegue até a pasta raiz do seu site (geralmente `/public_html` ou similar)
3. Faça upload da pasta compactada com os arquivos da aplicação
4. Extraia o arquivo ZIP diretamente no servidor

### Opção 2: Usando SSH e Git (Recomendado)

1. Conecte-se ao seu servidor via SSH
   ```
   ssh seu_usuario@seu_servidor.hostinger.com
   ```

2. Navegue até a pasta raiz do seu site
   ```
   cd /public_html
   ```

3. Clone seu repositório (se estiver usando Git)
   ```
   git clone https://seu-repositorio/jgr-broker.git .
   ```
   
   Ou faça upload via SCP/SFTP
   ```
   scp -r ./deploy_jgr/* seu_usuario@seu_servidor.hostinger.com:/public_html/
   ```

## Passo 5: Construir e iniciar o contêiner Docker

Através do SSH, execute os seguintes comandos na pasta raiz do seu site:

```bash
docker-compose build
docker-compose up -d
```

O parâmetro `-d` executa o contêiner em segundo plano.

## Passo 6: Configurar o proxy para acessar a aplicação

Se você quiser que a aplicação esteja disponível diretamente no domínio principal, configure o servidor web (geralmente Nginx) para fazer proxy das requisições para o contêiner Docker.

Crie um arquivo de configuração Nginx em `/etc/nginx/sites-available/seu_dominio.conf`:

```nginx
server {
    listen 80;
    server_name seu_dominio.com www.seu_dominio.com;

    location / {
        proxy_pass http://localhost:8501;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

Ative a configuração e reinicie o Nginx:

```bash
sudo ln -s /etc/nginx/sites-available/seu_dominio.conf /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

## Passo 7: Verificar a aplicação

Acesse seu site pelo navegador em `http://seu_dominio.com` e verifique se a aplicação está funcionando corretamente.

## Comandos úteis para gerenciar a aplicação

- Verificar logs da aplicação:
  ```
  docker-compose logs -f
  ```

- Reiniciar a aplicação:
  ```
  docker-compose restart
  ```

- Parar a aplicação:
  ```
  docker-compose down
  ```

- Atualizar a aplicação (após alterações):
  ```
  docker-compose build
  docker-compose up -d
  ```

## Solução de problemas

### A aplicação não inicia

Verifique os logs do contêiner:
```
docker-compose logs
```

### Erro de permissão nos arquivos de dados

Execute o seguinte comando para ajustar as permissões:
```
chmod 666 data.json users.json
```

### Problemas com o proxy Nginx

Verifique os logs do Nginx:
```
sudo tail -f /var/log/nginx/error.log
```

## Observações Importantes

- Mantenha backups regulares dos arquivos `data.json` e `users.json` para evitar perda de dados
- Considere configurar HTTPS usando Let's Encrypt para maior segurança
- Para atualizações futuras, você pode simplesmente substituir os arquivos alterados e reiniciar o contêiner

## Alternativas de Deploy

Se o deploy com Docker apresentar problemas, considere:

1. **Streamlit Cloud**: Plataforma especializada em hospedagem de aplicações Streamlit
2. **Render**: Serviço de hospedagem que suporta aplicações Python/Streamlit
3. **Heroku**: Plataforma que oferece deploys simplificados para aplicações Python

Para obter mais informações sobre essas alternativas, consulte a documentação oficial do Streamlit: https://docs.streamlit.io/knowledge-base/deploy