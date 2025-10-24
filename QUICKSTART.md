# 🚀 PlannerX - Rýchly štart

Tento súbor vás prevedie základným nastavením a spustením PlannerX za 5 minút.

## ⚡ Rýchle spustenie (5 minút)

### 1. Klonujte/Skopírujte projekt
```powershell
cd C:\Users\Admin\Ultraprogram\plannerx
```

### 2. Vytvorte virtuálne prostredie
```powershell
python -m venv venv
.\venv\Scripts\activate
```

### 3. Nainštalujte závislosti
```powershell
pip install -r requirements.txt
```

### 4. Vytvorte .env súbor
```powershell
copy .env.example .env
```

Upravte `.env` - minimum potrebné:
```env
SECRET_KEY=my-secret-key-123
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
```

### 5. Inicializujte databázu a demo dáta
```powershell
python scripts\seed_dev.py
```

### 6. Spustite aplikáciu
```powershell
python wsgi.py
```

Otvoriť v prehliadači: **http://localhost:5000**

## 🔑 Prihlásenie (Development)

V development móde použite test token:
```
Authorization: Bearer dev_demo_user:demo@plannerx.local
```

## 📧 Testovanie digestu

```powershell
python scripts\run_digest.py
```

## 🎯 Ďalšie kroky

1. **Konfigurovať Firebase** - Viď hlavné README.md
2. **Nastaviť SMTP** - Pre produkčné emaily
3. **Nasadiť do produkcie** - Docker alebo PythonAnywhere

## 📚 Užitočné príkazy

```powershell
# Seed demo dáta
python scripts\seed_dev.py

# Test email
python scripts\send_test_email.py your@email.com

# Spustiť digest manuálne
python scripts\run_digest.py

# Spustiť testy
pytest

# Formátovať kód
black app/ tests/
```

## ⚠️ Troubleshooting

### Import chyby
```powershell
pip install -r requirements.txt
```

### Databáza neexistuje
```powershell
python wsgi.py  # Automaticky vytvorí tabuľky
```

### SMTP chyba
Skontrolujte `.env` - `SMTP_USER` a `SMTP_PASSWORD` musia byť nastavené.

---

Pre detailné informácie viď [README.md](README.md)
