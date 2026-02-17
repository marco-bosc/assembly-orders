# from flask import Flask, render_template, request, redirect, url_for, jsonify
# from datetime import date, timedelta

# from queries import (
#     get_user_by_code,
#     insert_record,
#     get_history
# )

# app = Flask(__name__)


# # =========================
# # UTILS
# # =========================
# def format_date_it(d: date) -> str:
#     giorni = ["lunedì", "martedì", "mercoledì", "giovedì", "venerdì", "sabato", "domenica"]
#     mesi = ["gennaio", "febbraio", "marzo", "aprile", "maggio", "giugno",
#             "luglio", "agosto", "settembre", "ottobre", "novembre", "dicembre"]
#     return f"{giorni[d.weekday()]} {d.day} {mesi[d.month - 1]} {d.year}"


# # =========================
# # ROUTES
# # =========================
# @app.route("/", methods=["GET", "POST"])
# def index():
#     if request.method == "POST":
#         user_id = request.form.get("user_id")
#         record_date = request.form.get("date")
#         activity_type = request.form.get("activity_type")

#         non_order = 1 if activity_type in ["cut", "other"] else 0

#         production_order = None if non_order else (request.form.get("production_order") or None)
#         quantity_raw = None if non_order else request.form.get("quantity")
#         quantity = int(quantity_raw) if quantity_raw and quantity_raw.isdigit() else None

#         deburring = 1 if request.form.get("deburring") == "on" else 0
#         deburring_qty = request.form.get("deburring_qty")
#         deburring_qty = int(deburring_qty) if deburring_qty and deburring_qty.isdigit() else None

#         sorting = 1 if request.form.get("sorting") == "on" else 0
#         sorting_qty = request.form.get("sorting_qty")
#         sorting_qty = int(sorting_qty) if sorting_qty and sorting_qty.isdigit() else None

#         waste_disposal = 1 if request.form.get("waste_disposal") == "on" else 0
#         waste_qty = request.form.get("waste_qty")
#         waste_qty = int(waste_qty) if waste_qty and waste_qty.isdigit() else None

#         causale = request.form.get("causale") or None
#         start_time = request.form.get("start_time") or None
#         finish_time = request.form.get("finish_time") or None

#         cut_model = request.form.get("cut_model") if activity_type == "cut" else None

#         insert_record({
#             "date": record_date,
#             "user_id": user_id,
#             "production_order": production_order,
#             "quantity": quantity,
#             "deburring": deburring,
#             "deburring_qty": deburring_qty,
#             "sorting": sorting,
#             "sorting_qty": sorting_qty,
#             "waste_disposal": waste_disposal,
#             "waste_qty": waste_qty,
#             "start_time": start_time,
#             "finish_time": finish_time,
#             "non_order": non_order,
#             "causale": causale,
#             "cut_model": cut_model
#         })

#         return redirect(url_for("index"))

#     today = date.today()
#     dates = [
#         {"label": "Oggi", "value": today.strftime("%Y-%m-%d")},
#         {"label": "Ieri", "value": (today - timedelta(days=1)).strftime("%Y-%m-%d")},
#         {"label": "Altro ieri", "value": (today - timedelta(days=2)).strftime("%Y-%m-%d")},
#     ]

#     return render_template(
#         "index.html",
#         dates=dates,
#         today_text=format_date_it(today),
#         today_value=today.strftime("%Y-%m-%d")
#     )


# @app.route("/check_user/<code>")
# def check_user(code):
#     user = get_user_by_code(code)

#     if user:
#         return jsonify({
#             "exists": True,
#             "id": user.id,
#             "name": f"{user.first_name} {user.last_name}"
#         })

#     return jsonify({"exists": False})


# @app.route("/history", methods=["GET"])
# def history():
#     code = request.args.get("code", "").strip()
#     start_date = request.args.get("start_date")
#     end_date = request.args.get("end_date")

#     records = []

