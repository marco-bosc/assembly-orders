from flask import Flask, render_template, request, redirect, url_for, jsonify
import sqlite3
from datetime import date, timedelta

DB_PATH = "database.db"
app = Flask(__name__)

def ensure_columns():
    """Add quantity columns for operations if they don't exist (safe to run every start)."""
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    # get existing columns
    cur.execute("PRAGMA table_info(records)")
    cols = [r[1] for r in cur.fetchall()]
    additions = []
    if "deburring_qty" not in cols:
        additions.append("ALTER TABLE records ADD COLUMN deburring_qty INTEGER")
    if "sorting_qty" not in cols:
        additions.append("ALTER TABLE records ADD COLUMN sorting_qty INTEGER")
    if "waste_qty" not in cols:
        additions.append("ALTER TABLE records ADD COLUMN waste_qty INTEGER")
    for sql in additions:
        cur.execute(sql)
    conn.commit()
    conn.close()

def get_user_by_code(code):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    # users table uses user_code (create_tables.py uses that)
    cur.execute("SELECT id, first_name, last_name FROM users WHERE user_code = ?", (code,))
    row = cur.fetchone()
    conn.close()
    return row  # None or (id, first_name, last_name)

def format_date_it(d: date) -> str:
    giorni = ["lunedì","martedì","mercoledì","giovedì","venerdì","sabato","domenica"]
    mesi = ["gennaio","febbraio","marzo","aprile","maggio","giugno","luglio","agosto","settembre","ottobre","novembre","dicembre"]
    return f"{giorni[d.weekday()]} {d.day} {mesi[d.month - 1]} {d.year}"

# ensure extra columns exist
# ensure_columns()

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        # Save new record
        user_id = request.form.get("user_id")
        record_date = request.form.get("date")  # YYYY-MM-DD
        non_order = 1 if request.form.get("non_order") == "on" else 0

        production_order = None if non_order else (request.form.get("production_order") or None)
        quantity_raw = None if non_order else request.form.get("quantity")
        quantity = int(quantity_raw) if quantity_raw and quantity_raw.isdigit() else None

        deburring = 1 if request.form.get("deburring") == "on" else 0
        deburring_qty = request.form.get("deburring_qty")
        deburring_qty = int(deburring_qty) if deburring_qty and deburring_qty.isdigit() else None

        sorting = 1 if request.form.get("sorting") == "on" else 0
        sorting_qty = request.form.get("sorting_qty")
        sorting_qty = int(sorting_qty) if sorting_qty and sorting_qty.isdigit() else None

        waste_disposal = 1 if request.form.get("waste_disposal") == "on" else 0
        waste_qty = request.form.get("waste_qty")
        waste_qty = int(waste_qty) if waste_qty and waste_qty.isdigit() else None

        causale = request.form.get("causale") if request.form.get("causale") else None
        start_time = request.form.get("start_time") if request.form.get("start_time") else None
        finish_time = request.form.get("finish_time") if request.form.get("finish_time") else None

        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO records (
                date, user_id, production_order, quantity,
                deburring, deburring_qty,
                sorting, sorting_qty,
                waste_disposal, waste_qty,
                start_time, finish_time, non_order, causale
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            record_date, user_id, production_order, quantity,
            deburring, deburring_qty,
            sorting, sorting_qty,
            waste_disposal, waste_qty,
            start_time, finish_time, non_order, causale
        ))
        conn.commit()
        conn.close()

        # After saving reload index to allow new insertion (empty)
        return redirect(url_for("index"))

    # GET: prepare dates for the buttons and textual today
    today = date.today()
    dates = [
        {"label": "Oggi", "value": today.strftime("%Y-%m-%d")},
        {"label": "Ieri", "value": (today - timedelta(days=1)).strftime("%Y-%m-%d")},
        {"label": "Altro ieri", "value": (today - timedelta(days=2)).strftime("%Y-%m-%d")}
    ]
    today_text = format_date_it(today)
    today_value = today.strftime("%Y-%m-%d")
    return render_template("index.html", dates=dates, today_text=today_text, today_value=today_value)

@app.route("/check_user/<code>")
def check_user(code):
    user = get_user_by_code(code)
    if user:
        return jsonify({"exists": True, "id": user[0], "name": f"{user[1]} {user[2]}"})
    else:
        return jsonify({"exists": False})

@app.route("/history", methods=["GET"])
def history():
    code = request.args.get("code", "").strip()
    start_date = request.args.get("start_date")
    end_date = request.args.get("end_date")
    records = []
    if code:
        user = get_user_by_code(code)
        if user:
            conn = sqlite3.connect(DB_PATH)
            conn.row_factory = sqlite3.Row
            cur = conn.cursor()
            # default range if not provided: last 7 days
            if not start_date:
                start_date = (date.today() - timedelta(days=7)).strftime("%Y-%m-%d")
            if not end_date:
                end_date = date.today().strftime("%Y-%m-%d")
            cur.execute("""
                SELECT r.id, r.date, r.production_order, r.quantity,
                       r.deburring, r.deburring_qty,
                       r.sorting, r.sorting_qty,
                       r.waste_disposal, r.waste_qty,
                       r.start_time, r.finish_time, r.causale, r.non_order
                FROM records r
                JOIN users u ON r.user_id = u.id
                WHERE u.user_code = ? AND r.date BETWEEN ? AND ?
                ORDER BY r.date DESC, r.start_time DESC
            """, (code, start_date, end_date))
            rows = cur.fetchall()
            for row in rows:
                records.append({k: row[k] for k in row.keys()})
            conn.close()
    return render_template("history.html", records=records, code=code, start_date=start_date, end_date=end_date)

if __name__ == "__main__":
    app.run(debug=True)
