# 🚀 PlannerX - Deployment Guide

Kompletný návod na nasadenie PlannerX do produkcie.

## 📋 Pred nasadením

### Checklist
- [ ] PostgreSQL databáza pripravená
- [ ] Firebase projekt vytvorený a nakonfigurovaný
- [ ] SMTP credentials (Gmail/Mailgun/SES)
- [ ] Domain a DNS nakonfigurované (voliteľné)
- [ ] SSL certifikát (Let's Encrypt alebo iný)
- [ ] Backupy nastavené

## 🐳 Option 1: Docker Deployment (Odporúčané)

### 1. Príprava

```bash
# Klonujte/nahrať projekt na server
cd /opt/plannerx

# Vytvorte .env z .env.example
cp .env.example .env
nano .env  # Upravte hodnoty
```

### 2. Konfigurácia .env (Production)

```env
FLASK_ENV=production
SECRET_KEY=<generate-strong-random-key>
DATABASE_URL=postgresql://plannerx:password@postgres:5432/plannerx

SMTP_HOST=smtp.mailgun.org
SMTP_PORT=587
SMTP_USER=postmaster@your-domain.com
SMTP_PASSWORD=your-mailgun-password
EMAIL_FROM=PlannerX <no-reply@your-domain.com>

FIREBASE_PROJECT_ID=your-project-id
  FIREBASE_API_KEY=your-firebase-api-key
FIREBASE_ALLOWED_ISSUER=https://securetoken.google.com/your-project-id

DIGEST_HOUR=7
DIGEST_MINUTE=0
TIMEZONE=Europe/Prague
```

### 3. Build a spustenie

```bash
# Build Docker image
docker build -f infra/docker/Dockerfile.api -t plannerx:latest .

# Alebo použite docker-compose (s PostgreSQL)
docker-compose up -d

# Skontrolujte logy
docker-compose logs -f app
```

### 4. Nginx Reverse Proxy (na hoste)

Vytvorte `/etc/nginx/sites-available/plannerx`:

```nginx
server {
    listen 80;
    server_name plannerx.yourdomain.com;

    location / {
        proxy_pass http://localhost:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

Aktivujte:
```bash
sudo ln -s /etc/nginx/sites-available/plannerx /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

### 5. SSL s Let's Encrypt

```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d plannerx.yourdomain.com
```

## 🖥️ Option 2: VPS/Dedicated Server (Systemd)

### 1. Príprava servera

```bash
# Update systému
sudo apt update && sudo apt upgrade -y

# Inštalácia závislostí
sudo apt install python3.11 python3.11-venv python3-pip postgresql nginx -y
```

### 2. PostgreSQL setup

```bash
sudo -u postgres psql

# V PostgreSQL konzole:
CREATE DATABASE plannerx;
CREATE USER plannerx WITH PASSWORD 'strong_password';
GRANT ALL PRIVILEGES ON DATABASE plannerx TO plannerx;
\q
```

### 3. Aplikácia setup

```bash
# Vytvoriť užívateľa
sudo useradd -m -s /bin/bash plannerx

# Nahrať projekt
sudo mkdir -p /opt/plannerx
sudo chown plannerx:plannerx /opt/plannerx
cd /opt/plannerx

# Ako plannerx user:
sudo -u plannerx bash
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Konfigurácia
cp .env.example .env
nano .env  # Upravte DATABASE_URL na PostgreSQL
```

### 4. Database migrácie

```bash
source venv/bin/activate
alembic upgrade head
```

### 5. Systemd service

Vytvorte `/etc/systemd/system/plannerx.service`:

```ini
[Unit]
Description=PlannerX Application
After=network.target postgresql.service

[Service]
Type=notify
User=plannerx
Group=plannerx
WorkingDirectory=/opt/plannerx
Environment="PATH=/opt/plannerx/venv/bin"
ExecStart=/opt/plannerx/venv/bin/gunicorn -c infra/gunicorn.conf.py wsgi:app
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Aktivácia:
```bash
sudo systemctl daemon-reload
sudo systemctl enable plannerx
sudo systemctl start plannerx
sudo systemctl status plannerx
```

### 6. Nginx (rovnako ako v Docker)

Použite konfiguráciu z Docker sekcie.

## ☁️ Option 3: PythonAnywhere (Free Tier)

### 1. Upload projektu

- Prejdite na PythonAnywhere.com
- Vytvorte account (Free tier)
- V **Files** nahrajte projekt (ZIP a rozbaľte)

### 2. Virtuálne prostredie

V **Consoles** → Bash:
```bash
cd ~/plannerx
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 3. Web App konfigurácia

- V **Web** tab vytvorte novú web app
- Vyberte "Manual configuration" → Python 3.11
- Nastavte:
  - **Source code:** `/home/yourusername/plannerx`
  - **Working directory:** `/home/yourusername/plannerx`
  - **Virtualenv:** `/home/yourusername/plannerx/venv`

### 4. WSGI config

V **Web** tab upravte WSGI configuration file:

```python
import sys
import os

project_home = '/home/yourusername/plannerx'
if project_home not in sys.path:
    sys.path.insert(0, project_home)

# Load .env
from dotenv import load_dotenv
load_dotenv(os.path.join(project_home, '.env'))

from wsgi import app as application
```

### 5. Environment variables

V **Files** vytvorte `.env`:
```env
FLASK_ENV=production
SECRET_KEY=your-secret
DATABASE_URL=sqlite:///data/db.sqlite3
# ... (zvyšok konfigurácie)
```

### 6. Scheduled tasks

V **Tasks** tab pridajte:
```
07:00 UTC - cd /home/yourusername/plannerx && /home/yourusername/plannerx/venv/bin/python scripts/run_digest.py
```

### 7. Reload

Kliknite na **Reload** v Web tab.

## 🔐 Bezpečnostné odporúčania

### 1. Silné heslá
```bash
# Vygenerovať SECRET_KEY
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

### 2. Firewall
```bash
# UFW (Ubuntu)
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable
```

### 3. PostgreSQL
- Zmeňte default heslo
- Povoľte iba lokálne pripojenia (ak možné)
- Pravidelné backupy

### 4. SSL/TLS
- Vždy používajte HTTPS v produkcii
- Let's Encrypt = zadarmo

### 5. Environment variables
- Nikdy necommitujte `.env` do gitu
- Používajte silné heslá
- Rotujte secrets pravidelne

## 📊 Monitoring a Logging

### 1. Logy

```bash
# Systemd logs
sudo journalctl -u plannerx -f

# Docker logs
docker-compose logs -f app

# Nginx logs
tail -f /var/log/nginx/access.log
tail -f /var/log/nginx/error.log
```

### 2. Health check

```bash
curl https://plannerx.yourdomain.com/health
```

Odpoveď:
```json
{
  "status": "healthy",
  "service": "PlannerX",
  "version": "1.0.0"
}
```

### 3. Monitoring (voliteľné)

- **Sentry:** Error tracking
- **Prometheus + Grafana:** Metriky
- **Uptime Robot:** Uptime monitoring

## 🔄 Update aplikácie

### Docker
```bash
cd /opt/plannerx
git pull  # alebo nahrajte nový kód
docker-compose down
docker-compose build
docker-compose up -d
```

### Systemd
```bash
cd /opt/plannerx
git pull
source venv/bin/activate
pip install -r requirements.txt
alembic upgrade head
sudo systemctl restart plannerx
```

## 💾 Backupy

### PostgreSQL backup
```bash
# Manuálny backup
pg_dump -U plannerx plannerx > backup_$(date +%Y%m%d).sql

# Automatický backup (cron)
0 2 * * * pg_dump -U plannerx plannerx > /backups/plannerx_$(date +\%Y\%m\%d).sql
```

### SQLite backup
```bash
cp data/db.sqlite3 backups/db_$(date +%Y%m%d).sqlite3
```

## 🆘 Troubleshooting

### Aplikácia sa nespustí
```bash
# Skontrolujte logy
sudo journalctl -u plannerx -n 50

# Skontrolujte syntax
cd /opt/plannerx
source venv/bin/activate
python -m flask --app wsgi.py check
```

### Database connection error
- Skontrolujte DATABASE_URL v .env
- Overte, že PostgreSQL beží: `sudo systemctl status postgresql`
- Skúste pripojiť sa manuálne: `psql -U plannerx -d plannerx`

### APScheduler nefunguje
- V PythonAnywhere použite **Scheduled tasks** namiesto APScheduler
- Skontrolujte timezone v .env

### Email sa neposiela
```bash
# Test SMTP
python scripts/send_test_email.py your@email.com
```

## 📞 Podpora

- **Dokumentácia:** README.md
- **Issues:** GitHub Issues
- **Email:** support@plannerx.local

---

**Úspešné nasadenie! 🎉**
