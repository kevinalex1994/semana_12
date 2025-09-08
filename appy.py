from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import json, csv, os

app = Flask(__name__)

# --- Crear carpetas necesarias ---
os.makedirs('datos', exist_ok=True)
os.makedirs('database', exist_ok=True)

# --- Configuración de SQLite ---
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
db_path = os.path.join(BASE_DIR, 'database', 'usuarios.db')

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + db_path
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Modelo para almacenar clientes
class Usuario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100))

# Crear tabla si no existe
with app.app_context():
    db.create_all()

# -------------------- Página principal --------------------
@app.route('/')
def index():
    return render_template("index.html")

# Formulario de ingreso
@app.route('/formulario')
def formulario():
    return render_template("formulario.html")

# -------------------- Persistencia TXT --------------------
@app.route('/guardar_txt', methods=['POST'])
def guardar_txt():
    nombre = request.form['nombre']
    with open("datos/datos.txt", "a", encoding="utf-8") as f:
        f.write(nombre + "\n")
    return redirect(url_for('index'))

@app.route('/leer_txt')
def leer_txt():
    try:
        with open("datos/datos.txt", "r", encoding="utf-8") as f:
            contenido = f.readlines()
    except FileNotFoundError:
        contenido = []
    return render_template("resultado.html", datos=contenido, titulo="Clientes (TXT)")

# -------------------- Persistencia JSON --------------------
@app.route('/guardar_json', methods=['POST'])
def guardar_json():
    nombre = request.form['nombre']
    data = []
    try:
        with open("datos/datos.json", "r", encoding="utf-8") as f:
            data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        pass
    
    data.append({"nombre": nombre})

    with open("datos/datos.json", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
    
    return redirect(url_for('index'))

@app.route('/leer_json')
def leer_json():
    try:
        with open("datos/datos.json", "r", encoding="utf-8") as f:
            data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        data = []
    return render_template("resultado.html", datos=data, titulo="Clientes (JSON)")

# -------------------- Persistencia CSV --------------------
@app.route('/guardar_csv', methods=['POST'])
def guardar_csv():
    nombre = request.form['nombre']
    with open("datos/datos.csv", "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([nombre])
    return redirect(url_for('index'))

@app.route('/leer_csv')
def leer_csv():
    data = []
    try:
        with open("datos/datos.csv", "r", encoding="utf-8") as f:
            reader = csv.reader(f)
            data = [row for row in reader if row]
    except FileNotFoundError:
        pass
    return render_template("resultado.html", datos=data, titulo="Clientes (CSV)")

# -------------------- Persistencia SQLite --------------------
@app.route('/guardar_db', methods=['POST'])
def guardar_db():
    nombre = request.form['nombre']
    if nombre.strip():
        nuevo = Usuario(nombre=nombre)
        db.session.add(nuevo)
        db.session.commit()
    return redirect(url_for('index'))

@app.route('/leer_db')
def leer_db():
    usuarios = Usuario.query.all()
    data = [u.nombre for u in usuarios]
    return render_template("resultado.html", datos=data, titulo="Clientes (SQLite)")

# -------------------- Arranque del servidor --------------------
if __name__ == '__main__':
    app.run(debug=True)
