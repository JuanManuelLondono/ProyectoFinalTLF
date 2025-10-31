from flask import Flask, render_template, request, jsonify, redirect, url_for, session
import re
from datetime import datetime
import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from dotenv import load_dotenv

# Cargar variables de entorno desde .env
load_dotenv()

app = Flask(__name__)
app.secret_key = '4545' 

# Configuración de SendGrid
SENDGRID_API_KEY = os.getenv('SENDGRID_API_KEY')

def enviar_correo_registro(nombre, email):
    try:
        message = Mail(
            from_email='juanp.velezl@uqvirtual.edu.co',
            to_emails=email,
            subject='Bienvenido a Hotel SmartCheck',
            html_content=f"""
            <h2>¡Bienvenido a Hotel SmartCheck, {nombre}!</h2>
            <p>Tu registro ha sido completado exitosamente.</p>
            <p>Ahora puedes realizar reservas en nuestro hotel.</p>
            """
        )
        sg = SendGridAPIClient(SENDGRID_API_KEY)
        response = sg.send(message)
        return True
    except Exception as e:
        print(f"Error al enviar correo de registro: {str(e)}")
        print(f"Detalles - Nombre: {nombre}, Email: {email}")
        return False

def enviar_correo_reserva(nombre, email, habitacion, fecha_entrada, fecha_salida, numero_huespedes):
    try:
        message = Mail(
            from_email='juanp.velezl@uqvirtual.edu.co',
            to_emails=email,
            subject='Confirmación de Reserva - Hotel SmartCheck',
            html_content=f"""
            <h2>Confirmación de Reserva - Hotel SmartCheck</h2>
            <p>Estimado(a) {nombre},</p>
            <p>Tu reserva ha sido confirmada con los siguientes detalles:</p>
            <ul>
                <li><strong>Habitación:</strong> {habitacion}</li>
                <li><strong>Fecha de entrada:</strong> {fecha_entrada}</li>
                <li><strong>Fecha de salida:</strong> {fecha_salida}</li>
                <li><strong>Número de huéspedes:</strong> {numero_huespedes}</li>
            </ul>
            <p>¡Esperamos verte pronto!</p>
            """
        )
        sg = SendGridAPIClient(SENDGRID_API_KEY)
        response = sg.send(message)
        return True
    except Exception as e:
        print(f"Error al enviar correo de reserva: {str(e)}")
        print(f"Detalles - Nombre: {nombre}, Email: {email}, Habitación: {habitacion}")
        print(f"Fechas - Entrada: {fecha_entrada}, Salida: {fecha_salida}, Huéspedes: {numero_huespedes}")
        return False

# Expresiones regulares
regex_nombre = r'^[A-Za-zÁÉÍÓÚáéíóúÑñ ]{3,60}$'
regex_email = r'^[\w\.-]+@[\w\.-]+\.\w{2,4}$'
regex_telefono = r'^3\d{9}$'
regex_cedula = r'^\d{10}$'
regex_pasaporte = r'^[A-Z0-9]{6,9}$'
regex_contrasena = r'^(?=.*[A-Z])(?=.*\d)(?=.*[!@#$%^&*()_+\-=\[\]{};:\'",.<>?/~`|\\]).{8,}$'
regex_habitacion = r'^HAB[A-Za-z0-9_]{1,20}$'

def validar(campo, patron):
    return bool(re.match(patron, campo))

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/registro')
def registro():
    return render_template('registro.html')

@app.route('/reserva')
def reserva():
    # Datos de habitaciones de ejemplo
    habitaciones = [
        {
            'id': 'HAB_DOBLE_1',
            'nombre': 'Habitación Doble Premium',
                'imagen': 'hab_doble_1.jpg',
            'precio': 150000,
            'descripcion': 'Habitación doble con vista al mar, cama king size y balcón privado.'
        },
        {
            'id': 'HAB_DOBLE_2', 
            'nombre': 'Habitación Doble Estándar',
                'imagen': 'hab_doble_2.jpg',
            'precio': 120000,
            'descripcion': 'Habitación doble con vista al jardín, cómoda y acogedora.'
        },
        {
            'id': 'HAB_SENCILLA_1',
            'nombre': 'Habitación Sencilla Premium',
                'imagen': 'hab_sencilla_1.jpg', 
            'precio': 100000,
            'descripcion': 'Habitación sencilla con todas las comodidades modernas.'
        },
        {
            'id': 'HAB_SUITE_1',
            'nombre': 'Suite Presidencial',
                'imagen': 'hab_suite_1.jpg',
            'precio': 250000,
            'descripcion': 'Suite de lujo con sala de estar, jacuzzi y vista panorámica.'
        }
    ]
    return render_template('reserva.html', habitaciones=habitaciones)

@app.route('/confirmacion_registro')
def confirmacion_registro():
    # Verificar si hay datos de registro en la sesión
    if 'registro_data' not in session:
        return redirect(url_for('registro'))
    
    registro_data = session['registro_data']
    return render_template('confirmacion_registro.html', 
                         nombre=registro_data['nombre'],
                         email=registro_data['email'],
                         fecha_registro=registro_data['fecha_registro'])

