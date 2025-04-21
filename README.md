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
