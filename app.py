from flask import Flask, render_template, request, jsonify
import json


app = Flask(__name__)

with open('products.json', 'r', encoding='utf-8') as file:
    products = json.load(file)

categories = sorted({p["category"] for p in products})


@app.route("/")
def index():
    return render_template("index.html", products=products, categories=categories)


@app.route("/order", methods=["POST"])
def order():
    data = request.get_json()
    customer = data.get("customer", {})
    items = data.get("items", [])

    # Здесь можно сохранить заказ в файл или базу данных.
    # Для простоты просто выводим в консоль.
    print("=== Новый заказ ===")
    print("Имя:", customer.get("name"))
    print("Телефон:", customer.get("phone"))
    print("Адрес:", customer.get("address"))
    print("Комментарий:", customer.get("comment"))
    for item in items:
        print(f"  - {item['name']} x{item['qty']} = {item['price'] * item['qty']} ₽")
    total = sum(item["price"] * item["qty"] for item in items)
    print("Итого:", total, "₽")
    print("===================")

    return jsonify({"success": True, "message": "Заказ принят!"})


if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0')
