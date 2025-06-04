# 🎓 Admissions Automation System

An intelligent admissions system built using **Django + PostgreSQL + React.js**, enhanced with **LangChain** for natural language queries and **APScheduler** for automated reminders and escalations.

---

## ⚙️ Setup Instructions

### 🔧 Backend Setup (Django + PostgreSQL)

1. **Clone the repo**

```bash
git clone https://github.com/your-org/admissions-system.git
cd admissions-system
```

2. **Create virtual environment & install dependencies**

```bash
python -m venv venv
venv/Scripts/activate  # Windows
pip install -r requirements.txt
```

3. **Set up PostgreSQL database**

* Create a PostgreSQL database and user
* Add credentials to your `.env`:

```ini
POSTGRES_DB=admission_system_webq
POSTGRES_USER=postgres
POSTGRES_PASSWORD=root
POSTGRES_HOST="localhost"
POSTGRES_PORT = 5433
```

4. **Set up other environment variables in `.env`**

```ini
DEBUG = True

# Database settings
POSTGRES_DB=admission_system_webq
POSTGRES_USER=postgres
POSTGRES_PASSWORD=root
POSTGRES_HOST="localhost"
POSTGRES_PORT = 5433

# Email
EMAIL_HOST = 'sandbox.smtp.mailtrap.io'
EMAIL_HOST_USER = '*******'
EMAIL_HOST_PASSWORD = '*******'
EMAIL_PORT = '*******'
DEFAULT_FROM_EMAIL = 'no-reply@text.com'

#OpenAI
OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxx
```

5. **Apply migrations and create superuser**

```bash
python manage.py migrate
python manage.py createsuperuser

#Seed test users
python manage.py seed_users
```

6. **Run the development server**

```bash
python manage.py runserver
```

## 🧠 Chosen Task Explanation

The system automates the **student offer letter tracking** process:

* Sends **automatic email reminders** if a student hasn't signed the offer within **3 days**.
* **Escalates** to a team lead if not signed within **5 days**.
* Tracks actions in an **Audit Log**.
* Supports **natural language queries** using LangChain, like:

  * "Which offer letters are pending for more than 3 days?"
  * "Show escalated offers"

---

## 📡 API Descriptions

### 🔐 Auth

* `POST /api/login/` – Obtain JWT tokens

### 📄 Offer Letters

* `GET /api/admissions/send-offer-letter` – List all offer letters
* `POST /api//admissions/send-offer-letter/` – Send offer letters
* `PUT /api/offers/<id>/sign/` – Mark offer letter as signed

### 📬 Reminders (APScheduler)

* Automatically triggered every 30 minutes: checks for unsigned offers & escalates if needed

### 🧠 LangChain

* `GET /api/admissions/langchain-query?query=<your question>` – Ask natural language questions about offer letters

---

## ⚖️ Trade-offs and Known Limitations

| Aspect            | Decision / Limitation                                                |
| ----------------- | -------------------------------------------------------------------- |
| Scheduler         | Used APScheduler instead of cron (cross-platform support)            |
| LangChain agent   | Single-agent using OpenAI with basic tools                           |
| Auth              | JWT (stateless) – no refresh logic yet                               |
| Email setup       | SMTP-based – no fallback if fails                                    |
| LangChain queries | Limited to predefined tool logic – doesn’t handle fuzzy queries well |

---

## 🤖 LangChain Integration

LangChain allows users to ask questions like:

* *"Which students haven’t signed in 3 days?"*
* *"Escalated offers?"*

### 🔧 Setup Details

* Agent: `initialize_agent` with `ChatOpenAI`
* Tools: Custom Python functions (`get_pending_offers`, `get_escalated_offers`, etc.)
* Model: GPT-4o or GPT-3.5-turbo
* Prompt: Dynamically routed to tools based on query intent

### 📄 Example Tool

```python
Tool(
    name="PendingOffersOver3Days",
    func=get_pending_offers,
    description="Returns offers not signed after 3 days. Use for questions about unsigned offers."
)
```

---


## 👤 Author

Athul VL

---


