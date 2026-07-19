from flask import Flask, render_template, request, jsonify, make_response
import json

app = Flask(__name__)

# Global product storage (clears automatically on server restart for clean testing!)
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

# --- SECURE SESSIONLESS LOGIN API ---
# Keeps logins completely isolated to each individual phone's browser!
@app.route('/api/buyer_login', methods=['POST'])
def buyer_login():
    data = request.json
    username = data.get('username', '').strip()
    phone = data.get('phone', '').strip()
    
    if not username or not phone:
        return jsonify({"status": "error", "message": "Missing username or phone"}), 400
        
    # Return success directly. The front-end will securely store this profile locally in the browser!
    return jsonify({
        "status": "success", 
        "user": {
            "username": username,
            "phone": phone
        }
    })

# --- GLOBAL LIVE PRODUCT STREAM API ---
@app.route('/api/sync_product', methods=['POST'])
def sync_product():
    data = request.json
    p_id = data.get('id')
    artisan = data.get('artisan')
    material = data.get('material')
    hours = data.get('hours')
    price = data.get('price')
    img_base64 = data.get('img')

    if not all([p_id, artisan, material, hours, price, img_base64]):
        return jsonify({"status": "error", "message": "All product fields are mandatory"}), 400

    # Build the product registry payload
    PRODUCTS_STREAM[p_id] = {
        "id": p_id,
        "artisan": artisan,
        "material": material,
        "hours": hours,
        "price": float(price),
        "img": img_base64,
        "stock": 5  # Freshly registered items start with a default demo stock of 5
    }

    # Generate the direct query parameters that the buyer kiosk can read instantly via QR scan
    qr_payload = f"https://karigarsync.onrender.com/buyer?scan_id={p_id}"

    return jsonify({
        "status": "success",
        "message": "Product stream synced to cloud marketplace",
        "qr_data": qr_payload
    })

@app.route('/api/get_products', methods=['GET'])
def get_products():
    # Send out the dictionary items as a flat list for the storefront grid
    return jsonify(list(PRODUCTS_STREAM.values()))

if __name__ == '__main__':
    app.run(debug=True)
