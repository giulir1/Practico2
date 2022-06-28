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
        unaReceta = Receta(nombre=nombre_receta, tiempo=tiempo_receta, fecha=fecha, elaboracion=elaboracion.capitalize(), cantidadmegusta=0
                           , usuarioid=idUsuario)
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
    return render_template('mostrar_ranking.html', recetas=Receta.query.order_by(-Receta.cantidadmegusta).limit(5))


@app.route('/consultar_recetas')
def consultar_recetas():
    return render_template('consultar_recetas.html')


@app.route('/consultar_tiempo', methods=['GET', 'POST'])
def consultar_recetas_tiempo():
    band = True
    if request.method == 'GET':
        return render_template('consultar_recetas_tiempo.html', band=band)
    else:
        tiempo = int(request.form['tiempo_receta'])
        recetas = Receta.query.filter(Receta.tiempo < tiempo).all()
        if len(recetas) == 0:
            band = False
        return render_template('consultar_recetas_tiempo.html', tiempo=tiempo, recetas=recetas, band=band)


@app.route('/consultar_ingredientes', methods=['GET', 'POST'])
def consultar_recetas_ingrediente():
    band = True
    if request.method == 'GET':
        return render_template('consultarecetasprueba.html', band=band)
    else:
        ingredientes = Ingrediente.query.filter_by(nombre=request.form['ingrediente_receta']).first()
        if ingredientes is None:
            band = False
        return render_template('consultarecetasprueba.html', ingredientes=ingredientes, band=band)


if __name__ == '__main__':
    db.create_all()
    app.run(debug=True)