#     if code:
#         user = get_user_by_code(code)
#         if user:
#             if not start_date:
#                 start_date = (date.today() - timedelta(days=7)).strftime("%Y-%m-%d")
#             if not end_date:
#                 end_date = date.today().strftime("%Y-%m-%d")

#             records = get_history(code, start_date, end_date)

#     return render_template(
#         "history.html",
#         records=records,
#         code=code,
#         start_date=start_date,
#         end_date=end_date
#     )


# if __name__ == "__main__":
#     app.run(debug=True)


from flask import Flask, render_template, request, redirect, url_for, jsonify
from datetime import date, timedelta
from queries import get_user_by_code, insert_record, get_history

app = Flask(__name__)

# =========================
# UTILS
# =========================
def format_date_it(d: date) -> str:
    giorni = ["lunedì", "martedì", "mercoledì", "giovedì", "venerdì", "sabato", "domenica"]
    mesi = ["gennaio", "febbraio", "marzo", "aprile", "maggio", "giugno",
            "luglio", "agosto", "settembre", "ottobre", "novembre", "dicembre"]
    return f"{giorni[d.weekday()]} {d.day} {mesi[d.month - 1]} {d.year}"

# =========================
# ROUTES
# =========================
@app.route("/", methods=["GET", "POST"])
def index():
    today = date.today()
    dates = [
        {"label": "Oggi", "value": today.strftime("%Y-%m-%d")},
        {"label": "Ieri", "value": (today - timedelta(days=1)).strftime("%Y-%m-%d")},
        {"label": "Altro ieri", "value": (today - timedelta(days=2)).strftime("%Y-%m-%d")},
    ]

    message = None

    if request.method == "POST":
        try:
            operator_id = request.form.get("user_id")
            record_date = request.form.get("date")
            event_type = request.form.get("activity_type")

            # Ordine o materiale
            order_code = request.form.get("order_code") or None
            material = request.form.get("material") or None

            # Quantità
            quantity = request.form.get("quantity")
            quantity = int(quantity) if quantity and quantity.isdigit() else None
            material_quantity = request.form.get("material_quantity")
            material_quantity = int(material_quantity) if material_quantity and material_quantity.isdigit() else None

            # Operazioni manuali
            manual_deburring = int(request.form.get("deburring_qty") or 0)
            manual_sorting = int(request.form.get("sorting_qty") or 0)
            manual_waste = int(request.form.get("waste_qty") or 0)
            followed_cut_machine = True if request.form.get("followed_cut_machine") == "on" else False

            # Orari e causale
            start_time = request.form.get("start_time") or None
            end_time = request.form.get("end_time") or None
            causale = request.form.get("causale") or None

            insert_record({
                "operator_id": operator_id,
                "event_type": event_type,
                "date": record_date,
                "order_code": order_code,
                "material": material,
                "quantity": quantity or material_quantity,
                "manual_deburring": manual_deburring,
                "manual_sorting": manual_sorting,
                "manual_waste": manual_waste,
                "followed_cut_machine": followed_cut_machine,
                "start_time": start_time,
                "end_time": end_time,
                "causale": causale
            })
            message = "Record salvato con successo!"
        except Exception as e:
            message = f"Errore durante il salvataggio: {str(e)}"

    return render_template(
        "index.html",
        dates=dates,
        today_text=format_date_it(today),
        today_value=today.strftime("%Y-%m-%d"),
        message=message
    )

@app.route("/check_user/<code>")
def check_user(code):
    user = get_user_by_code(code)
    if user:
        return jsonify({"exists": True, "id": user.id, "name": f"{user.first_name} {user.last_name}"})
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
            if not start_date:
                start_date = (date.today() - timedelta(days=7)).strftime("%Y-%m-%d")
            if not end_date:
                end_date = date.today().strftime("%Y-%m-%d")
            records = get_history(code, start_date, end_date)

    return render_template("history.html", records=records, code=code, start_date=start_date, end_date=end_date)

if __name__ == "__main__":
    app.run(debug=True)
