# from sqlalchemy import text
# from db import engine

# def get_user_by_code(code):
#     sql = text("""
#         SELECT id, first_name, last_name
#         FROM users
#         WHERE user_code = :code
#     """)

#     with engine.connect() as conn:
#         return conn.execute(sql, {"code": code}).fetchone()

# def insert_record(data):
#     sql = text("""
#         INSERT INTO records (
#             date, user_id, production_order, quantity,
#             deburring, deburring_qty,
#             sorting, sorting_qty,
#             waste_disposal, waste_qty,
#             start_time, finish_time, non_order, causale, cut_model
#         ) VALUES (
#             :date, :user_id, :production_order, :quantity,
            
#             :start_time, :finish_time, :non_order, :causale, :cut_model
#         )
#     """)

#     with engine.begin() as conn:
#         conn.execute(sql, data)

# def get_history(code, start_date, end_date):
#     sql = text("""
#         SELECT r.id, r.date, r.production_order, r.quantity,
#                r.deburring, r.deburring_qty,
#                r.sorting, r.sorting_qty,
#                r.waste_disposal, r.waste_qty,
#                r.start_time, r.finish_time, r.causale, r.non_order
#         FROM records r
#         JOIN users u ON r.user_id = u.id
#         WHERE u.user_code = :code
#           AND r.date BETWEEN :start AND :end
#         ORDER BY r.date DESC, r.start_time DESC
#     """)

#     with engine.connect() as conn:
#         return conn.execute(sql, {
#             "code": code,
#             "start": start_date,
#             "end": end_date
#         }).mappings().all()


from sqlalchemy import text
from db import engine

def get_user_by_code(code):
    sql = text("""
        SELECT id, first_name, last_name
        FROM hub_mes_users
        WHERE user_code = :code
    """)
    with engine.connect() as conn:
        return conn.execute(sql, {"code": code}).fetchone()

def insert_record(data):
    # trasformazioni per DB
    data = data.copy()
    data["followed_cut_machine"] = 1 if data.get("followed_cut_machine") else 0
    data["quantity"] = data.get("quantity") or 0
    data["manual_deburring"] = data.get("manual_deburring") or 0
    data["manual_sorting"] = data.get("manual_sorting") or 0
    data["manual_waste"] = data.get("manual_waste") or 0

    sql = text("""
        INSERT INTO hub_mes_orders (
            date, operator_id, event_type, order_code, material,
            quantity, causale,
            manual_deburring, manual_sorting, manual_waste,
            followed_cut_machine,
            start_time, end_time
        ) VALUES (
            :date, :operator_id, :event_type, :order_code, :material,
            :quantity, :causale,
            :manual_deburring, :manual_sorting, :manual_waste,
            CAST(:followed_cut_machine AS BOOLEAN),
            :start_time, :end_time
        )
    """)

    try:
        with engine.begin() as conn:
            conn.execute(sql, data)
    except Exception as e:
        print("Errore insert_record:", e)
        raise


def get_history(code, start_date, end_date):
    sql = text("""
        SELECT h.id, h.date, h.event_type, h.order_code, h.material,
               h.quantity, h.causale,
               h.manual_deburring, h.manual_sorting, h.manual_waste,
               h.followed_cut_machine,
               h.start_time, h.end_time
        FROM hub_mes_orders h
        JOIN hub_mes_users u ON h.operator_id = u.id
        WHERE u.user_code = :code
          AND h.date BETWEEN :start AND :end
        ORDER BY h.date DESC, h.start_time DESC
    """)
    with engine.connect() as conn:
        return conn.execute(sql, {
            "code": code,
            "start": start_date,
            "end": end_date
        }).mappings().all()
