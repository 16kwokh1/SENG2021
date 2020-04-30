from flask import Flask, render_template, request
from backend.api import search_woolworths, search_coles
from backend.testdata import coles_oranges, woolies_oranges, coles_salmon, woolies_salmon, coles_apples, woolies_apples
from wtforms import Form, StringField

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    search = ProductSearchForm(request.form)
    if request.method == 'POST':
        return search_results(search)
    return render_template('home.html', form=search)

@app.route('/About')
def about():
    return render_template('about.html', title='About')


@app.route('/results', methods=['GET','POST'])
def search_results(search):

    if search.data['search'].strip() == '':
        results_coles = []
        results_woolies = []
    else:
        
        results_coles = search_coles(search.data['search'])
        results_woolies = search_woolworths(search.data['search'])

        if len(results_coles) > len(results_woolies):
            extra = len(results_coles)-len(results_woolies)
            for i in range(extra):
                results_woolies.append({})

        if len(results_woolies) > len(results_coles):
            extra = len(results_woolies)-len(results_coles)
            for i in range(extra):
                results_coles.append({})

    return render_template('results.html', product_coles=results_coles, product_woolies=results_woolies, search_term=search.data['search'].upper(), title=search.data['search'])

class ProductSearchForm(Form):
    search = StringField('')

cart_current_coles = []
cart_current_woolies = []

@app.route('/add_cart', methods=['POST'])
def carts_add():
    data = request.get_json()
    if data['shop'] == 'addtocart-woolies':
        cart_current_woolies.append(data)
        #print('this is from woolies')
    if data['shop'] == 'addtocart-coles':
        #print('this is from coles')
        cart_current_coles.append(data)
    return render_template('cart.html', product_coles=cart_current_coles, product_woolies=cart_current_woolies)

@app.route('/remove_cart', methods=['POST', 'GET'])
def carts_remove():
    data = request.get_json()

    if data['shop'] == 'addtocart-woolies':
        for i in cart_current_woolies:
            if data['name'] == i['name']:
                cart_current_woolies.remove(i)
                break
    if data['shop'] == 'addtocart-coles':
        for i in cart_current_coles:
            if data['name'] == i['name']:
                cart_current_coles.remove(i)
                break
    return carts()

@app.route('/cart', methods=['GET'])
def carts():
    #print(cart_current_coles)
    #print(cart_current_woolies)

    total=0

    for i in cart_current_coles:
        total += float(i['price'].split()[0].replace('$',''))
    for i in cart_current_woolies:
        total += float(i['price'].replace('$',''))

    return render_template('cart.html', product_coles=cart_current_coles, product_woolies=cart_current_woolies, total=round(total, 2))

if __name__ == "__main__":
    app.run(debug=True)