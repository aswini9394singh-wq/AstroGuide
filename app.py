"""AstroGuide - a simple astrology web app (Flask + SQLite).
All horoscope/compatibility content is sample entertainment data."""
import os, re, sqlite3
from datetime import date, datetime
from flask import Flask, render_template, request, redirect, url_for, flash, abort

app = Flask(__name__)
app.secret_key = "change-this-secret-key"  # needed for flash messages
DB = os.path.join(os.path.dirname(os.path.abspath(__file__)), "database.db")

# ---------- Sample data ----------
# name, symbol, (start month, day), date range, element, planet, traits, strengths, weaknesses
_RAW = [
 ("Aries","♈",(3,21),"Mar 21 – Apr 19","Fire","Mars","Bold, energetic and competitive.","Courageous, confident, enthusiastic","Impatient, impulsive, short-tempered"),
 ("Taurus","♉",(4,20),"Apr 20 – May 20","Earth","Venus","Steady, sensual and loyal.","Reliable, patient, practical","Stubborn, possessive, resistant to change"),
 ("Gemini","♊",(5,21),"May 21 – Jun 20","Air","Mercury","Curious, witty and sociable.","Adaptable, communicative, quick learner","Restless, inconsistent, indecisive"),
 ("Cancer","♋",(6,21),"Jun 21 – Jul 22","Water","Moon","Nurturing, intuitive and protective.","Caring, empathetic, loyal","Moody, clingy, overly sensitive"),
 ("Leo","♌",(7,23),"Jul 23 – Aug 22","Fire","Sun","Warm, dramatic and generous.","Charismatic, creative, generous","Prideful, attention-seeking, stubborn"),
 ("Virgo","♍",(8,23),"Aug 23 – Sep 22","Earth","Mercury","Analytical, modest and hardworking.","Detail-oriented, helpful, dependable","Perfectionist, overcritical, worry-prone"),
 ("Libra","♎",(9,23),"Sep 23 – Oct 22","Air","Venus","Charming, fair-minded and gracious.","Diplomatic, cooperative, social","Indecisive, conflict-avoidant, people-pleasing"),
 ("Scorpio","♏",(10,23),"Oct 23 – Nov 21","Water","Pluto","Intense, passionate and resourceful.","Determined, brave, perceptive","Secretive, jealous, resentful"),
 ("Sagittarius","♐",(11,22),"Nov 22 – Dec 21","Fire","Jupiter","Adventurous, optimistic and honest.","Open-minded, cheerful, freedom-loving","Blunt, careless, restless"),
 ("Capricorn","♑",(12,22),"Dec 22 – Jan 19","Earth","Saturn","Disciplined, ambitious and responsible.","Persistent, wise, goal-oriented","Rigid, pessimistic, workaholic"),
 ("Aquarius","♒",(1,20),"Jan 20 – Feb 18","Air","Uranus","Original, independent and humanitarian.","Innovative, progressive, idealistic","Aloof, unpredictable, stubborn"),
 ("Pisces","♓",(2,19),"Feb 19 – Mar 20","Water","Neptune","Dreamy, compassionate and artistic.","Imaginative, gentle, intuitive","Escapist, overly trusting, indecisive"),
]
KEYS = ("name","symbol","start","dates","element","planet","traits","strengths","weaknesses")
SIGNS = [dict(zip(KEYS, r), slug=r[0].lower()) for r in _RAW]
BY_SLUG = {s["slug"]: s for s in SIGNS}

# Horoscope: 3 sample lines per category (rotated daily) + an element flavour line.
CATEGORIES = ["Love", "Career", "Health", "Finance", "General"]
LINES = {
 "Love": ["Honest conversation brings you closer to someone special.","A small gesture means more than a grand plan today.","Listen first; clarity in a relationship follows."],
 "Career": ["Focus on one priority and finish it well.","A colleague may offer a useful idea; stay open.","Steady effort now sets up progress later this week."],
 "Health": ["Take short breaks and drink enough water.","A walk outdoors can lift your mood and energy.","Keep a regular sleep routine tonight."],
 "Finance": ["Review your spending before any big purchase.","Saving a small amount today builds a good habit.","Avoid impulsive buys; compare options first."],
 "General": ["A calm, patient approach works best today.","Unexpected news may open a new door.","Trust your preparation and take things one step at a time."],
}
FLAVOUR = {"Fire":"Your fiery energy is high, so channel it wisely.","Earth":"Grounded routines keep you steady today.",
           "Air":"Conversations and fresh ideas are your strength today.","Water":"Your intuition is sharp; notice how you feel."}

