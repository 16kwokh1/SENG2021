def woolworths_search(searchParams):
    search = ""

    search.join(searchParams)

    response = requests.get("developer.woolworths.com.au/content/woolworths-supermarkets.supermarket-search.json", params=parameters)
    data = response.json()

    return data

def coles_search(searchParams):
    search = ""

    search.join(searchParams)

    response = requests.get("api.coles.come.au/home/api/products/item-search.json", params=parameters)
    data = response.json()

    return data
    

def data_parse(data){

    parsed = []

    for product in data:
        item = {}
        item[name] = product[name]
        item[price] = product[price]
        item[amount] = product[amount]
        item[discount] = product[discount]
        parsed.append(product)

    return data

}