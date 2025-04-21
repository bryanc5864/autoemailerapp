# AutoEmailerApp

**AutoEmailerApp** is a Flask-based web application for sending bulk, personalized emails via CSV upload or manual entry. It features user registration, login, email queuing, randomized send intervals, send history tracking, and simple UI animations.

## 🔧 Features

- **User Auth**: register/login/logout with per-user in-memory storage
- **Recipient Queue**: import via CSV or add single entries
- **Bulk Send**: personalized greeting (`Hi {name},`) and random 60–120s delay between sends
- **History**: track successful sends per user
- **UI Animations**: paper-plane send effect; “unboxing” effect on queue-add

## ⚙️ Requirements

- Python 3.7+
- Flask
- `email`, `smtplib`, `csv`, `io`, `random`, `time` (built‑ins)

Install with:
```bash
pip install Flask
```

## 🚀 Installation & Setup

1. **Clone repository**
   ```bash
git clone git@github.com:bryanc5864/autoemailerapp.git
cd autoemailerapp
```
2. **(Optional) Create virtual env**
   ```bash
python -m venv venv
source venv/bin/activate  # macOS/Linux
venv\Scripts\activate     # Windows
```
3. **Install dependencies**
   ```bash
pip install -r requirements.txt
```
4. **Configure**
   - Open `app.py` (or your main script)
   - Set `app.secret_key` to a strong random value

## ▶️ Running the App

```bash
python app.py  # or `flask run` if FLASK_APP is set
oh_url: http://localhost:5000/
```

1. **Register** a new user (supply sender email/app password)
2. **Login**
3. **Add recipients** (CSV/manual)
4. **Compose message** & **Send Emails**
5. **View history** in _History_ tab

## 📁 Project Structure

```
├─ app.py
├─ requirements.txt
├─ templates/
│  ├─ base.html
│  ├─ index.html
│  ├─ login.html
│  ├─ login_success.html
│  ├─ register.html
│  └─ history.html
└─ static/  (optional: for custom CSS/JS)
```

## 🔒 Security Notes

- **In-memory DB**: not persistent; switch to real DB (SQLite/Postgres) for production
- **Passwords**: currently stored plaintext; implement hashing (e.g., `bcrypt`)
- **Email creds**: store securely (env vars or vault), avoid hard‑coding

## 📝 License

MIT © Bryan Cheng

