# app.py
from flask import Flask, render_template, request, redirect, url_for, jsonify
import sqlite3
from datetime import date, timedelta

DB_PATH = "database.db"
app = Flask(__name__)

def format_date_it(d: date) -> str:
    # d: datetime.date
    giorni = ["lunedì","martedì","mercoledì","giovedì","venerdì","sabato","domenica"]
    mesi = ["gennaio","febbraio","marzo","aprile","maggio","giugno","luglio","agosto","settembre","ottobre","novembre","dicembre"]
    # weekday(): Monday=0
    day_name = giorni[d.weekday()]
    month_name = mesi[d.month - 1]
    return f"{day_name} {d.day} {month_name} {d.year}"

def get_user_by_code(code):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT id, first_name, last_name FROM users WHERE user_code = ?", (code,))
    row = cur.fetchone()
    conn.close()
    return row  # None or (id, first_name, last_name)

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        # Insert new record
        user_id = request.form.get("user_id")
        record_date = request.form.get("date")  # YYYY-MM-DD
        non_order = 1 if request.form.get("non_order") == "on" else 0

        production_order = None if non_order else (request.form.get("production_order") or None)
        quantity_raw = None if non_order else request.form.get("quantity")
        quantity = int(quantity_raw) if quantity_raw and quantity_raw.isdigit() else None

        deburring = 1 if request.form.get("deburring") == "on" else 0
        sorting = 1 if request.form.get("sorting") == "on" else 0
        waste_disposal = 1 if request.form.get("waste_disposal") == "on" else 0
        causale = request.form.get("causale") if request.form.get("causale") else None
        start_time = request.form.get("start_time") if request.form.get("start_time") else None
        finish_time = request.form.get("finish_time") if request.form.get("finish_time") else None

        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO records (
                date, user_id, production_order, quantity,
                deburring, sorting, waste_disposal,
                start_time, finish_time, non_order, causale
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            record_date, user_id, production_order, quantity,
            deburring, sorting, waste_disposal,
            start_time, finish_time, non_order, causale
        ))
        conn.commit()
        conn.close()
        # After save, reload index (blank) for new insertion
        return redirect(url_for("index"))

    # GET: prepare dates (server-side)
    today = date.today()
    dates = [
        {"label": "Oggi", "value": today.strftime("%Y-%m-%d")},
        {"label": "Ieri", "value": (today - timedelta(days=1)).strftime("%Y-%m-%d")},
        {"label": "Altro ieri", "value": (today - timedelta(days=2)).strftime("%Y-%m-%d")}
    ]
    today_text = format_date_it(today)
    return render_template("index.html", dates=dates, today_text=today_text, today_value=today.strftime("%Y-%m-%d"))

@app.route("/check_user/<code>")
def check_user(code):
    user = get_user_by_code(code)
    if user:
        return jsonify({"exists": True, "id": user[0], "name": f"{user[1]} {user[2]}"})
    else:
        return jsonify({"exists": False})

@app.route("/history", methods=["GET"])
def history():
    # Accept query params: code, start_date, end_date
    code = request.args.get("code", "").strip()
    start_date = request.args.get("start_date")
    end_date = request.args.get("end_date")
    records = []
    user = None

    if code:
        user = get_user_by_code(code)
        if user:
            conn = sqlite3.connect(DB_PATH)
            conn.row_factory = sqlite3.Row
            cur = conn.cursor()
            # default date range if not provided: today
            if not start_date:
                start_date = (date.today() - timedelta(days=7)).strftime("%Y-%m-%d")  # default last 7 days
            if not end_date:
                end_date = date.today().strftime("%Y-%m-%d")

            cur.execute("""
                SELECT r.id, r.date, r.production_order, r.quantity, r.deburring, r.sorting, r.waste_disposal,
                       r.start_time, r.finish_time, r.causale, r.non_order
                FROM records r
                JOIN users u ON r.user_id = u.id
                WHERE u.user_code = ? AND r.date BETWEEN ? AND ?
                ORDER BY r.date DESC, r.start_time DESC
            """, (code, start_date, end_date))
            rows = cur.fetchall()
            # convert rows to list of dicts
            for row in rows:
                records.append({k: row[k] for k in row.keys()})
            conn.close()

    return render_template("history.html", records=records, code=code, start_date=start_date, end_date=end_date)
    
if __name__ == "__main__":
    app.run(debug=True)
