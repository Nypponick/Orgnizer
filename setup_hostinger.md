# Guia de Instalação para Hostinger Cloud

Este guia explica como instalar e executar o Sistema de Acompanhamento de Importação da JGR Broker em um servidor Hostinger Cloud.

## Pré-requisitos

- Acesso SSH ao seu servidor Hostinger
- Python 3.9+ instalado (ou permissão para instalá-lo)
- Habilidade para executar processos em segundo plano

## Passo 1: Conectar ao servidor via SSH

Use seu cliente SSH preferido para se conectar ao servidor Hostinger:

```bash
ssh seu_usuario@seu_servidor.hostinger.com
```

## Passo 2: Instalar Python e dependências (se necessário)

Verifique a versão do Python:

```bash
python3 --version
```

Se o Python não estiver instalado ou for uma versão antiga, instale-o:

```bash
sudo apt-get update
sudo apt-get install python3 python3-pip python3-venv
```

## Passo 3: Criar diretório para o aplicativo

```bash
mkdir -p ~/jgr_importacao
cd ~/jgr_importacao
```

## Passo 4: Configurar ambiente virtual Python

```bash
python3 -m venv venv
source venv/bin/activate
```

## Passo 5: Copiar arquivos do aplicativo

Faça upload de todos os arquivos do aplicativo para o diretório criado. Você pode usar SCP, SFTP ou o gerenciador de arquivos da Hostinger para isso.

## Passo 6: Instalar dependências do aplicativo

```bash
# Crie um arquivo requirements.txt com o seguinte conteúdo:
cat > requirements.txt << EOL
streamlit==1.31.0
pandas==2.1.4
twilio==8.13.0
xlsxwriter==3.1.9
EOL

# Instale as dependências
pip install -r requirements.txt
```

## Passo 7: Configurar o aplicativo para iniciar automaticamente

### Usando Supervisor (recomendado)

Instale o Supervisor:

```bash
sudo apt-get install supervisor
```

Crie um arquivo de configuração para o aplicativo:

```bash
sudo nano /etc/supervisor/conf.d/jgr_importacao.conf
```

Adicione o seguinte conteúdo:

```ini
[program:jgr_importacao]
command=/home/seu_usuario/jgr_importacao/venv/bin/streamlit run /home/seu_usuario/jgr_importacao/app.py --server.port 8501 --server.address 0.0.0.0
directory=/home/seu_usuario/jgr_importacao
user=seu_usuario
autostart=true
autorestart=true
stopasgroup=true
killasgroup=true
stderr_logfile=/home/seu_usuario/jgr_importacao/logs/err.log
stdout_logfile=/home/seu_usuario/jgr_importacao/logs/out.log
```

Crie a pasta de logs:

```bash
mkdir -p ~/jgr_importacao/logs
```

Recarregue o Supervisor e inicie o aplicativo:

```bash
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start jgr_importacao
```

## Passo 8: Configurar Nginx como proxy reverso

Instale o Nginx:

```bash
sudo apt-get install nginx
```

Crie um arquivo de configuração para o site:

```bash
sudo nano /etc/nginx/sites-available/jgr_importacao
```

Adicione o seguinte conteúdo:

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
        proxy_cache_bypass $http_upgrade;
    }
}
```

Ative o site e reinicie o Nginx:

```bash
sudo ln -s /etc/nginx/sites-available/jgr_importacao /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

## Passo 9: Configurar HTTPS com Let's Encrypt (recomendado)

Instale o Certbot:

```bash
sudo apt-get install certbot python3-certbot-nginx
```

Obtenha um certificado SSL:

```bash
sudo certbot --nginx -d seu_dominio.com -d www.seu_dominio.com
```

## Manutenção e Atualizações

Para atualizar o aplicativo:

1. Faça upload dos novos arquivos
2. Reinicie o aplicativo:

```bash
sudo supervisorctl restart jgr_importacao
```

## Solução de Problemas

Verifique os logs para diagnosticar problemas:

```bash
# Logs do aplicativo
cat ~/jgr_importacao/logs/err.log
cat ~/jgr_importacao/logs/out.log

# Logs do Nginx
sudo cat /var/log/nginx/error.log

# Status do supervisor
sudo supervisorctl status
```