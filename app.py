from flask import Flask, render_template, request, abort
import requests

app = Flask(__name__)

# URL API Publik sesuai instruksi UAS
API_URL = "https://fakestoreapi.com/products"

@app.route('/')
def index():
    query = request.args.get('q')
    category = request.args.get('category')
    try:
        # Ambil data produk dan kategori secara paralel
        res_prods = requests.get(API_URL)
        products = res_prods.json()
        
        res_cats = requests.get(f"{API_URL}/categories")
        categories = res_cats.json()
        
        # Logika Filter Kategori
        if category:
            products = [p for p in products if p['category'] == category]
            
        # Logika Pencarian
        if query:
            products = [p for p in products if query.lower() in p['title'].lower()]
            
        return render_template('index.html', products=products, categories=categories, query=query, selected_cat=category)
    except Exception as e:
        return f"Terjadi kesalahan koneksi API: {e}"

@app.route('/product/<int:item_id>')
def detail(item_id):
    try:
        response = requests.get(f"{API_URL}/{item_id}")
        if response.status_code != 200:
            abort(404)
        return render_template('detail.html', product=response.json())
    except:
        abort(404)

@app.route('/dashboard')
def dashboard():
    try:
        response = requests.get(API_URL)
        products = response.json()
        
        # Pengolahan Data Statistik (Analisis Python)
        total_produk = len(products)
        harga_rata_rata = sum(p['price'] for p in products) / total_produk
        produk_termahal = max(products, key=lambda x: x['price'])
        produk_termurah = min(products, key=lambda x: x['price'])
        
        kategori_counts = {}
        for p in products:
            cat = p['category']
            kategori_counts[cat] = kategori_counts.get(cat, 0) + 1
            
        return render_template('dashboard.html', total=total_produk, avg=round(harga_rata_rata, 2),
                               mahal=produk_termahal, murah=produk_termurah, kategori_stats=kategori_counts)
    except Exception as e:
        return f"Gagal memuat dashboard: {e}"

@app.route('/about')
def about():
    # Sesuaikan dengan data kelompok Anda
    kelompok = [
        {"nama": "Galang Sopyan", "nim": "312410046", "peran": "Frontend Developer"},
        {"nama": "ADE TEGUH ARDIANSYAH ", "nim": "312410014", "peran": "Backend Developer"},
        {"nama": "MUHAMMAD RIZKI", "nim": "312410039", "peran": "UI/UX Designer"},
        {"nama": "FAKHRUL MUDZAKKIR SHIDDIQ", "nim": "312410041", "peran": "Dokumentasi"},
        {"nama": "FASYAL MUHAMMAD", "nim": "312410023", "peran": "UI/UX Designer"},
    ]
    return render_template('about.html', anggota=kelompok)

if __name__ == '__main__':
    app.run(debug=True)