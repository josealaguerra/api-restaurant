import flask
from flask import request, jsonify, Blueprint
import pyodbc


api_v1_bp = Blueprint('api_v1', __name__,url_prefix='/api/v1')
api_v2_bp = Blueprint('api_v2', __name__,url_prefix='/api/v2')




# Create some test data for our catalog in the form of a list of dictionaries.
category = [
    {'id': 0,
     'name': 'Combos'},
    {'id': 1,
     'name': 'Bebidas'},
    {'id': 2,
     'name': 'Postres'}
]




# Create some test data for our catalog in the form of a list of dictionaries.
product = [
    {'id': 0,
     'name': 'Combos',
     'price': 57.60,
     'quantity': 150,
     'description': 'Combo 1: Pollo frito con papas y gaseosa',
     'idCategory': 1,
     'available': 'S',
     'url_imagen': 'PolloFrito.jpg'},
    {'id': 1,
     'name': 'Bebidas',
     'price': 57.60,
     'quantity': 150,
     'description': 'Combo 2: Hamburguesa con papas y gaseosa',
     'idCategory': 1,
     'available': 'S',
     'url_imagen': 'Hamburguer.jpg'},
    {'id': 2,
     'name': 'Lata Gaseosa Coca-cola original',
     'price': 8.00,
     'quantity': 300,
     'description': 'Gaseosa Coca-cola original',
     'idCategory': 1,
     'available': 'S',
     'url_imagen': 'Cocacola.jpg'}
]



@api_v1_bp.route('/', methods=['GET'])
def home_v1():
    return '''<h1>API categoria V1</h1>
<p>Un prototipo de un API para el proyecto de ingenieria de software V1.</p>'''


@api_v1_bp.route('/resources/category/all', methods=['GET'])
def api_all_category_v1():
    return jsonify(category)


@api_v1_bp.route('/resources/product/all', methods=['GET'])
def api_all_product_v1():
    return jsonify(product)



def get_db_connection():
   # Conexión a la base de datos de SQL Server
    server = 'familyWarTun'
    database = 'restaurant'
    username = 'sa'
    password = 'Guate.2023'
    driver = '{ODBC Driver 17 for SQL Server}'
    return pyodbc.connect(f'DRIVER={driver};SERVER={server};DATABASE={database};UID={username};PWD={password}')



@api_v2_bp.route('/', methods=['GET'])
def home_v2():
    return '''<h1>API categoria V2</h1>
<p>Un prototipo de un API para el proyecto de ingenieria de software V2.</p>'''



@api_v2_bp.route('/resources/product/all', methods=['GET'])
def api_get_all_products_v2():

    cnxn = get_db_connection()

    # Consulta SQL para obtener todos los productos
    cursor = cnxn.cursor()
    cursor.execute('''SELECT P.ID_PRODUCT, P.NAME_PRODUCT, P.PRICE, P.QUANTITY, P.DESCRIPTION, C.NAME_CATEGORY AS NAME_CATEGORY, 
                        CASE WHEN AVAILABLE='0' THEN 'No disponible' ELSE 'Disponible' END AS AVAILABLE, URL_IMAGEN FROM PRODUCT P 
                        JOIN CATEGORY C ON C.ID_CATEGORY=P.ID_CATEGORY''')
    productos = cursor.fetchall()

    # Lista de diccionarios con la información de cada producto
    productos_list = []
    for producto in productos:
        producto_dict = {'ID_PRODUCT': producto[0], 'NAME_PRODUCT': producto[1], 
                            'PRICE': producto[2], 'QUANTITY': producto[3], 
                            'DESCRIPTION': producto[4], 'NAME_CATEGORY': producto[5], 
                            'AVAILABLE': producto[6], 'URL_IMAGEN': producto[7]}
        productos_list.append(producto_dict)

    # Objeto JSON con la lista de productos
    productos_json = jsonify(productos_list)

    # return jsonify(category)
    return productos_json;





@api_v1_bp.route('/resources/product', methods=['POST'])
def api_create_products_v1():
    # Check if an ID was provided as part of the URL.
    # If ID is provided, assign it to a variable.
    # If no ID is provided, display an error in the browser.
    if 'NAME_CATEGORY' in request.args:
        id = int(request.args['NAME_CATEGORY'])
    else:
        return "Error: No id field provided. Please specify an id."

    # Create an empty list for our results
    results = []

    return jsonify({'message': 'Categoria creada exitosamente!'})



@api_v2_bp.route('/resources/product', methods=['POST'])
def api_create_products_v2():
    conn = get_db_connection()
    cursor = conn.cursor()
    data = request.get_json()

    cursor.execute('''INSERT INTO product (NAME_PRODUCT, PRICE, QUANTITY, DESCRIPTION, ID_CATEGORY, AVAILABLE, URL_IMAGEN) VALUES 
                    (?, ?, ?, ?, ?, ?, ?)''',
                   (data['NAME_PRODUCT'], data['PRICE'], data['QUANTITY'], data['DESCRIPTION'], 
                    data['ID_CATEGORY'], data['AVAILABLE'], data['URL_IMAGEN']))
    conn.commit()

    return jsonify({'message': 'Producto creado exitosamente!'})









