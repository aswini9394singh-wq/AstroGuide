# AstroGuide – Astrology Web Application

AstroGuide is a simple, beginner-friendly astrology website built with **Flask**, **SQLite**, **HTML/CSS/JavaScript** and **Bootstrap 5**. Users can browse the 12 zodiac signs, find their sun sign from their date of birth, read a sample daily horoscope, check compatibility between two signs and send a message through a contact form.

> **Disclaimer:** All horoscope and compatibility content is sample data for entertainment only. Astrology is not scientifically proven.

---

## 1. Features

| Page | URL | What it does |
|------|-----|--------------|
| Home | `/` | Hero ("Discover Your Stars"), all 12 sign cards, daily horoscope preview |
| Zodiac Signs | `/zodiac` | All 12 signs plus the **Find Your Sign** date-of-birth form |
| Sign Detail | `/zodiac/<name>` | Symbol, dates, element, ruling planet, personality, strengths, weaknesses |
| Horoscope | `/horoscope?sign=leo` | Today's date + Love, Career, Health, Finance, General for the chosen sign |
| Compatibility | `/compatibility` | Pick two signs; get a percentage, description, strengths, challenges, summary |
| About | `/about` | Purpose of the site and a short intro to zodiac astrology |
| Contact | `/contact` | Validated form; messages are saved to SQLite |

---

## 2. Tech Stack

- **Backend:** Python 3 + Flask
- **Database:** SQLite (built into Python, no install needed)
- **Frontend:** HTML5, CSS3, JavaScript, Bootstrap 5 (CDN)
- **Icons:** Font Awesome (CDN)
- **Fonts:** Cormorant Garamond and Nunito (Google Fonts, CDN)

An internet connection is needed for the CDN files (Bootstrap, Font Awesome, fonts).

---

## 3. Folder Structure

```
AstroGuide/
├── app.py                  # Flask app: routes, data, logic, database
├── database.db             # SQLite database (auto-created on first run)
├── requirements.txt        # Python dependencies
├── README.md
├── templates/
│   ├── base.html           # Shared layout: navbar, flash messages, footer
│   ├── index.html          # Home page
│   ├── zodiac.html         # All signs + date-of-birth form
│   ├── zodiac_detail.html  # Single sign details
│   ├── horoscope.html      # Daily horoscope
│   ├── compatibility.html  # Compatibility checker
│   ├── about.html
│   ├── contact.html
│   └── error.html          # 404 / 500 pages
└── static/
    ├── css/style.css       # Theme: dark purple, lavender, cream, gold
    ├── js/script.js        # Client-side form validation messages
    └── images/             # Empty; zodiac symbols are Unicode characters
```

---

## 4. Installation and Running (VS Code)

**Requirements:** Python 3.9 or newer.