# Compatibility: sample data by element pairing.
PAIRS = {
 "same": (84,"Two signs sharing an element understand each other instinctively.",
          ["Shared values and outlook","Easy understanding"],["May amplify each other's flaws","Can get too comfortable"]),
 "harmonious": (88,"These elements naturally support and inspire each other.",
          ["Complementary strengths","Natural chemistry"],["Different paces at times","Needs honest communication"]),
 "neutral": (65,"A balanced pairing where differences can be learned from.",
          ["Each brings something new","Room to grow together"],["Different priorities","Requires patience"]),
 "challenging": (50,"Quite different temperaments; effort and respect make it work.",
          ["Opposites can teach each other","Exciting contrast"],["Clashing communication styles","Different emotional needs"]),
}
PAIR_TYPE = {frozenset(["Fire","Air"]):"harmonious", frozenset(["Earth","Water"]):"harmonious",
             frozenset(["Fire","Earth"]):"neutral", frozenset(["Air","Water"]):"neutral",
             frozenset(["Fire","Water"]):"challenging", frozenset(["Earth","Air"]):"challenging"}

# ---------- Helpers ----------
def get_sign_by_date(month, day):
    """Latest sign whose start date is on/before (month, day); before Jan 20 -> Capricorn."""
    ok = [s for s in SIGNS if s["start"] <= (month, day)]
    return max(ok, key=lambda s: s["start"]) if ok else BY_SLUG["capricorn"]

def horoscope_for(sign, today):
    i = SIGNS.index(sign)
    return {c: LINES[c][(today.toordinal() + i) % 3] + " " + FLAVOUR[sign["element"]] for c in CATEGORIES}

def compatibility(a, b):
    key = "same" if a["element"] == b["element"] else PAIR_TYPE[frozenset([a["element"], b["element"]])]
    base, desc, strengths, challenges = PAIRS[key]
    i, j = SIGNS.index(a), SIGNS.index(b)
    score = max(40, min(98, base + (i * j + i + j) % 9 - 4))  # symmetric small variation
    return dict(score=score, desc=desc, strengths=strengths, challenges=challenges,
                summary=f"{a['name']} ({a['element']}) and {b['name']} ({b['element']}) score {score}%. {desc}")

def db():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with db() as conn:
        conn.execute("""CREATE TABLE IF NOT EXISTS contact_messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL, email TEXT NOT NULL,
            subject TEXT NOT NULL, message TEXT NOT NULL,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP)""")

# ---------- Routes ----------
@app.route("/")
def index():
    return render_template("index.html", signs=SIGNS, preview=SIGNS[:3], today=date.today(),
                           horoscopes={s["slug"]: horoscope_for(s, date.today())["General"] for s in SIGNS[:3]})

@app.route("/zodiac", methods=["GET", "POST"])
def zodiac():
    """Lists all signs; POST handles the date-of-birth 'Find your sign' form."""
    found, error = None, None
    if request.method == "POST":
        try:
            dob = datetime.strptime(request.form.get("dob", ""), "%Y-%m-%d").date()
            if dob > date.today():
                error = "Date of birth cannot be in the future."
            else:
                found = get_sign_by_date(dob.month, dob.day)
        except ValueError:
            error = "Please enter a valid date of birth."
    return render_template("zodiac.html", signs=SIGNS, found=found, error=error, today=date.today())

@app.route("/zodiac/<slug>")
def zodiac_detail(slug):
    sign = BY_SLUG.get(slug.lower())
    if not sign: abort(404)
    return render_template("zodiac_detail.html", sign=sign)

@app.route("/horoscope")
def horoscope():
    sign = BY_SLUG.get(request.args.get("sign", "").lower())
    today = date.today()
    return render_template("horoscope.html", signs=SIGNS, sign=sign, today=today,
                           content=horoscope_for(sign, today) if sign else None)

@app.route("/compatibility", methods=["GET", "POST"])
def compat():
    result = a = b = error = None
    if request.method == "POST":
        a, b = BY_SLUG.get(request.form.get("sign1", "")), BY_SLUG.get(request.form.get("sign2", ""))
        if a and b: result = compatibility(a, b)
        else: error = "Please choose both zodiac signs."
    return render_template("compatibility.html", signs=SIGNS, result=result, a=a, b=b, error=error)

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/contact", methods=["GET", "POST"])
def contact():
    form = {k: request.form.get(k, "").strip() for k in ("name", "email", "subject", "message")}
    errors = []
    if request.method == "POST":
        if not 2 <= len(form["name"]) <= 100: errors.append("Name must be 2-100 characters.")
        if not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", form["email"]): errors.append("Enter a valid email address.")
        if not 3 <= len(form["subject"]) <= 150: errors.append("Subject must be 3-150 characters.")
        if not 10 <= len(form["message"]) <= 2000: errors.append("Message must be 10-2000 characters.")
        if not errors:
            with db() as conn:  # parameterised query prevents SQL injection
                conn.execute("INSERT INTO contact_messages (name,email,subject,message) VALUES (?,?,?,?)",
                             (form["name"], form["email"], form["subject"], form["message"]))
            flash("Thanks! Your message has been sent.", "success")
            return redirect(url_for("contact"))
    return render_template("contact.html", form=form, errors=errors)

@app.errorhandler(404)
def not_found(e):
    return render_template("error.html", code=404, msg="That page could not be found."), 404

@app.errorhandler(500)
def server_error(e):
    return render_template("error.html", code=500, msg="Something went wrong on our side."), 500

init_db()
if __name__ == "__main__":
    app.run(debug=True)
