from flask import Flask, render_template, request, jsonify
import socket

app = Flask(__name__)

database = {}
buyer_profiles = {
    "active_user": None,
    "cart": [],
    "orders": []
}

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/artisan')
def artisan():
    return render_template('artisan.html')

@app.route('/buyer')
def buyer():
    return render_template('buyer.html')

@app.route('/buyer-login', methods=['POST'])
def buyer_login():
    data = request.json
    username = data.get('username', '').strip()
    if not username:
        return jsonify({"status": "error", "message": "Username required"})
    
    buyer_profiles["active_user"] = {
        "username": username,
        "wallet": 1500,
        "joined": "2026"
    }
    return jsonify({"status": "success", "profile": buyer_profiles["active_user"]})

@app.route('/buyer-logout', methods=['POST'])
def buyer_logout():
    buyer_profiles["active_user"] = None
    buyer_profiles["cart"] = []
    return jsonify({"status": "success"})

@app.route('/get-active-buyer')
def get_active_buyer():
    return jsonify({"user": buyer_profiles["active_user"]})

@app.route('/next-id')
def get_next_id():
    next_number = len(database) + 1
    hostname = socket.gethostname()
    try:
        ip_address = socket.gethostbyname(hostname)
    except:
        ip_address = "127.0.0.1"
    return jsonify({
        "nextId": f"item_{next_number:03d}",
        "ipAddress": ip_address
    })

@app.route('/upload', methods=['POST'])
def upload_product():
    data = request.json
    item_id = data.get('itemId')
    
    database[item_id] = {
        "name": data.get('artisanName'),
        "material": data.get('material'),
        "hours": data.get('hoursSpent'),
        "stock": int(data.get('stockCount', 1)),
        "price": data.get('finalPrice'),
        "story": data.get('story'),
        "image": data.get('image')
    }
    return jsonify({"status": "success", "message": "Product synced!"})

@app.route('/purchase-item', methods=['POST'])
def purchase_item():
    data = request.json
    item_id = data.get('itemId')
    if item_id in database and database[item_id]["stock"] > 0:
        database[item_id]["stock"] -= 1
        return jsonify({"status": "success", "newStock": database[item_id]["stock"]})
    return jsonify({"status": "error", "message": "Out of stock"})

@app.route('/all-products')
def get_all_products():
    return jsonify(database)

# DYNAMIC QR SCAN TARGET VIEW (With New Fixed Navigation Buttons)
@app.route('/product/<item_id>')
def view_product(item_id):
    product = database.get(item_id)
    if product:
        status_msg = f"Available Stock: {product['stock']}" if product['stock'] > 0 else "🔒 OUT OF STOCK"
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>KarigarSync - Product Origin</title>
            <style>
                body {{ font-family: sans-serif; background: #1a252f; color: white; text-align: center; padding: 20px; margin-bottom: 90px; }}
                .card {{ background: rgba(255,255,255,0.1); padding: 20px; border-radius: 15px; max-width: 400px; margin: 0 auto; box-shadow: 0 4px 15px rgba(0,0,0,0.3); }}
                img {{ width: 100%; border-radius: 10px; margin-top: 15px; display: { 'block' if product['image'] else 'none' }; }}
                .price {{ font-size: 1.8rem; color: #27ae60; font-weight: bold; margin: 15px 0; }}
                .badge {{ background: #e05a47; padding: 4px 10px; border-radius: 10px; display: inline-block; font-size: 0.8rem; }}
                
                /* Responsive Fixed Bottom Dock Layout */
                .nav-bar {{
                    position: fixed;
                    bottom: 0;
                    left: 0;
                    width: 100%;
                    background: #2c3e50;
                    padding: 15px 0;
                    display: flex;
                    justify-content: center;
                    gap: 15px;
                    border-top: 2px solid #ffe259;
                    box-shadow: 0 -4px 10px rgba(0,0,0,0.3);
                    z-index: 999;
                }}
                .nav-link {{
                    background: #e05a47;
                    color: white;
                    text-decoration: none;
                    padding: 12px 20px;
                    border-radius: 8px;
                    font-weight: bold;
                    font-size: 1rem;
                    box-shadow: 0 2px 5px rgba(0,0,0,0.2);
                }}
                .nav-link.market-style {{ background: #27ae60; }}
            </style>
        </head>
        <body>
            <div class="card">
                <div class="badge">{item_id}</div>
                <h2>{product['name']}'s Craft</h2>
                <hr style="opacity:0.2;">
                <p><b>Material:</b> {product['material']}</p>
                <p><b>Status:</b> {status_msg}</p>
                <p style="text-align:left; background:rgba(0,0,0,0.2); padding:10px; border-radius:8px;">"{product['story']}"</p>
                { f'<img src="{product["image"]}" alt="Craft Photo">' if product['image'] else '' }
                <div class="price">₹{product['price']}</div>
            </div>

            <!-- FIXED PHONE MOBILE CONTROL BAR INTERFACE -->
            <div class="nav-bar">
                <a href="/" class="nav-link">🏠 Home Gateway</a>
                <a href="/buyer" class="nav-link market-style">🛒 Marketplace</a>
            </div>
        </body>
        </html>
        """
    return "<h1>Product Not Found</h1>", 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)