
from flask import Flask, render_template, request, jsonify
from db import init_db
from shipping_service import save_shipment, delete_last, get_last, print_label

app = Flask(__name__)

# Inizializza DB all'avvio dell'app
init_db()

@app.route("/")
def index():
    last = get_last()
    return render_template("index.html", saved=last)

@app.route("/save", methods=["POST"])
def save():
    data = request.get_json(silent=True) or {}
    ddt = data.get("ddt")
    tracking = data.get("tracking")
    courier = data.get("courier")  # opzionale, non richiesto dal frontend
    if not ddt or not tracking:
        return jsonify({"error": "Campi vuoti"}), 400
    record = save_shipment(ddt, tracking, courier)
    return jsonify(record)

@app.route("/delete_last", methods=["POST"])
def delete_record():
    ok = delete_last()
    if ok:
        return jsonify({"status": "deleted"})
    return jsonify({"status": "none"})

@app.route("/print", methods=["POST"])
def print_api():
    data = request.get_json(silent=True) or {}
    parcel_id = data.get("code")
    if not parcel_id:
        return jsonify({"error": "Campo vuoto"}), 400
    res = print_label(parcel_id)
    return jsonify(res)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
