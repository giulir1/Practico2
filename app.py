from datetime import datetime
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
    global usuario_actual
    if request.method == 'GET':
        return render_template('ingresar_receta.html', usuario_actual=usuario_actual)
    else:
        nombre_receta = request.form['nombre_receta']
        tiempo_receta = int(request.form['tiempo_receta'])
        elaboracion = request.form['procedimiento']
        idUsuario = int(request.form['idUsuario'])
        fecha = datetime.now()
        idReceta = len(Receta.query.order_by(Receta.id).all())
        unaReceta = Receta(nombre=nombre_receta, tiempo=tiempo_receta, fecha=fecha, elaboracion=elaboracion.capitalize(), cantidadmegusta=8, usuarioid=idUsuario)
        db.session.add(unaReceta)
        db.session.commit()
        band = False
        i = 1
        while (i <= 10) and (not band):
            if (not request.form['nombre_ingrediente'+str(i)]) or (not request.form['cantidad_ingrediente'+str(i)]) or (not request.form['unidad_ingrediente'+str(i)]):
                band = True
            else:
                nombre_ingrediente = request.form['nombre_ingrediente'+str(i)]
                cantidad_ingrediente = request.form['cantidad_ingrediente'+str(i)]
                unidad_ingrediente = request.form['unidad_ingrediente'+str(i)]
                unIngrediente = Ingrediente(nombre=nombre_ingrediente, cantidad=cantidad_ingrediente, unidad=unidad_ingrediente, recetaid=idReceta+1)
                db.session.add(unIngrediente)
                db.session.commit()
                i += 1
        return redirect(url_for('home'))

@app.route('/consultar_ranking')
def consultar_ranking():
    return render_template('mostrar_ranking.html', recetas = Receta.query.order_by(-Receta.cantidadmegusta).limit(5))


@app.route('/consultar_recetas')
def consultar_recetas():
    return render_template('consultar_recetas.html')

@app.route('/consultar_tiempo')
def consultar_recetas_tiempo():
    return 'consultar por tiempo'

@app.route('/consultar_ingredientes')
def consultar_recetas_ingrediente():
    return 'consultar por ingrediente'

@app.route('/error')
def error():
    return render_template('error.html')


if __name__ == '__main__':
    db.create_all()
    app.run(debug=True)