@app.route('/confirmacion_reserva')
def confirmacion_reserva():
    # Verificar si hay datos de reserva en la sesión
    if 'reserva_data' not in session:
        return redirect(url_for('reserva'))
    
    reserva_data = session['reserva_data']
    return render_template('confirmacion_reserva.html', 
                         nombre=reserva_data['nombre'],
                         email=reserva_data['email'],
                         telefono=reserva_data['telefono'],
                         habitacion=reserva_data['habitacion'],
                         fecha_entrada=reserva_data['fecha_entrada'],
                         fecha_salida=reserva_data['fecha_salida'],
                         numero_huespedes=reserva_data['numero_huespedes'],
                         fecha_reserva=reserva_data['fecha_reserva'])

@app.route('/validar', methods=['POST'])
def validar_form():
    data = request.get_json()
    nombre = data.get('nombre', '')
    email = data.get('email', '')
    telefono = data.get('telefono', '')
    cedula = data.get('cedula', '')
    tipo_identificacion = data.get('tipo_identificacion', 'cedula')
    contrasena = data.get('contrasena', '')

    errores = {}

    if not validar(nombre, regex_nombre):
        errores['nombre'] = "Solo letras y espacios (3-60 caracteres)."
    if not validar(email, regex_email):
        errores['email'] = "Formato de correo no válido."
    if not validar(telefono, regex_telefono):
        errores['telefono'] = "Debe empezar con 3 y tener exactamente 10 dígitos."
    # Validar documento según el tipo seleccionado
    if tipo_identificacion == 'pasaporte':
        if not validar(cedula, regex_pasaporte):
            errores['cedula'] = "Pasaporte: 6-9 caracteres. Solo letras MAYÚSCULAS y números."
    else:
        if not validar(cedula, regex_cedula):
            errores['cedula'] = "Cédula colombiana: exactamente 10 números."
    if not validar(contrasena, regex_contrasena):
        errores['contrasena'] = "Debe tener al menos 8 caracteres, una mayúscula, un número y un carácter especial."

    if errores:
        return jsonify({'valido': False, 'errores': errores})
    else:
        # Guardar datos del registro en la sesión
        fecha_registro = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        session['registro_data'] = {
            'nombre': nombre,
            'email': email,
            'fecha_registro': fecha_registro
        }
        
        # Enviar correo de bienvenida
        enviar_correo_registro(nombre, email)
        
        return jsonify({'valido': True, 'redirect': url_for('confirmacion_registro')})

@app.route('/validar_reserva', methods=['POST'])
def validar_reserva():
    data = request.get_json()
    nombre = data.get('nombre', '')
    email = data.get('email', '')
    telefono = data.get('telefono', '')
    habitacion = data.get('habitacion', '')
    fecha_entrada = data.get('fecha_entrada', '')
    fecha_salida = data.get('fecha_salida', '')
    numero_huespedes = data.get('numero_huespedes', '')

    # Datos de habitaciones disponibles (debe coincidir con los del template)
    habitaciones_disponibles = [
        'HAB_DOBLE_1', 'HAB_DOBLE_2', 'HAB_SENCILLA_1', 'HAB_SUITE_1'
    ]

    errores = {}

    if not validar(nombre, regex_nombre):
        errores['nombre'] = "Solo letras y espacios (3-60 caracteres)."
    if not validar(email, regex_email):
        errores['email'] = "Formato de correo no válido."
    if not validar(telefono, regex_telefono):
        errores['telefono'] = "Debe empezar con 3 y tener exactamente 10 dígitos."
    if not habitacion:
        errores['habitacion'] = "Debe ingresar el nombre de una habitación."
    elif not validar(habitacion, regex_habitacion):
        errores['habitacion'] = "El nombre debe empezar con 'HAB' seguido de letras, números o guiones bajos (máximo 20 caracteres)."
    elif habitacion not in habitaciones_disponibles:
        errores['habitacion'] = "Esta habitación no está disponible. Selecciona una de las habitaciones disponibles."
    if not fecha_entrada:
        errores['fecha_entrada'] = "Debe seleccionar fecha de entrada."
    if not fecha_salida:
        errores['fecha_salida'] = "Debe seleccionar fecha de salida."
    if not numero_huespedes or int(numero_huespedes) < 1 or int(numero_huespedes) > 6:
        errores['numero_huespedes'] = "Debe ser entre 1 y 6 huéspedes."

    # Validar que la fecha de salida sea posterior a la de entrada
    if fecha_entrada and fecha_salida:
        try:
            fecha_entrada_dt = datetime.strptime(fecha_entrada, '%Y-%m-%d')
            fecha_salida_dt = datetime.strptime(fecha_salida, '%Y-%m-%d')
            if fecha_salida_dt <= fecha_entrada_dt:
                errores['fecha_salida'] = "La fecha de salida debe ser posterior a la de entrada."
        except ValueError:
            errores['fecha_entrada'] = "Formato de fecha inválido."

    if errores:
        return jsonify({'valido': False, 'errores': errores})
    else:
        # Guardar datos de la reserva en la sesión
        fecha_reserva = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        session['reserva_data'] = {
            'nombre': nombre,
            'email': email,
            'telefono': telefono,
            'habitacion': habitacion,
            'fecha_entrada': fecha_entrada,
            'fecha_salida': fecha_salida,
            'numero_huespedes': numero_huespedes,
            'fecha_reserva': fecha_reserva
        }
        
        # Enviar correo de confirmación de reserva
        enviar_correo_reserva(nombre, email, habitacion, fecha_entrada, fecha_salida, numero_huespedes)
        
        return jsonify({'valido': True, 'redirect': url_for('confirmacion_reserva')})

if __name__ == '__main__':
    app.run(debug=True)
