# 🚀 Deployment Checklist pre PlannerX

## 1️⃣ Firebase Setup (POVINNÉ pre production)

### Vytvor Firebase projekt:
1. Choď na [Firebase Console](https://console.firebase.google.com/)
2. Klikni "Add project" / "Vytvoriť projekt"
3. Zadaj názov: `plannerx-prod` (alebo iný)
4. Deaktivuj Google Analytics (nepovinné)

### Aktivuj Authentication:
1. V Firebase Console → **Authentication** → **Get Started**
2. Povoľ **Email/Password** provider
3. (Voliteľne) povoľ **Google Sign-In**

### Získaj credentials:
1. **Project ID**: 
   - Nájdeš v **Project Settings** → `plannerx-prod`
   
2. **API Key**:
   - **Project Settings** → **General** → **Web API Key**
   - Skopíruj hodnotu (napr. `AIzaSyC...`)

### Nastav v .env:
```bash
FIREBASE_PROJECT_ID=plannerx-prod
FIREBASE_API_KEY=AIzaSyC_your_actual_api_key_here
FIREBASE_ALLOWED_ISSUER=https://securetoken.google.com/plannerx-prod
```

---

## 2️⃣ SMTP Email Setup (pre denný digest)

### Option A: Gmail App Password (NAJJEDNODUCHŠIE)
1. Zapni 2FA na Gmail účte
2. Choď na https://myaccount.google.com/apppasswords
3. Vytvor "App password" pre "Mail"
4. Skopíruj 16-znakový kód (napr. `abcd efgh ijkl mnop`)

**V .env:**
```bash
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_STARTTLS=true
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=abcdefghijklmnop  # Bez medzier!
EMAIL_FROM=PlannerX <your-email@gmail.com>
```

### Option B: Mailgun (pre viac emailov)
1. Vytvor účet na [mailgun.com](https://mailgun.com) (free 5000 emailov/mesiac)
2. Pridaj doménu alebo použi sandbox
3. Získaj SMTP credentials z **Sending** → **Domain Settings**

**V .env:**
```bash
SMTP_HOST=smtp.mailgun.org
SMTP_PORT=587
SMTP_USER=postmaster@your-domain.mailgun.org
SMTP_PASSWORD=your-mailgun-smtp-password
EMAIL_FROM=PlannerX <no-reply@your-domain.com>
```

### Option C: SendGrid
Free tier 100 emailov/deň

---

## 3️⃣ Database Migration (SQLite → PostgreSQL)

### Pre Render.com / Railway:
Automaticky vytvoria PostgreSQL databázu a dajú ti `DATABASE_URL`.

**V .env nastav:**
```bash
DATABASE_URL=postgresql://user:password@host:5432/dbname
```

### Export dát zo SQLite (ak chceš preniesť demo dáta):
```bash
# Export do CSV
python scripts/export_import_csv.py export

# Import do PostgreSQL (po nastavení DATABASE_URL)
python scripts/export_import_csv.py import
```

---

## 4️⃣ Environment Variables pre Production

**Kompletný .env pre production:**

```bash
# Flask
FLASK_ENV=production
SECRET_KEY=your-super-secret-random-string-change-this-NOW-xyz123

# Database (PostgreSQL na Render/Railway)
DATABASE_URL=postgresql://user:password@hostname:5432/plannerx_db

# Firebase Authentication
FIREBASE_PROJECT_ID=plannerx-prod
FIREBASE_API_KEY=AIzaSyC_your_actual_api_key
FIREBASE_ALLOWED_ISSUER=https://securetoken.google.com/plannerx-prod

# Email (Gmail App Password)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_STARTTLS=true
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password-16chars
EMAIL_FROM=PlannerX <your-email@gmail.com>

# Scheduler (07:00 Europe/Prague)
DIGEST_HOUR=7
DIGEST_MINUTE=0
TIMEZONE=Europe/Prague

# SMS (voliteľné - Twilio)
# TWILIO_ACCOUNT_SID=
# TWILIO_AUTH_TOKEN=
# TWILIO_FROM_NUMBER=
```

**DÔLEŽITÉ:** Vygeneruj silný SECRET_KEY:
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

---

## 5️⃣ Deployment na Render.com (ODPORÚČAM)

### Krok 1: Push na GitHub
```bash
cd C:\Users\Admin\Ultraprogram\plannerx
git init
git add .
git commit -m "Initial commit - PlannerX production ready"

# Vytvor repo na github.com a potom:
git remote add origin https://github.com/yourusername/plannerx.git
git push -u origin main
```

### Krok 2: Vytvor PostgreSQL databázu
1. Prihlás sa na [render.com](https://render.com)
2. **New** → **PostgreSQL**
3. Názov: `plannerx-db`
4. Region: `Frankfurt` (EU)
5. Free tier: YES
6. Klikni **Create Database**
7. Skopíruj **Internal Database URL** (začína `postgresql://...`)

### Krok 3: Vytvor Web Service
1. **New** → **Web Service**
2. Pripoj GitHub repository `plannerx`
3. Nastavenia:
   - **Name**: `plannerx`
   - **Runtime**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn wsgi:app`
   - **Instance Type**: `Free`

### Krok 4: Nastav Environment Variables
V Render dashboarde → **Environment**:

```
FLASK_ENV=production
SECRET_KEY=<vygeneruj pomocou python -c "import secrets; print(secrets.token_urlsafe(32))">
DATABASE_URL=<skopíruj z PostgreSQL databázy Internal URL>
FIREBASE_PROJECT_ID=plannerx-prod
FIREBASE_API_KEY=AIza...
FIREBASE_ALLOWED_ISSUER=https://securetoken.google.com/plannerx-prod
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_STARTTLS=true
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
EMAIL_FROM=PlannerX <your-email@gmail.com>
DIGEST_HOUR=7
DIGEST_MINUTE=0
TIMEZONE=Europe/Prague
```

### Krok 5: Deploy!
1. Klikni **Create Web Service**
2. Render automaticky:
   - Nainštaluje dependencies
   - Spustí `gunicorn wsgi:app`
   - Vytvorí HTTPS URL: `https://plannerx.onrender.com`

### Krok 6: Inicializuj databázu
V Render dashboarde → **Shell**:
```bash
python -c "from app import create_app, db; app = create_app('production'); app.app_context().push(); db.create_all()"
```

---

## 6️⃣ Frontend Firebase Integration

Vytvor **Firebase Web App**:
1. Firebase Console → **Project Settings** → **Your apps**
2. Klikni **Web icon** (</>)
3. Názov: `PlannerX Web`
4. Skopíruj Firebase config

Aktualizuj `login.html` s Firebase SDK (môžem ti pomôcť po deplomente).

---

## 7️⃣ Testovanie Production

### Test 1: Health Check
```bash
curl https://plannerx.onrender.com/health
# Očakávaný output: {"status":"ok","version":"1.0.0"}
```

### Test 2: Login & Dashboard
1. Otvor `https://plannerx.onrender.com`
2. Klikni "Prihlásiť sa cez Firebase"
3. Registruj/prihlás sa cez Firebase Auth
4. Dashboard by sa mal načítať

### Test 3: Denný Digest
```bash
# V Render Shell:
python scripts/run_digest.py
# Skontroluj inbox - mal by prísť testovací email
```

---

## ⚠️ Dôležité Security poznámky

1. **NIKDY NEcommituj `.env` súbor do Gitu!** (už je v `.gitignore`)
2. **Zmeň SECRET_KEY** z "change-me-in-production"
3. **Firebase API Key** môže byť verejný (je to OK pre web apps)
4. **SMTP heslo** drž v tajnosti (použiť App Password, nie hlavné heslo)
5. **PostgreSQL URL** nikdy nezdieľaj

---

## 📊 Monitoring & Logs

### Render.com:
- **Logs**: Dashboard → **Logs** (real-time)
- **Metrics**: CPU, Memory usage
- **Alerts**: Nastav email notifikácie

### Check APScheduler:
Logs by mali obsahovať:
```
Scheduler started. Daily digest job scheduled for 07:00 Europe/Prague
```

---

## 🔄 CI/CD (Continuous Deployment)

Render automaticky redeploy pri každom push na GitHub `main` branch:

```bash
# Lokálne urob zmeny
git add .
git commit -m "Fix bug in tasks"
git push origin main

# Render automaticky:
# 1. Detekuje push
# 2. Rebuild aplikáciu
# 3. Redeploy (zero downtime)
```

---

## 💰 Náklady

### Free Tier (Render.com):
- ✅ PostgreSQL: 90 dní free, potom $7/mesiac
- ✅ Web Service: Free (with cold starts po 15 min neaktivity)
- ✅ HTTPS/SSL: Zadarmo

### Paid Tier ($7/mesiac):
- ✅ Žiadne cold starts
- ✅ 512MB RAM
- ✅ Persistentná databáza

---

## 🆘 Troubleshooting

### Problem: "Application failed to start"
**Fix:** Check Render logs → pravdepodobne chýba env variable

### Problem: "Database connection failed"
**Fix:** Skontroluj `DATABASE_URL` - musí byť **Internal Database URL** z Render PostgreSQL

### Problem: "Emails sa neodosielajú"
**Fix:** Test SMTP v Render Shell:
```bash
python scripts/send_test_email.py
```

### Problem: "Firebase auth nefunguje"
**Fix:** Skontroluj CORS - pridaj Render doménu do Firebase Authorized domains:
Firebase Console → **Authentication** → **Settings** → **Authorized domains**
Pridaj: `plannerx.onrender.com`

---

## ✅ Deployment Checklist Summary

- [ ] Firebase projekt vytvorený
- [ ] Firebase Authentication aktivovaný (Email/Password)
- [ ] Gmail App Password vytvorený
- [ ] SECRET_KEY vygenerovaný
- [ ] GitHub repo vytvorený a push-nutý
- [ ] Render.com PostgreSQL databáza vytvorená
- [ ] Render.com Web Service vytvorený
- [ ] Environment variables nastavené
- [ ] Databáza inicializovaná (`db.create_all()`)
- [ ] Health check funguje
- [ ] Login funguje
- [ ] Testovací digest odoslaný
- [ ] Firebase Authorized domains nastavené
- [ ] (Voliteľne) Custom doména pripojená

---

**Po dokončení deployment máš production-ready PlannerX! 🎉**

Potrebuješ pomoc s niektorým krokom? Daj vedieť!