# Endpoint para recuperar y actualizar un producto
@api_v2_bp.route('/resources/product/<int:product_id>', methods=['GET', 'PUT'])
def api_update_product_v2(product_id):
    # Conectar a la base de datos
    conn = get_db_connection()

    if request.method == 'GET':
        # Recuperar el producto de la base de datos
        cursor = conn.cursor()
        cursor.execute('''SELECT P.ID_PRODUCT, P.NAME_PRODUCT, P.PRICE, P.QUANTITY, P.DESCRIPTION, C.NAME_CATEGORY AS NAME_CATEGORY, 
                        CASE WHEN AVAILABLE='0' THEN 'NO DISPONIBLE' ELSE 'DISPONIBLE' END AS AVAILABLE, URL_IMAGEN FROM PRODUCT P 
                        JOIN CATEGORY C ON C.ID_CATEGORY=P.ID_CATEGORY WHERE id_product = {product_id}''')
        producto = cursor.fetchone()

        if producto is None:
            # Devolver un error si el producto no existe
            return jsonify({'error': 'Producto no existe'}), 404

        # Devolver los datos del producto en el cuerpo de la respuesta
        return jsonify({'product': {'ID_PRODUCT': producto[0], 'NAME_PRODUCT': producto[1], 
                            'PRICE': producto[2], 'QUANTITY': producto[3], 
                            'DESCRIPTION': producto[4], 'NAME_CATEGORY': producto[5], 
                            'AVAILABLE': producto[6], 'URL_IMAGEN': producto[7]}}), 200

    elif request.method == 'PUT':
        # Obtener los datos actualizados del producto del cuerpo de la solicitud
        data = request.json

        # Actualizar los datos del producto en la base de datos
        cursor = conn.cursor()
        cursor.execute("""UPDATE products 
                            SET NAME_PRODUCT = '{data['NAME_PRODUCT']}', PRICE = {data['PRICE']}, 
                            QUANTITY = '{data['QUANTITY']}', DESCRIPTION = {data['DESCRIPTION']}, 
                            ID_CATEGORY = '{data['ID_CATEGORY']}', AVAILABLE = '{data['AVAILABLE']}', 
                            URL_IMAGEN = {data['URL_IMAGEN']}
                            WHERE ID_PRODUCT = {product_id}""")
        conn.commit()

        # Devolver los datos actualizados del producto en el cuerpo de la respuesta
        return jsonify({'product': {'id': product_id, 'NAME_PRODUCT': data['NAME_PRODUCT'], 
                            'PRICE': data['PRICE'], 'QUANTITY': data['QUANTITY'], 
                            'DESCRIPTION': data['DESCRIPTION'], 'NAME_CATEGORY': data['NAME_CATEGORY'], 
                            'AVAILABLE': data['AVAILABLE'], 'URL_IMAGEN': data['URL_IMAGEN']}}), 200




@api_v2_bp.route('/resources/category/all', methods=['GET'])
def api_all_category_v2():

    cnxn = get_db_connection()

    # Consulta SQL para obtener todas las categorias
    cursor = cnxn.cursor()
    cursor.execute('SELECT ID_CATEGORY, NAME_CATEGORY FROM category')
    categories = cursor.fetchall()

    # Lista de diccionarios con la información de cada producto
    categories_list = []
    for categoryItem in categories:
        producto_dict = {'ID_CATEGORY': categoryItem[0], 'NAME_CATEGORY': categoryItem[1]}
        categories_list.append(producto_dict)

    # Objeto JSON con la lista de categories
    categories_json = jsonify(categories_list)

    # return jsonify(category)
    return categories_json;






@api_v1_bp.route('/resources/categories', methods=['POST'])
def api_create_categories_v1():
    # Check if an ID was provided as part of the URL.
    # If ID is provided, assign it to a variable.
    # If no ID is provided, display an error in the browser.
    if 'NAME_CATEGORY' in request.args:
        id = int(request.args['NAME_CATEGORY'])
    else:
        return "Error: No id field provided. Please specify an id."

    # Create an empty list for our results
    results = []

    return jsonify({'message': 'Categoria creada exitosamente!'})



@api_v2_bp.route('/resources/categories', methods=['POST'])
def api_create_categories_v2():
    conn = get_db_connection()
    cursor = conn.cursor()
    data = request.get_json()

    cursor.execute("INSERT INTO category (NAME_CATEGORY) VALUES (?)",
                   (data['NAME_CATEGORY']))
    conn.commit()

    return jsonify({'message': 'Categoria creada exitosamente!'})








# Endpoint para actualizar un producto existente
@api_v2_bp.route('/resources/productos/<int:product_id>', methods=['PUT'])
def update_product(product_id):
    # Recuperar el producto existente desde la base de datos
    product = Product.query.get(product_id)

    if not product:
        # Devolver un error si el producto no existe
        return jsonify({'error': 'Product not found'}), 404

    # Obtener los datos actualizados del producto del cuerpo de la solicitud
    data = request.json

    # Actualizar los datos del producto
    product.name = data['name']
    product.price = data['price']
    product.description = data['description']

    # Guardar los cambios en la base de datos
    db.session.commit()

    # Devolver los datos actualizados del producto en el cuerpo de la respuesta
    return jsonify({'product': product.to_dict()}), 200






app = flask.Flask(__name__)
app.register_blueprint(api_v1_bp)
app.register_blueprint(api_v2_bp)
app.config["DEBUG"] = True


if __name__ == '__main__':
    app.run()