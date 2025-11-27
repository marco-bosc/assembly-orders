# app.py
from flask import Flask, request, render_template, jsonify, g
import sqlite3
from datetime import datetime
import os

DB_PATH = os.environ.get("DB_PATH", "shipments.db")
TEMPLATE_NAME = "tracking_index.html"

app = Flask(__name__, static_folder="static", template_folder="templates")

def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(DB_PATH)
        g.db.row_factory = sqlite3.Row
    return g.db

def init_db():
    sql = """
    CREATE TABLE IF NOT EXISTS shipments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        ddt TEXT,
        tracking TEXT,
        carrier TEXT,
        tracking_url TEXT,
        created_at TEXT
    );
    """
    conn = get_db()
    conn.execute(sql)
    conn.commit()

@app.teardown_appcontext
def close_connection(exception):
    db = g.pop("db", None)
    if db is not None:
        db.close()

# ------------------------------
# INIT DB (Flask 3 compatible)
# ------------------------------
db_initialized = False

@app.before_request
def ensure_db_initialized():
    global db_initialized
    if not db_initialized:
        init_db()
        db_initialized = True


# ------------------------------
# TRACKING DETECTOR
# ------------------------------
def detect_carrier_and_url(code):
    code = (code or "").strip()

    if not code:
        return ("UNKNOWN", None)

    # TNT: 9 digits → usa .com
    if code.isdigit() and len(code) == 9:
        return (
            "TNT",
            f"https://www.tnt.com/express/it_it/site/shipping-tools/tracking.html?searchType=con&cons={code}"
        )

    # BRT
    if code.isdigit() and 12 <= len(code) <= 14:
        return (
            "BRT",
            f"https://vas.brt.it/vas/spedizione?lang=it&spedizione={code}"
        )

    return ("UNKNOWN", None)


# ------------------------------
# INDEX
# ------------------------------
@app.route("/", methods=["GET"])
def index():
    return render_template(TEMPLATE_NAME)


# ------------------------------
# SAVE (ORA FUNZIONA CON JSON)
# ------------------------------
@app.route("/save", methods=["POST"])
def save():
    # 🌟 SUPPORTA SIA JSON CHE FORM POST
    if request.is_json:
        payload = request.get_json()
        ddt = (payload.get("ddt") or "").strip()
        tracking = (payload.get("tracking") or "").strip()
    else:
        ddt = (request.form.get("ddt") or "").strip()
        tracking = (request.form.get("tracking") or "").strip()

    if not tracking:
        return jsonify({"saved": False, "error": "Tracking mancante"}), 400

    carrier, tracking_url = detect_carrier_and_url(tracking)
    created_at = datetime.utcnow().isoformat()

    conn = get_db()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO shipments (ddt, tracking, carrier, tracking_url, created_at)
        VALUES (?, ?, ?, ?, ?)
    """, (ddt or None, tracking or None, carrier, tracking_url, created_at))

    conn.commit()
    new_id = cur.lastrowid

    return jsonify({
        "saved": True,
        "id": new_id,
        "ddt": ddt,
        "tracking": tracking,
        "carrier": carrier,
        "tracking_url": tracking_url
    })


# ------------------------------
# HISTORY API
# ------------------------------
@app.route("/api/history", methods=["GET"])
def history_api():
    limit = int(request.args.get("limit", 100))
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM shipments ORDER BY id DESC LIMIT ?", (limit,))
    rows = [dict(r) for r in cur.fetchall()]
    return jsonify(rows)


# ------------------------------
# HISTORY HTML
# ------------------------------
@app.route("/history", methods=["GET"])
def history_html():
    limit = int(request.args.get("limit", 200))
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM shipments ORDER BY id DESC LIMIT ?", (limit,))
    rows = cur.fetchall()
    return render_template("history.html", records=rows)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
