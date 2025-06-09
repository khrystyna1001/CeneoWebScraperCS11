import os
import json
from app import app
from flask import render_template, redirect, url_for, request
from app.forms import ExtractForm
from app.models import Product

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/extract")
def render_form():
    form = ExtractForm()
    return render_template("extract.html", form=form)

@app.route("/extract", methods=['POST'])
def extract():
    form = ExtractForm(request.form)
    if form.validate():
        product_id = form.product_id.data
        product = Product(product_id)
        if product.extract_name():
            product.extract_opinions()
            product.analyze()
            product.export_info()
            product.export_opinions()
            return redirect(url_for('product', product_id=product_id))
        form.product_id.errors.append('There is no product for provided id or product has no opinions')
        return render_template('extract.html', form=form)
    return render_template('extract.html', form=form)

@app.route("/products")
def products():
    products_list = []
    products_dir = "./app/data/products"
    if os.path.exists(products_dir):
        for filename in os.listdir(products_dir):
            if filename.endswith(".json"):
                product_id = filename.replace(".json", "")
                product_filepath = os.path.join(products_dir, filename)
                try:
                    with open(product_filepath, "r", encoding="UTF-8") as f:
                        product_data = json.load(f)
                        products_list.append({
                            'product_id': product_data.get('product_id'),
                            'product_name': product_data.get('product_name')
                        })
                except Exception as e:
                    print(f"Error reading prodcut file {filename}: {e}")
    return render_template("products.html", products=products_list)

@app.route("/product/<product_id>")
def product(product_id):
    product = Product(product_id)
    try:
        product.import_info()
        product.import_opinions()
    except FileNotFoundError:
        return "Product data not found.", 404
    except Exception as e:
        return f"An error occurred: {e}", 500

    return render_template("product.html", product=product)

@app.route("/about")
def about():
    return render_template("about.html")