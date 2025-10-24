# 🔥 Firebase Setup pre PlannerX

Už máš vytvorený Firebase projekt: **plannerx-905b1** ✅

## 1️⃣ Aktivuj Firebase Authentication

1. Otvor [Firebase Console](https://console.firebase.google.com/)
2. Vyber projekt **plannerx-905b1**
3. V ľavom menu → **Build** → **Authentication**
4. Klikni **Get started**
5. V záložke **Sign-in method**:
   - Klikni **Email/Password**
   - Zapni **Enable**
   - Klikni **Save**

---

## 2️⃣ Získaj Web API Key

### Spôsob 1: Project Settings
1. Firebase Console → **⚙️ Project Settings** (koliesko vľavo hore)
2. V záložke **General**
3. Scroll nadol na **Your apps**
4. Ak nie je žiadna web app:
   - Klikni **</>** (Web icon)
   - Názov: `PlannerX Web`
   - Klikni **Register app**
5. Skopíruj hodnoty:

```javascript
// Ukážka Firebase config (tvoje hodnoty budú iné)
const firebaseConfig = {
  apiKey: "AIzaSyBXXXXXXXXXXXXXXXXXXXXXXXXXXXX",  // ← Toto potrebuješ!
  authDomain: "plannerx-905b1.firebaseapp.com",
  projectId: "plannerx-905b1",                    // ← Už máš
  storageBucket: "plannerx-905b1.firebasestorage.app",
  messagingSenderId: "123456789012",
  appId: "1:123456789012:web:abcdef123456"
};
```

### Spôsob 2: Zo Settings direktne
1. Firebase Console → **⚙️ Project Settings**
2. **General** tab
3. Sekcia **Your project** → **Web API Key**
4. Skopíruj hodnotu (začína `AIza...`)

---

## 3️⃣ Nastav Environment Variables

**Aktualizuj `.env` súbor:**

```bash
# Firebase Web Authentication
FIREBASE_PROJECT_ID=plannerx-905b1
FIREBASE_API_KEY=AIzaSyBXXXXXXXXXXXXXXXXXXXXXXXXXXXX  # ← Zmeň na tvoj API Key
FIREBASE_ALLOWED_ISSUER=https://securetoken.google.com/plannerx-905b1
```

**DÔLEŽITÉ:**
- ✅ `FIREBASE_PROJECT_ID`: `plannerx-905b1` (už máš správne)
- ✅ `FIREBASE_API_KEY`: Musíš skopírovať z Firebase Console (začína `AIza`)
- ✅ API Key **môže byť verejný** - je to bezpečné pre web apps

---

## 4️⃣ Aktualizuj login.html pre Firebase Auth

Po získaní API Key, aktualizuj `app/templates/login.html`:

### Pridaj Firebase SDK:

V `<head>` sekcii pridaj:
```html
<!-- Firebase SDK -->
<script src="https://www.gstatic.com/firebasejs/10.7.1/firebase-app-compat.js"></script>
<script src="https://www.gstatic.com/firebasejs/10.7.1/firebase-auth-compat.js"></script>
```

### Inicializuj Firebase:

V `<script>` sekcii pridaj:
```javascript
// Firebase konfigurácia
const firebaseConfig = {
  apiKey: "AIzaSyBXXXXXXXXXXXXXXXXXXXXXXXXXXXX",  // Tvoj API Key
  authDomain: "plannerx-905b1.firebaseapp.com",
  projectId: "plannerx-905b1",
};

// Inicializuj Firebase
firebase.initializeApp(firebaseConfig);
const auth = firebase.auth();
```

### Implementuj firebaseLogin():
```javascript
async function firebaseLogin() {
    try {
        // Email/Password prihlásenie
        const email = prompt('Email:');
        const password = prompt('Password:');
        
        if (!email || !password) return;
        
        // Prihlás sa
        const userCredential = await auth.signInWithEmailAndPassword(email, password);
        
        // Získaj ID token
        const idToken = await userCredential.user.getIdToken();
        
        // Ulož token
        localStorage.setItem('auth_token', idToken);
        
        showSuccess('✅ Prihlásenie úspešné!');
        
        // Presmeruj na dashboard
        setTimeout(() => {
            window.location.href = '/dashboard';
        }, 1000);
        
    } catch (error) {
        showError('Prihlásenie zlyhalo: ' + error.message);
    }
}
```

---

## 5️⃣ Vytvor test používateľa

### Spôsob 1: Cez Firebase Console (Odporúčam)
1. Firebase Console → **Authentication** → **Users**
2. Klikni **Add user**
3. Email: `test@plannerx.sk` (alebo tvoj)
4. Password: `Test123456`
5. Klikni **Add user**

### Spôsob 2: Cez registračný formulár
Vytvor registračný endpoint v aplikácii (môžem ti pomôcť).

---

## 6️⃣ Nastav Authorized Domains (Production)

Keď deployneš na Render/Railway:

1. Firebase Console → **Authentication** → **Settings**
2. **Authorized domains** tab
3. Klikni **Add domain**
4. Pridaj: `plannerx.onrender.com` (alebo tvoja doména)
5. Klikni **Add**

**Localhost** (`127.0.0.1`, `localhost`) sú už automaticky povolené.

---

## 7️⃣ Test Firebase Auth

### Lokálne testovanie:
1. Spusti server: `python wsgi.py`
2. Otvor: `http://127.0.0.1:5000/login`
3. Klikni **"Prihlásiť sa cez Firebase"**
4. Zadaj email a heslo test usera
5. Malo by ťa prihlásiť a presmerovať na dashboard

### Debug:
Otvor Browser DevTools (F12) → **Console** → sleduj chybové hlášky.

---

## 🔒 Firebase Admin SDK (Service Account)

Súbor `plannerx-905b1-firebase-adminsdk-fbsvc-eeb68669fa.json` je **Admin SDK key**.

### Kedy ho použiť:
- **Backend operácie** (vytvorenie usera cez API, overenie tokenov na backende)
- **Nie pre frontend!** (nikdy ho nedávaj do `login.html`)

### Ako ho použiť (voliteľné - pre pokročilé použitie):

1. **Nainštaluj Firebase Admin SDK:**
```bash
pip install firebase-admin
```

2. **V `app/auth/firebase.py` pridaj:**
```python
import firebase_admin
from firebase_admin import credentials, auth as firebase_auth

# Inicializuj Admin SDK (len raz pri štarte)
cred = credentials.Certificate("path/to/serviceAccountKey.json")
firebase_admin.initialize_app(cred)

# Overenie tokenu (bezpečnejšie ako manuálne parsing)
def verify_id_token_admin(id_token: str) -> dict:
    try:
        decoded_token = firebase_auth.verify_id_token(id_token)
        return {
            "uid": decoded_token["uid"],
            "email": decoded_token.get("email"),
            "email_verified": decoded_token.get("email_verified", False),
        }
    except Exception as e:
        raise ValueError(f"Invalid token: {e}")
```

**DÔLEŽITÉ:**
- ⚠️ **NIKDY NEcommituj service account JSON do Gitu!**
- ⚠️ Pridaj `*.json` do `.gitignore`
- ⚠️ Na Render/Railway nahraj ako **Secret File** (nie env variable)

---

## ✅ Checklist

- [ ] Firebase Authentication aktivovaný (Email/Password)
- [ ] Web API Key skopírovaný z Project Settings
- [ ] `.env` aktualizovaný s `FIREBASE_API_KEY`
- [ ] `login.html` aktualizovaný s Firebase SDK
- [ ] Test user vytvorený v Firebase Console
- [ ] Lokálne testovanie funguje
- [ ] (Production) Authorized domain pridaný
- [ ] Service account JSON **NIE** v Gite (v `.gitignore`)

---

Potrebuješ pomoc s niektorým krokom? 🔥
