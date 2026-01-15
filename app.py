from flask import Flask, render_template, request, abort, redirect, url_for, session
import requests

app = Flask(__name__, template_folder="templates", static_folder='static')
app.secret_key = "secret123" 

# URL API Publik
API_URL = "https://fakestoreapi.com/products"

# =========================
# HOME (INDEX)
# =========================
@app.route('/')
def index():
    try:
        res_products = requests.get(API_URL)
        products = res_products.json()

        res_categories = requests.get(f"{API_URL}/categories")
        categories = res_categories.json()

        products_by_category = {}
        for cat in categories:
            products_by_category[cat] = [p for p in products if p['category'] == cat][:3]

        return render_template(
            'index.html',
            products_by_category=products_by_category
        )

    except Exception as e:
        return f"Terjadi kesalahan koneksi API: {e}"

# =========================
# KATALOG
# =========================
@app.route('/catalog')
def catalog():
    query = request.args.get('q')
    category = request.args.get('category')
    try:
        res_products = requests.get(API_URL)
        products = res_products.json()

        res_categories = requests.get(f"{API_URL}/categories")
        categories = res_categories.json()

        if category:
            products = [p for p in products if p['category'] == category]

        if query:
            products = [p for p in products if query.lower() in p['title'].lower()]

        return render_template(
            'catalog.html',
            products=products,
            categories=categories,
            query=query,
            selected_cat=category
        )

    except Exception as e:
        return f"Gagal memuat katalog: {e}"

# =========================
# DETAIL PRODUK
# =========================
@app.route('/product/<int:item_id>')
def detail(item_id):
    try:
        response = requests.get(f"{API_URL}/{item_id}")
        if response.status_code != 200:
            abort(404)
        return render_template('detail.html', product=response.json())
    except:
        abort(404)

# =========================
# DASHBOARD ANALISIS DATA
# =========================
@app.route('/dashboard')
def dashboard():
    try:
        response = requests.get(API_URL)
        products = response.json()

        total_produk = len(products)
        harga_rata_rata = sum(p['price'] for p in products) / total_produk
        produk_termahal = max(products, key=lambda x: x['price'])
        produk_termurah = min(products, key=lambda x: x['price'])

        kategori_counts = {}
        for p in products:
            cat = p['category']
            kategori_counts[cat] = kategori_counts.get(cat, 0) + 1

        return render_template(
            'dashboard.html',
            total=total_produk,
            avg=round(harga_rata_rata, 2),
            mahal=produk_termahal,
            murah=produk_termurah,
            kategori_stats=kategori_counts
        )
    except Exception as e:
        return f"Gagal memuat dashboard: {e}"

# =========================
# TAMBAH KE KERANJANG
# =========================
@app.route("/add_to_cart/<int:item_id>")
def add_to_cart(item_id):
    cart = session.get("cart", [])

    for item in cart:
        if item["id"] == item_id:
            item["quantity"] += 1
            session["cart"] = cart
            return redirect(request.referrer or url_for("index"))

    product = requests.get(f"{API_URL}/{item_id}").json()
    cart.append({
        "id": product["id"],
        "title": product["title"],
        "price": product["price"],
        "quantity": 1,
        "image": product["image"]
    })

    session["cart"] = cart
    return redirect(request.referrer or url_for("index"))

# =========================
# KERANJANG
# =========================
@app.route("/cart")
def cart():
    cart = session.get("cart", [])
    return render_template("cart.html", cart=cart, total=0)

# =========================
# HAPUS ITEM
# =========================
@app.route("/remove_from_cart/<int:item_id>")
def remove_from_cart(item_id):
    cart = [item for item in session.get("cart", []) if item["id"] != item_id]
    session["cart"] = cart
    return redirect(url_for("cart"))

# =========================
# TAMBAH / KURANG JUMLAH
# =========================
@app.route("/cart/increase/<int:item_id>")
def increase_cart(item_id):
    cart = session.get("cart", [])
    for item in cart:
        if item["id"] == item_id:
            item["quantity"] += 1
            break
    session["cart"] = cart
    return redirect(url_for("cart"))

@app.route("/cart/decrease/<int:item_id>")
def decrease_cart(item_id):
    cart = session.get("cart", [])
    for item in cart:
        if item["id"] == item_id:
            item["quantity"] -= 1
            if item["quantity"] <= 0:
                cart.remove(item)
            break
    session["cart"] = cart
    return redirect(url_for("cart"))

# =========================
# CHECKOUT
# =========================
@app.route("/checkout", methods=["POST"])
def checkout():
    selected_ids = request.form.getlist("selected_items")
    selected_ids = [int(i) for i in selected_ids]

    cart = session.get("cart", [])
    selected_items = [item for item in cart if item["id"] in selected_ids]

    if not selected_items:
        return redirect(url_for("cart"))

    total = sum(item["price"] * item["quantity"] for item in selected_items)

    return render_template(
        "checkout.html",
        items=selected_items,
        total=total
    )

# =========================
# FAQ
# =========================
@app.route("/faq")
def faq():
    return render_template("faq.html")

# =========================
# ABOUT
# =========================
@app.route('/about')
def about():
    kelompok = [
        {"nama": "Galang Sopyan", "nim": "312410046", "foto": "IMG-20250113-WA0001_1_.jpg"},
        {"nama": "ADE TEGUH ARDIANSYAH", "nim": "312410014",  "foto": "1715320189513.jpg"},
        {"nama": "MUHAMMAD RIZKI", "nim": "312410039",  "foto": "IMG20240303150826.jpg"},
        {"nama": "FAKHRUL MUDZAKKIR SHIDDIQ", "nim": "312410041", "foto": "pasfotopb.png"},
        {"nama": "FASYAL MUHAMMAD", "nim": "312410023", "foto": "0B2C35D5-AADA-400F-9646-55D0730548CD.jpeg"}, ]

    return render_template('about.html', anggota=kelompok)

# =========================
# RUN APP
# =========================
if __name__ == '__main__':
    app.run(debug=True)
