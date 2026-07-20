from flask import Flask, render_template, request, jsonify
import json

app = Flask(__name__)

# Core product memory storage
PRODUCTS_STREAM = {}

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/artisan')
def artisan_studio():
    return render_template('artisan.html')

@app.route('/buyer')
def buyer_marketplace():
    return render_template('buyer.html')

@app.route('/api/buyer_login', methods=['POST'])
def buyer_login():
    data = request.json
    username = data.get('username', '').strip()
    phone = data.get('phone', '').strip()
    
    if not username or not phone:
        return jsonify({"status": "error", "message": "Missing fields"}), 400
        
    return jsonify({"status": "success", "user": {"username": username, "phone": phone}})

@app.route('/api/sync_product', methods=['POST'])
def sync_product():
    data = request.json
    p_id = data.get('id')
    p_name = data.get('name')
    p_desc = data.get('desc')
    artisan = data.get('artisan')
    material = data.get('material')
    hours = data.get('hours')
    price = data.get('price')
    img_base64 = data.get('img')

    if not all([p_id, p_name, p_desc, artisan, material, hours, price, img_base64]):
        return jsonify({"status": "error", "message": "All fields are required"}), 400

    PRODUCTS_STREAM[p_id] = {
        "id": p_id,
        "name": p_name,
        "desc": p_desc,
        "artisan": artisan,
        "material": material,
        "hours": hours,
        "price": float(price),
        "img": img_base64,
        "stock": 5,
        "reviews": [
            {"user": "Amit Kumar", "rating": 5, "comment": "Beautiful design! Quality is excellent."},
            {"user": "Neha Sharma", "rating": 4, "comment": "Very neat handiwork, highly recommended."}
        ]
    }

    qr_payload = f"https://karigarsync.onrender.com/buyer?scan_id={p_id}"

    return jsonify({
        "status": "success",
        "qr_data": qr_payload
    })

@app.route('/api/get_products', methods=['GET'])
def get_products():
    return jsonify(list(PRODUCTS_STREAM.values()))

if __name__ == '__main__':
    app.run(debug=True)
