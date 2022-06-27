from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import hashlib

app = Flask(__name__)
app.config.from_pyfile('config.py')

from models import db
from models import Usuario, Receta, Ingrediente

usuario_actual = None


@app.route('/', methods=['POST', 'GET'])
def inicio_sesion():
    global usuario_actual
    if request.method == 'POST':
        usuario_actual = Usuario.query.filter_by(correo=request.form['correo']).first()
        if usuario_actual is None:
            return render_template('error.html', error='Cuenta no registrada.')
        else:
            clave = hashlib.md5(bytes(request.form['clave'], encoding='utf-8'))
            if clave.hexdigest() == usuario_actual.clave:
                return redirect(url_for('home'))
            else:
                return render_template('error.html', error='Contraseña incorrecta.')
    else:
        return render_template('inicio_sesion.html')


@app.route('/home')
def home():
    return render_template('home.html')


@app.route('/compartir_receta', methods=['POST', 'GET'])
def compartir_receta():
    if request.method == 'GET':
        return render_template('ingreso_cantidad.html')
    else:
        i = 0
        cantidad_ingredientes = int(request.form['cantidad_ingredientes'])
        return render_template('compartir_receta.html', cantidad_ingredientes=cantidad_ingredientes, i=i)


@app.route('/consultar_ranking')
def consultar_ranking():
    return 'consulta ranking'


@app.route('/consultar_recetas')
def consultar_recetas():
    return 'consulta recetas'


@app.route('/error')
def error():
    return render_template('error.html')


if __name__ == '__main__':
    db.create_all()
    app.run(debug=True)
