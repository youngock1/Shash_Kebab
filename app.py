import json
import os
from datetime import datetime
from functools import wraps
from flask import (
    Flask, render_template, request, jsonify,
    session, redirect, url_for
)


app = Flask(__name__)
app.secret_key = "Somethinginteresting"

DATA_FILE = "data.json"

# Логин и пароль администратора
ADMIN_LOGIN = "admin"
ADMIN_PASSWORD = "admin123"


with open('products.json', 'r', encoding='utf-8') as file:
    products = json.load(file)

categories = sorted({p["category"] for p in products})

data = {
    "orders": [],
    "shifts": [],
    "current_shift_id": None,
    "next_order_id": 1,
    "next_shift_id": 1,
}


def load_data():
    global data
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)


def save_data():
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


load_data()


# --- Декоратор авторизации ---
def login_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if not session.get("admin"):
            return redirect(url_for("admin_login"))
        return f(*args, **kwargs)
    return wrapper


@app.route("/")
def index():
    return render_template("index.html", products=products, categories=categories)


@app.route("/order", methods=["POST"])
def order():
    payload = request.get_json()
    customer = payload.get("customer", {})
    items = payload.get("items", [])

    if not items:
        return jsonify({"success": False, "message": "Пустой заказ"}), 400

    total = sum(item["price"] * item["qty"] for item in items)

    order = {
        "id": data["next_order_id"],
        "customer": customer,
        "items": items,
        "total": total,
        "status": "new",           # new | accepted | rejected | done
        "created_at": datetime.now().isoformat(timespec="seconds"),
        "shift_id": data["current_shift_id"],
    }
    data["orders"].append(order)
    data["next_order_id"] += 1
    save_data()

    return jsonify({
        "success": True,
        "message": f"Заказ №{order['id']} принят!",
        "order_id": order["id"],
    })


@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    error = None
    if request.method == "POST":
        login = request.form.get("login")
        password = request.form.get("password")
        if login == ADMIN_LOGIN and password == ADMIN_PASSWORD:
            session["admin"] = login
            return redirect(url_for("admin_panel"))
        error = "Неверный логин или пароль"
    return render_template("admin_login.html", error=error)


@app.route("/admin/logout")
def admin_logout():
    session.pop("admin", None)
    return redirect(url_for("admin_login"))


# --- Админ-панель ---

@app.route("/admin")
@login_required
def admin_panel():
    return render_template("admin.html", admin=session.get("admin"))


# --- API для админки ---

@app.route("/admin/api/state")
@login_required
def api_state():
    current_shift = None
    if data["current_shift_id"] is not None:
        current_shift = next(
            (s for s in data["shifts"] if s["id"] == data["current_shift_id"]),
            None
        )

    return jsonify({
        "orders": data["orders"],
        "shifts": data["shifts"],
        "current_shift": current_shift,
        "analytics": build_analytics(),
    })


@app.route("/admin/api/shift/open", methods=["POST"])
@login_required
def api_shift_open():
    if data["current_shift_id"] is not None:
        return jsonify({"success": False, "message": "Смена уже открыта"}), 400

    shift = {
        "id": data["next_shift_id"],
        "opened_at": datetime.now().isoformat(timespec="seconds"),
        "closed_at": None,
        "admin": session.get("admin"),
        "stats": None,
    }
    data["shifts"].append(shift)
    data["current_shift_id"] = shift["id"]
    data["next_shift_id"] += 1
    save_data()
    return jsonify({"success": True, "shift": shift})


@app.route("/admin/api/shift/close", methods=["POST"])
@login_required
def api_shift_close():
    if data["current_shift_id"] is None:
        return jsonify({"success": False, "message": "Нет открытой смены"}), 400

    shift = next(
        s for s in data["shifts"] if s["id"] == data["current_shift_id"]
    )
    shift["closed_at"] = datetime.now().isoformat(timespec="seconds")

    # Считаем статистику смены
    shift_orders = [o for o in data["orders"] if o["shift_id"] == shift["id"]]
    done_orders = [o for o in shift_orders if o["status"] == "done"]
    rejected_orders = [o for o in shift_orders if o["status"] == "rejected"]

    shift["stats"] = {
        "orders_total": len(shift_orders),
        "orders_done": len(done_orders),
        "orders_rejected": len(rejected_orders),
        "revenue": sum(o["total"] for o in done_orders),
    }

    data["current_shift_id"] = None
    save_data()
    return jsonify({"success": True, "shift": shift})


@app.route("/admin/api/order/<int:order_id>", methods=["POST"])
@login_required
def api_order_update(order_id):
    action = request.get_json().get("action")
    order = next((o for o in data["orders"] if o["id"] == order_id), None)
    if not order:
        return jsonify({"success": False, "message": "Заказ не найден"}), 404

    transitions = {
        "accept": ("new", "accepted"),
        "reject": ("new", "rejected"),
        "done": ("accepted", "done"),
    }
    if action not in transitions:
        return jsonify({"success": False, "message": "Неизвестное действие"}), 400

    from_status, to_status = transitions[action]
    if order["status"] != from_status:
        return jsonify({
            "success": False,
            "message": f"Нельзя выполнить: заказ в статусе '{order['status']}'"
        }), 400

    order["status"] = to_status
    save_data()
    return jsonify({"success": True, "order": order})


# --- Аналитика ---

def build_analytics():
    orders = data["orders"]
    done = [o for o in orders if o["status"] == "done"]
    rejected = [o for o in orders if o["status"] == "rejected"]
    new = [o for o in orders if o["status"] == "new"]
    accepted = [o for o in orders if o["status"] == "accepted"]

    revenue = sum(o["total"] for o in done)

    # Топ товаров
    product_stats = {}
    for o in done:
        for item in o["items"]:
            key = item["name"]
            if key not in product_stats:
                product_stats[key] = {"name": key, "qty": 0, "revenue": 0}
            product_stats[key]["qty"] += item["qty"]
            product_stats[key]["revenue"] += item["price"] * item["qty"]

    top_products = sorted(
        product_stats.values(), key=lambda x: x["revenue"], reverse=True
    )[:5]

    return {
        "total_orders": len(orders),
        "orders_new": len(new),
        "orders_accepted": len(accepted),
        "orders_done": len(done),
        "orders_rejected": len(rejected),
        "revenue": revenue,
        "avg_check": round(revenue / len(done), 2) if done else 0,
        "top_products": top_products,
    }


if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0')
