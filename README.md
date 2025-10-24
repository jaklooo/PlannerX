# 📅 PlannerX

**PlannerX** je plnohodnotná webová aplikácia na plánovanie úloh a udalostí s automatickým denným emailovým digestom. Aplikácia podporuje používateľské účty cez Firebase Auth, striktne oddelené dáta používateľov a plánovaný job, ktorý každé ráno o 07:00 (Europe/Prague) odošle prehľadný email.

## ✨ Funkcie

- **🔐 Autentifikácia:** Firebase Authentication s verifikáciou ID tokenu na backende
- **📋 Úlohy (Tasks):** CRUD operácie, priority (LOW/MED/HIGH), stavy (TODO/DOING/DONE), projekty
- **📅 Udalosti (Events):** Kalendár s podporou opakovania (NONE/DAILY/WEEKLY/MONTHLY)
- **👥 Kontakty:** Sledovanie narodenín a menín
- **📧 Denný digest:** Automatický email každé ráno s prehľadom dňa
- **📰 RSS správy:** Integrácia správ z vybraných zdrojov
- **💬 SMS notifikácie:** Voliteľné cez Twilio (môže byť vypnuté)
- **🌍 Časové pásmo:** Europe/Prague
- **🔒 Bezpečnosť:** Striktne oddelené dáta používateľov, CSRF ochrana

## 🏗️ Architektúra

### Tech Stack

- **Backend:** Python 3.11+, Flask, SQLAlchemy, Alembic
- **Databáza:** SQLite (development), PostgreSQL (production)
- **Auth:** Firebase Authentication
- **Scheduler:** APScheduler
- **Email:** SMTP (Gmail/Mailgun/SES kompatibilné)
- **RSS:** feedparser
- **Frontend:** Jinja2 templates, vanilla CSS/JS
- **Quality:** black, ruff, pytest, mypy

### Štruktúra projektu

```
plannerx/
├── app/                    # Hlavná aplikácia
│   ├── auth/              # Firebase autentifikácia
│   ├── models/            # SQLAlchemy modely
│   ├── routes/            # Flask blueprinty
│   ├── services/          # Business logika
│   ├── tasks/             # APScheduler joby
│   ├── templates/         # Jinja2 šablóny
│   └── static/            # CSS, JS
├── data/                   # Dáta (DB, RSS feeds, meniny)
├── scripts/               # Utility skripty
├── tests/                 # Pytest testy
├── infra/                 # Docker, Gunicorn, Nginx
└── migrations/            # Alembic migrácie
```

## 🚀 Rýchle spustenie (Development)

### 1. Predpoklady

- Python 3.11 alebo vyšší
- pip a virtuálne prostredie (venv)
- (Voliteľne) PostgreSQL pre produkčné nasadenie

### 2. Inštalácia

```powershell
# Vytvoriť virtuálne prostredie
python -m venv venv

# Aktivovať
.\venv\Scripts\activate

# Nainštalovať závislosti
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Skopírovať a upraviť .env
copy .env.example .env
# Upraviť .env s vlastnými hodnotami
```

### 3. Konfigurácia .env

Upravte `.env` súbor:

```env
# Flask
FLASK_ENV=development
SECRET_KEY=your-secret-key-here

# Database (SQLite pre dev)
DATABASE_URL=sqlite:///data/db.sqlite3

# Email (Gmail príklad)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_STARTTLS=true
SMTP_USER=vasa-email@gmail.com
SMTP_PASSWORD=vase-app-heslo
EMAIL_FROM=PlannerX <no-reply@plannerx.local>

# Firebase (získajte z Firebase Console)
FIREBASE_PROJECT_ID=your-project-id
FIREBASE_API_KEY=your-api-key
FIREBASE_ALLOWED_ISSUER=https://securetoken.google.com/your-project-id

# Scheduler
DIGEST_HOUR=7
DIGEST_MINUTE=0
TIMEZONE=Europe/Prague
```

### 4. Inicializácia databázy

```powershell
# Vytvoriť tabuľky
python wsgi.py

# Naplniť demo dátami
python scripts\seed_dev.py
```

### 5. Spustenie aplikácie

```powershell
# Spustiť development server
python -m flask run --reload

# Alebo cez Makefile (vyžaduje make)
make dev
```

Aplikácia beží na: `http://localhost:5000`

