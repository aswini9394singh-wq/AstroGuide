# AstroGuide

A simple, beginner-friendly astrology web app built with **Flask**, **SQLite**, **HTML/CSS/JavaScript** and **Bootstrap 5**, plus a **Streamlit dashboard**.

Users can browse the 12 zodiac signs, find their sun sign from their date of birth, read a sample daily horoscope, check compatibility between two signs, and send a message through a contact form.

> **Disclaimer:** All horoscope and compatibility content is sample data for entertainment only. Astrology is not scientifically proven.

---

## Table of Contents

1. [Features](#features)
2. [Tech Stack](#tech-stack)
3. [Project Structure](#project-structure)
4. [Installation](#installation)
5. [Running the Apps](#running-the-apps)
6. [How It Works](#how-it-works)
7. [Streamlit Dashboard](#streamlit-dashboard)
8. [Testing Checklist](#testing-checklist)
9. [Customising](#customising)
10. [Troubleshooting](#troubleshooting)
11. [Future Improvements](#future-improvements)

---

## Features

| Page | URL | Description |
|------|-----|-------------|
| Home | `/` | Hero section, all 12 sign cards, daily horoscope preview |
| Zodiac Signs | `/zodiac` | All signs plus the Find Your Sign date-of-birth form |
| Sign Detail | `/zodiac/<name>` | Symbol, dates, element, ruling planet, personality, strengths, weaknesses |
| Horoscope | `/horoscope?sign=leo` | Today's date with Love, Career, Health, Finance and General |
| Compatibility | `/compatibility` | Pick two signs and get a score, description, strengths and challenges |
| About | `/about` | Purpose of the site and a short intro to zodiac astrology |
| Contact | `/contact` | Validated form that saves messages to SQLite |

---

## Tech Stack

- **Backend:** Python 3 and Flask
- **Database:** SQLite (built into Python)
- **Frontend:** HTML5, CSS3, JavaScript, Bootstrap 5 (CDN)
- **Icons:** Font Awesome (CDN)
- **Fonts:** Cormorant Garamond and Nunito (Google Fonts)
- **Dashboard:** Streamlit and pandas

An internet connection is needed for the CDN files (Bootstrap, Font Awesome, fonts).

---

## Project Structure

```text
AstroGuide/
├── app.py                  # Flask app: routes, data, logic, database
├── dashboard.py            # Streamlit dashboard
├── database.db             # SQLite database (auto-created on first run)
├── requirements.txt        # Python dependencies
├── README.md
├── templates/
│   ├── base.html           # Shared layout: navbar, messages, footer
│   ├── index.html          # Home page
│   ├── zodiac.html         # All signs and date-of-birth form
│   ├── zodiac_detail.html  # Single sign details
│   ├── horoscope.html      # Daily horoscope
│   ├── compatibility.html  # Compatibility checker
│   ├── about.html
│   ├── contact.html
│   └── error.html          # 404 and 500 pages
└── static/
    ├── css/style.css       # Theme: dark purple, lavender, cream, gold
    ├── js/script.js        # Client-side form validation messages
    └── images/             # Empty (zodiac symbols are Unicode characters)
```

---

## Installation

**Requirements:** Python 3.9 or newer.

1. Unzip the project and open the `AstroGuide` folder in VS Code (File > Open Folder).
2. Open the terminal (Ctrl + `).
3. Optional but recommended, create a virtual environment:

   ```bash
   # Windows
   python -m venv venv
   venv\Scripts\activate

   # macOS / Linux
   python3 -m venv venv
   source venv/bin/activate
   ```

4. Install the dependencies:

   ```bash
   pip install -r requirements.txt
   ```

---

## Running the Apps

Run these from inside the `AstroGuide` folder.

**Flask website**

```bash
python app.py
```

Open http://127.0.0.1:5000

**Streamlit dashboard** (use a second terminal if the website is running)

```bash
streamlit run dashboard.py
```

Open http://localhost:8501

If the `streamlit` command is not recognised, use:

```bash
python -m streamlit run dashboard.py
```

Stop either app with **Ctrl + C**.

---

## How It Works

### Data (in `app.py`)

- `SIGNS`: list of 12 dictionaries (name, symbol, date range, element, ruling planet, traits, strengths, weaknesses, URL slug).
- `LINES` and `FLAVOUR`: sample horoscope sentences per category and per element.
- `PAIRS` and `PAIR_TYPE`: sample compatibility data grouped by element pairing.

### Sign calculator

Each sign stores its start month and day. Given a birth date, the app picks the sign with the latest start date on or before that day. Dates before Jan 20 fall back to Capricorn (Dec 22 to Jan 19). The form also rejects invalid and future dates.

### Daily horoscope

For each category, one of three sample lines is chosen using the date and the sign's position, so the text changes every day and differs between signs. An element-based sentence is added to it.

### Compatibility

| Element pairing | Type | Base score |
|-----------------|------|-----------|
| Same element | Same | 84% |
| Fire + Air, Earth + Water | Harmonious | 88% |
| Fire + Earth, Air + Water | Neutral | 65% |
| Fire + Water, Earth + Air | Challenging | 50% |

A small symmetric adjustment (-4 to +4) makes each pair's score distinct, so A + B always equals B + A. Scores are limited to 40 to 98 percent.

### Contact form and database

Table `contact_messages`:

| Column | Type | Notes |
|--------|------|-------|
| id | INTEGER | Primary key, auto-increment |
| name | TEXT | Required |
| email | TEXT | Required |
| subject | TEXT | Required |
| message | TEXT | Required |
| created_at | TEXT | Defaults to the current timestamp |

Validation rules:

- Name: 2 to 100 characters
- Email: valid format
- Subject: 3 to 150 characters
- Message: 10 to 2000 characters

Inserts use parameterised queries to prevent SQL injection. After a successful save the app redirects and shows a success message.

### Error handling

Unknown sign names return a 404 page, unexpected errors show a friendly 500 page, and invalid form input shows messages instead of crashing.

---

## Streamlit Dashboard

`dashboard.py` is a second interface that imports the same signs, horoscope and compatibility logic from `app.py` and reads the same `database.db`. Messages sent from the Flask contact form appear in the dashboard.

| Dashboard page | What it shows |
|----------------|---------------|
| Overview | Metrics, charts of signs by element and planet, table of all signs |
| Zodiac Explorer | Pick a sign to see dates, element, planet, personality, strengths, weaknesses |
| Find Your Sign | Date picker that returns your sun sign |
| Daily Horoscope | Tabs for Love, Career, Health, Finance and General |
| Compatibility | Score, strengths, challenges and a chart of one sign against all 12 |
| Contact Messages | Saved messages with search and CSV download |

---

## Testing Checklist

1. **Navigation:** click every navbar and footer link.
2. **Zodiac cards:** click any card to open its detail page.
3. **Sign finder:**
   - `2000-11-01` gives Scorpio
   - `2001-01-05` gives Capricorn
   - `2001-03-21` gives Aries
   - `2001-03-20` gives Pisces
   - A future date or empty field shows an error
4. **Horoscope:** with no sign selected you see a prompt. Choosing a sign shows today's date and all 5 categories.
5. **Compatibility:** try Aries + Leo (high) and Aries + Cancer (low). Submit without choosing a sign to see the error.
6. **Contact form:**
   - Empty submit shows validation errors
   - An invalid email such as `abc` shows an error
   - Valid data shows a success message
7. **Check saved messages:**

   ```bash
   python -c "import sqlite3;print(sqlite3.connect('database.db').execute('select * from contact_messages').fetchall())"
   ```

8. **Responsive:** resize the browser or use DevTools device mode. The navbar should collapse and cards should stack.
9. **404 page:** visit `/anything-wrong`.
10. **Dashboard:** open each sidebar page and confirm none shows an error.

---

## Customising

- **Content:** edit sign descriptions, horoscope lines or compatibility text in the data section at the top of `app.py`.
- **Colours:** edit the CSS variables at the top of `static/css/style.css`.
- **Secret key:** replace `app.secret_key` in `app.py` with a long random string before deploying publicly.
- **Debug mode:** `debug=True` is for development only. Turn it off in production.

---

## Troubleshooting

| Problem | Fix |
|---------|-----|
| `No module named flask` | Activate your virtual environment, then run `pip install -r requirements.txt` |
| `python` not found | Try `python3`, or reinstall Python and tick "Add to PATH" |
| Port 5000 already in use | Run `flask --app app run --debug --port 5001` |
| Page looks unstyled | Check your internet connection (Bootstrap loads from a CDN) |
| Reset saved messages | Stop the apps and delete `database.db`. It is recreated on next start |

---

## Future Improvements

- Per-sign horoscope text
- Admin login for viewing contact messages
- Optional user profiles table
- Illustrated zodiac artwork in `static/images/`
