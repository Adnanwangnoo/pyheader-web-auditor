# 🛡️ SecHeaders.audit — Web Security Header Auditor

A Flask + Claude AI app that analyzes HTTP security headers and gives you an A–F grade with detailed recommendations.

## Quick Start

### 1. Clone / open the folder in VS Code

### 2. Create & activate a virtual environment
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Mac / Linux
source venv/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Add your Anthropic API key
```bash
cp .env.example .env
# Edit .env and replace sk-ant-your-key-here with your real key
# Get one at https://console.anthropic.com
```

### 5. Run the app
```bash
python app.py
```

Open **http://127.0.0.1:5000** in your browser.

---

## Features

- 🔗 **Fetch by URL** — server-side header fetching (no CORS issues)
- 📋 **Paste Headers** — paste raw headers from DevTools
- 🎯 **10 security headers** checked and graded
- 🤖 **AI analysis** of each header's value and configuration
- 📊 **A–F score** with overall summary
- 🔧 **Top 3 fix recommendations**

## Project Structure

```
security-header-auditor/
├── app.py              ← Flask backend
├── requirements.txt    ← Python dependencies
├── .env                ← Your API key (never commit this)
├── .gitignore
├── templates/
│   └── index.html      ← Frontend UI
└── static/
    └── style.css       ← Styles
```

## Security Headers Checked

| Header | Risk Category |
|--------|--------------|
| Content-Security-Policy | XSS Prevention |
| Strict-Transport-Security | HTTPS Enforcement |
| X-Frame-Options | Clickjacking |
| X-Content-Type-Options | MIME Sniffing |
| Referrer-Policy | Data Leakage |
| Permissions-Policy | Feature Abuse |
| X-XSS-Protection | Legacy XSS Filter |
| Cross-Origin-Embedder-Policy | Resource Isolation |
| Cross-Origin-Opener-Policy | Context Isolation |
| Cross-Origin-Resource-Policy | Resource Sharing |