## 🔧 Konfigurácia Firebase Authentication

### 1. Vytvorenie Firebase projektu

1. Prejdite na [Firebase Console](https://console.firebase.google.com/)
2. Vytvorte nový projekt
3. V **Authentication** povoľte Email/Password provider

### 2. Získanie Firebase credentials

1. V **Project Settings** → **General** nájdite:
   - **Project ID** (napr. `my-plannerx-app`)
   - **Web API Key** (napr. `AIza...`)

2. Nastavte v `.env`:
   ```env
   FIREBASE_PROJECT_ID=my-plannerx-app
   FIREBASE_API_KEY=AIza...
   FIREBASE_ALLOWED_ISSUER=https://securetoken.google.com/my-plannerx-app
   ```

### 3. Development mode (bez Firebase)

Pre lokálny vývoj môžete použiť dev tokeny:

```
Authorization: Bearer dev_userid:user@example.com
```

Backend automaticky akceptuje tokeny vo formáte `dev_*` v development móde.

## 📧 Konfigurácia SMTP (Email)

### Gmail (s App Password)

1. Povoľte 2-faktorovú autentifikáciu v Google účte
2. Vygenerujte App Password: https://myaccount.google.com/apppasswords
3. Nastavte v `.env`:
   ```env
   SMTP_HOST=smtp.gmail.com
   SMTP_PORT=587
   SMTP_STARTTLS=true
   SMTP_USER=your-email@gmail.com
   SMTP_PASSWORD=your-16-char-app-password
   ```

### Mailgun

```env
SMTP_HOST=smtp.mailgun.org
SMTP_PORT=587
SMTP_USER=postmaster@your-domain.mailgun.org
SMTP_PASSWORD=your-mailgun-password
```

### Testovanie emailu

```powershell
python scripts\send_test_email.py your@email.com
```

## ⏰ APScheduler a denný digest

### Automatické spustenie

Digest job sa automaticky spustí pri štarte aplikácie a beží každý deň o čase nastavenom v `.env`:

```env
DIGEST_HOUR=7
DIGEST_MINUTE=0
TIMEZONE=Europe/Prague
```

### Manuálne spustenie (testovanie)

```powershell
python scripts\run_digest.py
```

### Zmena času odoslania

1. Upravte `DIGEST_HOUR` a `DIGEST_MINUTE` v `.env`
2. Reštartujte aplikáciu

### Vypnutie pre konkrétneho používateľa

Používateľ môže vypnúť digest v nastaveniach (`/settings`).

## 🧪 Testovanie

```powershell
# Spustiť všetky testy
pytest

# S pokrytím
pytest --cov=app --cov-report=html

# Konkrétny test
pytest tests/test_tasks.py -v

# Cez Makefile
make test
```

## 🐳 Docker deployment

### Build a spustenie

```powershell
# Build image
docker build -f infra/docker/Dockerfile.api -t plannerx:latest .

# Spustiť container
docker run -d -p 5000:5000 --env-file .env plannerx:latest
```

### Docker Compose (s PostgreSQL)

```powershell
# Štart všetkých služieb
docker-compose up -d

# Zastavenie
docker-compose down
```

`docker-compose.yml` obsahuje:
- **postgres:** PostgreSQL 15
- **app:** PlannerX aplikácia

## 🗄️ Migrácia na PostgreSQL

### 1. Inštalácia PostgreSQL

```powershell
# Windows: Stiahnite z postgresql.org
# Alebo použite Docker Compose (viď vyššie)
```

### 2. Vytvorenie databázy

```sql
CREATE DATABASE plannerx;
CREATE USER plannerx WITH PASSWORD 'strong_password';
GRANT ALL PRIVILEGES ON DATABASE plannerx TO plannerx;
```

### 3. Aktualizácia .env

```env
DATABASE_URL=postgresql://plannerx:strong_password@localhost:5432/plannerx
```

### 4. Migrácia dát

```powershell
# Inicializácia Alembic (ak ešte nie je)
alembic init migrations

# Vytvorenie migrácie
alembic revision --autogenerate -m "Initial migration"

# Aplikovanie migrácií
alembic upgrade head

# Alebo cez Makefile
make migrate
```

## 🚀 Production Deployment

### Gunicorn (odporúčané)

```powershell
# Inštalácia
pip install gunicorn

# Spustenie
gunicorn -c infra/gunicorn.conf.py wsgi:app

# Alebo
make prod
```

### Nginx (reverse proxy)

Príklad konfigurácie v `infra/nginx/nginx.conf`:

```nginx
server {
    listen 80;
    server_name plannerx.yourdomain.com;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
```

### Systemd service

Vytvorte `/etc/systemd/system/plannerx.service`:

```ini
[Unit]
Description=PlannerX Application
After=network.target

[Service]
User=www-data
WorkingDirectory=/opt/plannerx
Environment="PATH=/opt/plannerx/venv/bin"
ExecStart=/opt/plannerx/venv/bin/gunicorn -c infra/gunicorn.conf.py wsgi:app
Restart=always

[Install]
WantedBy=multi-user.target
```

Aktivácia:
```bash
sudo systemctl enable plannerx
sudo systemctl start plannerx
```

### PythonAnywhere

1. Upload projektu cez Files
2. Vytvorte virtuálne prostredie
3. Nastavte web app s WSGI config:
   ```python
   import sys
   sys.path.insert(0, '/home/yourusername/plannerx')
   
   from wsgi import app as application
   ```
4. Nastavte environment variables v `.env`

## 📊 Používanie

### API Endpointy

Všetky API endpointy vyžadujú `Authorization: Bearer <token>` hlavičku.

#### Tasks
- `GET /tasks/` - Zoznam úloh
- `POST /tasks/create` - Vytvoriť úlohu
- `GET /tasks/<id>` - Detail úlohy
- `PUT /tasks/<id>` - Aktualizovať úlohu
- `DELETE /tasks/<id>` - Zmazať úlohu
- `POST /tasks/<id>/snooze` - Odložiť úlohu o 1 deň

#### Events
- `GET /events/` - Zoznam udalostí
- `POST /events/create` - Vytvoriť udalosť
- `PUT /events/<id>` - Aktualizovať udalosť
- `DELETE /events/<id>` - Zmazať udalosť

#### Contacts
- `GET /contacts/` - Zoznam kontaktov
- `POST /contacts/create` - Vytvoriť kontakt
- `PUT /contacts/<id>` - Aktualizovať kontakt
- `DELETE /contacts/<id>` - Zmazať kontakt

#### Settings
- `GET /settings/` - Nastavenia používateľa
- `POST /settings/update` - Aktualizovať nastavenia

### Filtrovanie úloh

```
/tasks/?filter=today       # Dnešné úlohy
/tasks/?filter=week        # Tento týždeň
/tasks/?filter=overdue     # Po termíne
```

## 🛠️ Development

### Code formatting

```powershell
# Format code
make fmt

# Alebo manuálne
black app/ tests/ scripts/
ruff check --fix app/
```

### Linting

```powershell
# Lint check
make lint

# Alebo manuálne
ruff check app/
mypy app/ --ignore-missing-imports
```

### Vytvorenie migrácie

```powershell
# Automatická detekcia zmien v modeloch
alembic revision --autogenerate -m "Add new field"

# Aplikovanie
alembic upgrade head
```

## 🎨 Prispôsobenie

### RSS feeds

Upravte `data/rss_feeds.yaml`:

```yaml
feeds:
  - name: Váš zdroj
    url: https://your-source.com/rss
```

### Meniny

Upravte `data/name_days.sk.json`:

```json
{
  "01-01": ["Nový rok"],
  "12-25": ["Vianoce"]
}
```

### Email šablóna

Upravte `app/templates/emails/daily_digest.html`

## 📝 Licencia

MIT License - viď [LICENSE](LICENSE)

## 🤝 Podpora

Pre otázky a problémy vytvorte issue v GitHub repozitári.

## 🔒 Bezpečnosť

- Všetky API endpointy sú chránené Firebase Auth
- CSRF ochrana pre HTML formuláre
- SQL injection prevencia cez SQLAlchemy
- XSS ochrana cez Jinja2 autoescaping
- Striktne oddelené dáta používateľov (user_id filter)

## 📚 Ďalšie zdroje

- [Flask dokumentácia](https://flask.palletsprojects.com/)
- [Firebase Auth](https://firebase.google.com/docs/auth)
- [SQLAlchemy](https://www.sqlalchemy.org/)
- [APScheduler](https://apscheduler.readthedocs.io/)

---

**Vytvorené s ❤️ pre efektívne plánovanie**
