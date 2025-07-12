import requests
from shop.scripts.loader import cb_token
import sqlite3


API_URL = "https://pay.crypt.bot/api"

def save_invoice(invoice_id: str, user_id: str, amount: float):
    conn = sqlite3.connect("shop.db")
    cursor = conn.cursor()
    cursor.execute("""
        INSERT OR REPLACE INTO invoices (invoice_id, user_id, amount, status)
        VALUES (?, ?, ?, 'pending')
    """, (invoice_id, user_id, amount))
    conn.commit()
    conn.close()

    
def create_invoice(amount: float, currency: str = "USDT", description: str = "Top up", payload: str = "") -> str:
    url = f"{API_URL}/createInvoice"
    headers = {
        "Crypto-Pay-API-Token": cb_token,
        "Content-Type": "application/json"
    }
    data = {
        "asset": currency,
        "amount": amount,
        "description": description,
        "hidden_message": "💸 Thank you for your payment!",
        "paid_btn_name": "openBot",
        "paid_btn_url": "https://t.me/example_shablon_bot",  # CHANGE TO YOUR URL
        "payload": payload
    }

    response = requests.post(url, json=data, headers=headers)
    if response.status_code == 200:
        result = response.json()["result"]
        invoice_id = result["invoice_id"]
        pay_url = result["pay_url"]
        save_invoice(invoice_id, payload, amount)
        return pay_url
    else:
        print(response.text)
        return None

def check_crypto_payment(user_id: int) -> float:
    conn = sqlite3.connect("shop.db")
    cursor = conn.cursor()
    cursor.execute("SELECT invoice_id, amount FROM invoices WHERE user_id=? AND status='pending'", (user_id,))
    invoices = cursor.fetchall()
    conn.close()

    if not invoices:
        return 0.0

    headers = {
        "Crypto-Pay-API-Token": cb_token
    }

    try:
        response = requests.get(f"{API_URL}/getInvoices", headers=headers)
        response.raise_for_status()
        remote_invoices = response.json()["result"]["items"]
    except Exception as e:
        print("🌐 Ошибка при получении счетов:", e)
        return 0.0

    print(f"🧾 Локальные счета в БД: {invoices}")
    print("🌐 Ответ от CryptoBot:", response.json())

    for local_id, amount in invoices:
        for invoice in remote_invoices:
            if (
                str(invoice["invoice_id"]) == str(local_id)
                and invoice["status"] == "paid"
            ):
                print(f"✅ Найден оплаченный счёт {local_id} на сумму {amount} USD для user_id {user_id}")
                mark_invoice_paid(local_id)
                return amount  # ✅ Возврат только одного подтверждённого счёта

    return 0.0

def mark_invoice_paid(invoice_id: str):
    conn = sqlite3.connect("shop.db")
    cursor = conn.cursor()
    cursor.execute("UPDATE invoices SET status='paid' WHERE invoice_id=?", (invoice_id,))
    conn.commit()
    conn.close()
