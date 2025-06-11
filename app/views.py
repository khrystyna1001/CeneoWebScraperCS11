import os
import io
import json
from app import app
from flask import render_template, redirect, url_for, request, send_file, send_from_directory
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
            product.make_charts()
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
                            'product_name': product_data.get('product_name'),
                            'stats': product_data.get('stats', {})
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

@app.route("/product/<product_id>/tocsv")
def tocsv(product_id):
    product = Product(product_id)
    try:
        product.import_opinions() 
        csv_data = product.to_csv()
        buffer = io.BytesIO()
        buffer.write(csv_data.encode('utf-8'))
        buffer.seek(0)
        return send_file(buffer,
                         mimetype='text/csv',
                         as_attachment=True,
                         download_name=f"{product_id}_opinions.csv")
    except FileNotFoundError:
            return "Opinions data not found for this product.", 404
    except Exception as e:
        return f"An error occurred while generating CSV: {e}", 500

@app.route("/product/<product_id>/tojson")
def tojson(product_id):
    product = Product(product_id)
    try:
        product.import_opinions() 
        json_data = product.to_json()
        buffer = io.BytesIO()
        buffer.write(json_data.encode('utf-8'))
        buffer.seek(0)
        return send_file(buffer,
                         mimetype='application/json',
                         as_attachment=True,
                         download_name=f"{product_id}_opinions.json")
    except FileNotFoundError:
            return "Opinions data not found for this product.", 404
    except Exception as e:
        return f"An error occurred while generating JSON: {e}", 500

@app.route("/product/<product_id>/toexcel")
def toexcel(product_id):
    product = Product(product_id)
    try:
        product.import_opinions() 
        excel_data = product.to_excel()
        return send_file(excel_data,
                         mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                         as_attachment=True,
                         download_name=f"{product_id}_opinions.xlsx")
    except FileNotFoundError:
            return "Opinions data not found for this product.", 404
    except Exception as e:
        return f"An error occurred while generating EXCEL: {e}", 500

@app.route("/charts/pie/<product_id>")
def view_pie_chart(product_id):
    pie_chart_dir = os.path.join(app.root_path, "data", "pie_chart")
    filename = f"{product_id}.png"
    try:
        return send_from_directory(pie_chart_dir, filename)
    except Exception as e:
        return f"Error serving pie chart: {e}"

@app.route("/charts/bar/<product_id>")
def view_bar_chart(product_id):
    bar_chart_dir = os.path.join(app.root_path, "data", "bar_chart")
    filename = f"{product_id}.png"
    try:
        return send_from_directory(bar_chart_dir, filename)
    except Exception as e:
        return f"Error serving bar chart: {e}"

@app.route("/charts/<product_id>/view")
def view_charts(product_id):
    product = Product(product_id)
    try:
        product.import_info()
    except FileNotFoundError:
        flash("Product data not found for charts.", "error")
        return redirect(url_for('products')) 
    except Exception as e:
        flash(f"An error occurred while preparing charts: {e}", "error")
        return redirect(url_for('product', product_id=product_id))

    return render_template('chart.html', product=product)