1. Unzip the project and open the `AstroGuide` folder in VS Code (File > Open Folder).
2. Open the terminal (Ctrl + `).
3. *(Recommended)* Create a virtual environment:
   - Windows: `python -m venv venv` then `venv\Scripts\activate`
   - macOS/Linux: `python3 -m venv venv` then `source venv/bin/activate`
4. Install dependencies: `pip install -r requirements.txt`
5. Start the app: `python app.py`
   (alternative: `flask --app app run --debug`)
6. Open **http://127.0.0.1:5000** in your browser.
7. Stop the server with **Ctrl + C**.

---

## 5. How It Works

### Data (in `app.py`)
- `SIGNS`: list of 12 dictionaries (name, symbol, date range, element, ruling planet, traits, strengths, weaknesses, URL slug).
- `LINES` and `FLAVOUR`: sample horoscope sentences per category and per element.
- `PAIRS` and `PAIR_TYPE`: sample compatibility data grouped by element pairing.

### Sign calculator
Each sign stores its start (month, day). Given a birth date, the app picks the sign with the **latest start date on or before** that day. Dates before Jan 20 have no match in that list, so they fall back to **Capricorn** (Dec 22 – Jan 19). The form also rejects invalid and future dates.

### Daily horoscope
For each category, one of three sample lines is chosen using `date.toordinal() + sign index`, so the text changes each day and differs between signs. An element-based sentence is added to it.

### Compatibility
1. Same element: base 84%.
2. Fire + Air or Earth + Water (harmonious): base 88%.
3. Fire + Earth or Air + Water (neutral): base 65%.
4. Fire + Water or Earth + Air (challenging): base 50%.
5. A small symmetric adjustment (-4 to +4) makes each pair's score distinct, so A + B equals B + A. Scores are limited to 40–98%.

### Contact form and database
Table `contact_messages`:

| Column | Type | Notes |
|--------|------|-------|
| id | INTEGER | Primary key, auto-increment |
| name | TEXT | Required |
| email | TEXT | Required |
| subject | TEXT | Required |
| message | TEXT | Required |
| created_at | TEXT | Defaults to current timestamp |

Validation rules: name 2–100 characters, valid email format, subject 3–150 characters, message 10–2000 characters. Inserts use **parameterised queries** (`?` placeholders) to prevent SQL injection. After a successful save, the app redirects (Post/Redirect/Get) and shows a success message.

### Error handling
Invalid sign names return a 404 page. Unexpected errors show a friendly 500 page. Invalid form input shows messages instead of crashing.

---

## 6. Testing Checklist

1. **Navigation:** click every navbar and footer link; none should be broken.
2. **Zodiac cards:** click any card (Home or Zodiac page) to open its detail page.
3. **Sign finder:**
   - `2000-11-01` → Scorpio
   - `2001-01-05` → Capricorn
   - `2001-03-21` → Aries
   - `2001-03-20` → Pisces
   - A future date or empty field → error message
4. **Horoscope:** with no sign selected you see a prompt; choosing a sign shows today's date and all 5 categories.
5. **Compatibility:** try Aries + Leo (high), Aries + Cancer (low); submit without choosing a sign to see the error.
6. **Contact form:**
   - Submit empty → validation errors
   - Invalid email like `abc` → error
   - Valid data → success message
   - View saved rows:
     `python -c "import sqlite3;print(sqlite3.connect('database.db').execute('select * from contact_messages').fetchall())"`
7. **Responsive:** resize the browser or use DevTools device mode; the navbar should collapse into a menu and cards should stack.
8. **404:** visit `/anything-wrong` to see the error page.

---

## 7. Customising

- **Edit content:** change sign descriptions, horoscope lines or compatibility text in the data section at the top of `app.py`.
- **Change colours:** edit the CSS variables at the top of `static/css/style.css` (`--purple`, `--lavender`, `--cream`, `--gold`).
- **Secret key:** replace `app.secret_key` in `app.py` with a long random string before deploying anywhere public.
- **Debug mode:** `debug=True` is for development only. Turn it off in production.

---

## 8. Troubleshooting

| Problem | Fix |
|---------|-----|
| `No module named flask` | Activate your virtual environment, then run `pip install -r requirements.txt` |
| `python` not found | Try `python3`, or reinstall Python and tick "Add to PATH" |
| Port 5000 already in use | Run `flask --app app run --debug --port 5001` |
| Page looks unstyled | Check your internet connection (Bootstrap loads from a CDN) |
| Want to reset messages | Stop the server and delete `database.db`; it is recreated on next start |

---

## 9. Possible Future Improvements

- Per-sign horoscope text (each sign with its own unique lines)
- An admin page to view contact messages
- Optional user profiles table
- Illustrated zodiac artwork in `static/images/`

---

## 10. Streamlit Dashboard (`dashboard.py`)

A second interface built with Streamlit. It imports the same signs, horoscope and compatibility logic from `app.py` and reads the same `database.db`, so both apps stay in sync.

**Run it:** `streamlit run dashboard.py` (opens at http://localhost:8501). Run the Flask site separately with `python app.py` if you want to submit contact messages.

| Dashboard page | What it shows |
|----------------|---------------|
| Overview | Metrics (signs, saved messages, today's date), charts of signs by element and ruling planet, table of all signs |
| Zodiac Explorer | Pick a sign to see dates, element, planet, personality, strengths, weaknesses |
| Find Your Sign | Date picker that returns your sun sign |
| Daily Horoscope | Pick a sign; tabs for Love, Career, Health, Finance, General |
| Compatibility | Two signs: score, progress bar, strengths, challenges, plus a bar chart of the first sign against all 12 |
| Contact Messages | Messages saved by the Flask contact form, with search and CSV download |
#   A s t r o G u i d e  
 