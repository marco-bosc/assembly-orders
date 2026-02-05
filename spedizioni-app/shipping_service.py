
# shipping_service.py
from typing import Optional, Dict
from db import get_connection
import sqlite3

def save_shipment(ddt: str, tracking: str, courier: Optional[str] = None) -> Dict:
    """
    Inserisce una spedizione in SQLite e ritorna il record inserito.
    """
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO shipments (ddt, tracking, courier)
            VALUES (?, ?, ?)
        """, (ddt, tracking, courier))
        new_id = cur.lastrowid

        cur.execute("""
            SELECT id, ddt, tracking, courier, created_at
            FROM shipments
            WHERE id = ?
        """, (new_id,))
        row = cur.fetchone()
        return dict(row) if row else {"id": new_id, "ddt": ddt, "tracking": tracking, "courier": courier}
    finally:
        conn.commit()
        conn.close()

def delete_last() -> bool:
    """
    Soft-delete: marca come eliminata l'ultima spedizione non eliminata.
    """
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("""
            SELECT id
            FROM shipments
            WHERE is_deleted = 0
            ORDER BY created_at DESC, id DESC
            LIMIT 1
        """)
        row = cur.fetchone()
        if not row:
            return False
        last_id = row["id"]
        cur.execute("""
            UPDATE shipments
            SET is_deleted = 1,
                deleted_at = CURRENT_TIMESTAMP
            WHERE id = ?
        """, (last_id,))
        return cur.rowcount > 0
    finally:
        conn.commit()
        conn.close()

def get_last() -> Optional[Dict]:
    """
    Ritorna l'ultima spedizione NON eliminata.
    """
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("""
            SELECT id, ddt, tracking, courier, created_at
            FROM shipments
            WHERE is_deleted = 0
            ORDER BY created_at DESC, id DESC
            LIMIT 1
        """)
        row = cur.fetchone()
        return dict(row) if row else None
    finally:
        conn.close()

def print_label(parcel_id: str) -> Dict:
    """
    Registra SEMPRE una scansione (printed_scans).
    Se il parcel era già presente in printed_labels, ritorna already_printed=True.
    Altrimenti inserisce in printed_labels e ritorna already_printed=False.
    """
    conn = get_connection()
    try:
        cur = conn.cursor()

        # Log: salva SEMPRE la scansione
        cur.execute("""
            INSERT INTO printed_scans (parcel_id)
            VALUES (?)
        """, (parcel_id,))

        # Verifica se è già stato stampato prima
        cur.execute("SELECT 1 FROM printed_labels WHERE parcel_id = ?", (parcel_id,))
        already = cur.fetchone() is not None

        if not already:
            try:
                cur.execute("""
                    INSERT INTO printed_labels (parcel_id)
                    VALUES (?)
                """, (parcel_id,))
            except sqlite3.IntegrityError:
                # Race condition: un altro processo ha inserito nel frattempo
                already = True

        return {"already_printed": already}
    finally:
        conn.commit()
        conn.close()
