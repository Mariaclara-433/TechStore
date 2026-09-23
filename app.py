from flask import Flask, render_template, request, redirect, url_for, flash, session
from database.conexion import obtener_conexion

import os
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash

from flask import send_file
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import cm
from io import BytesIO
from datetime import datetime


app = Flask(__name__)
app.secret_key = "adso2026"


UPLOAD_FOLDER = os.path.join("static", "img_productos")
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER


# =========================
# INICIO
# =========================

@app.route("/")
def inicio():

    conexion = obtener_conexion()
    cursor = conexion.cursor(dictionary=True)

    cursor.execute("SELECT * FROM productos LIMIT 4")

    productos = cursor.fetchall()

    cursor.close()
    conexion.close()

    return render_template("index1.html", productos=productos)


# =========================
# PRODUCTOS
# =========================

@app.route("/productos")
def productos():

    if "usuario" not in session:
        return redirect(url_for("inicio"))

    if session.get("rol") != "Administrador":
        return redirect(url_for("inicio"))

    conexion = obtener_conexion()

    cursor = conexion.cursor(dictionary=True)

    cursor.execute("SELECT * FROM productos")

    productos = cursor.fetchall()

    cursor.close()
    conexion.close()

    return render_template("productos.html", productos=productos)


# =========================
# PAGINAS
# =========================

@app.route("/contacto")
def contacto():
    return render_template("contacto.html")


@app.route("/nosotros")
def nosotros():
    return render_template("nosotros.html")


@app.route("/servicios")
def servicios():
    return render_template("servicios.html")


@app.route("/catalogo")
def catalogo():
    return render_template("catalogo.html")


# =========================
# REGISTRAR PRODUCTO
# =========================

@app.route("/registro_producto")
def registro_producto():

    if "usuario" not in session:
        return redirect(url_for("inicio"))

    if session.get("rol") != "Administrador":
        return redirect(url_for("inicio"))

    return render_template("registro_producto.html")


@app.route("/guardar_producto", methods=["POST"])
def guardar_producto():

    # Verificar sesión
    if "usuario" not in session:
        return redirect(url_for("inicio"))

    if session.get("rol") != "Administrador":
        return redirect(url_for("inicio"))
    # ==========================================
    # 1. OBTENER DATOS Y ELIMINAR ESPACIOS
    # ==========================================

    codigo = request.form.get("codigo", "").strip()
    nombre = request.form.get("nombre", "").strip()
    precio = request.form.get("precio", "").strip()
    categoria = request.form.get("categoria", "").strip()


    # ==========================================
    # 2. NINGÚN CAMPO VACÍO
    # ==========================================

    if not codigo or not nombre or not precio or not categoria:

        flash(
            "Todos los campos son obligatorios.",
            "danger"
        )

        return redirect(
            url_for("registro_producto")
        )


    # ==========================================
    # 3. PRECIO NUMÉRICO
    # ==========================================

    try:

        precio = float(precio)

    except ValueError:

        flash(
            "El precio debe ser numérico.",
            "danger"
        )

        return redirect(
            url_for("registro_producto")
        )


    # ==========================================
    # 4. PRECIO MAYOR QUE CERO
    # ==========================================

    if precio <= 0:

        flash(
            "El precio debe ser mayor que cero.",
            "danger"
        )

        return redirect(
            url_for("registro_producto")
        )


    # ==========================================
    # 5. PRECIO MÁXIMO
    # ==========================================

    if precio > 50000000:

        flash(
            "El precio no puede ser mayor a $5.000.000.",
            "danger"
        )

        return redirect(
            url_for("registro_producto")
        )


    # ==========================================
    # 6. LONGITUD DEL CÓDIGO
    # ==========================================

    if len(codigo) != 4:

        flash(
            "El código debe tener exactamente 4 caracteres.",
            "danger"
        )

        return redirect(
            url_for("registro_producto")
        )


    # ==========================================
    # 7. FORMATO DEL CÓDIGO
    # ==========================================
    # Ejemplos válidos:
    # P001
    # P002
    # P003

    import re

    if not re.match(r"^P\d{3}$", codigo):

        flash(
            "Formato incorrecto. Use un código como P001, P002 o P003.",
            "danger"
        )

        return redirect(
            url_for("registro_producto")
        )


    # ==========================================
    # 8. NOMBRE MÍNIMO
    # ==========================================

    if len(nombre) < 5:

        flash(
            "El nombre debe tener mínimo 5 caracteres.",
            "danger"
        )

        return redirect(
            url_for("registro_producto")
        )


    # ==========================================
    # 9. NOMBRE MÁXIMO
    # ==========================================

    if len(nombre) > 100:

        flash(
            "El nombre no puede tener más de 100 caracteres.",
            "danger"
        )

        return redirect(
            url_for("registro_producto")
        )


    # ==========================================
    # CONEXIÓN A LA BASE DE DATOS
    # ==========================================

    conexion = obtener_conexion()

    cursor = conexion.cursor()


    # ==========================================
    # 10. CÓDIGO DUPLICADO
    # ==========================================

    cursor.execute(
        "SELECT codigo FROM productos WHERE codigo = %s",
        (codigo,)
    )

    existente = cursor.fetchone()


    if existente:

        cursor.close()
        conexion.close()

        flash(
            f"El código {codigo} ya existe. Elija otro.",
            "danger"
        )

        return redirect(
            url_for("registro_producto")
        )


    # ==========================================
    # 11. IMAGEN
    # ==========================================

    imagen = request.files.get("imagen")

    nombre_imagen = None


    if imagen and imagen.filename != "":

        os.makedirs(
            app.config["UPLOAD_FOLDER"],
            exist_ok=True
        )

        nombre_imagen = secure_filename(
            imagen.filename
        )

        ruta = os.path.join(
            app.config["UPLOAD_FOLDER"],
            nombre_imagen
        )

        imagen.save(ruta)


    # ==========================================
    # 12. INSERTAR PRODUCTO
    # ==========================================

    sql = """
        INSERT INTO productos
        (codigo, nombre, precio, categoria, imagen)
        VALUES (%s, %s, %s, %s, %s)
    """


    cursor.execute(
        sql,
        (
            codigo,
            nombre,
            precio,
            categoria,
            nombre_imagen
        )
    )


    conexion.commit()

    cursor.close()
    conexion.close()


    # ==========================================
    # MENSAJE DE ÉXITO
    # ==========================================

    flash(
        "Producto registrado correctamente.",
        "success"
    )

    return redirect(
        url_for("productos")
    )

# =========================
# EDITAR PRODUCTO
# =========================

@app.route("/editar_producto/<codigo>")
def editar_producto(codigo):

    if "usuario" not in session:
        return redirect(url_for("inicio"))

    if session.get("rol") != "Administrador":
        return redirect(url_for("inicio"))


    conexion = obtener_conexion()

    cursor = conexion.cursor(dictionary=True)


    sql = """
        SELECT * FROM productos
        WHERE codigo=%s
    """


    cursor.execute(
        sql,
        (codigo,)
    )


    producto = cursor.fetchone()


    cursor.close()
    conexion.close()


    return render_template(
        "editar_producto.html",
        producto=producto
    )


# =========================
# ACTUALIZAR PRODUCTO
# =========================

@app.route("/actualizar_producto", methods=["POST"])
def actualizar_producto():

    if "usuario" not in session:
        return redirect(url_for("inicio"))

    if session.get("rol") != "Administrador":
        return redirect(url_for("inicio"))


    codigo = request.form["codigo"]
    nombre = request.form["nombre"].strip()
    categoria = request.form["categoria"].strip()
    precio = request.form["precio"].strip()


    # =========================
    # VALIDACIONES
    # =========================

    if len(nombre) < 3:
        flash(
            "El nombre debe tener mínimo 3 caracteres.",
            "danger"
        )

        return redirect(
            url_for(
                "editar_producto",
                codigo=codigo
            )
        )


    if len(categoria) < 3:
        flash(
            "La categoría debe tener mínimo 3 caracteres.",
            "danger"
        )

        return redirect(
            url_for(
                "editar_producto",
                codigo=codigo
            )
        )


    try:
        precio = float(precio)

    except ValueError:
        flash(
            "El precio debe ser numérico.",
            "danger"
        )

        return redirect(
            url_for(
                "editar_producto",
                codigo=codigo
            )
        )


    if precio <= 0:
        flash(
            "El precio debe ser mayor que 0.",
            "danger"
        )

        return redirect(
            url_for(
                "editar_producto",
                codigo=codigo
            )
        )


    conexion = obtener_conexion()

    cursor = conexion.cursor()


    # =========================
    # IMAGEN
    # =========================

    imagen = request.files.get("imagen")


    if imagen and imagen.filename != "":

        nombre_imagen = secure_filename(
            imagen.filename
        )


        os.makedirs(
            app.config["UPLOAD_FOLDER"],
            exist_ok=True
        )


        ruta = os.path.join(
            app.config["UPLOAD_FOLDER"],
            nombre_imagen
        )


        imagen.save(ruta)


        sql = """
            UPDATE productos
            SET nombre=%s,
                precio=%s,
                categoria=%s,
                imagen=%s
            WHERE codigo=%s
        """


        cursor.execute(
            sql,
            (
                nombre,
                precio,
                categoria,
                nombre_imagen,
                codigo
            )
        )


    else:

        sql = """
            UPDATE productos
            SET nombre=%s,
                precio=%s,
                categoria=%s
            WHERE codigo=%s
        """


        cursor.execute(
            sql,
            (
                nombre,
                precio,
                categoria,
                codigo
            )
        )


    conexion.commit()

    cursor.close()
    conexion.close()


    flash(
        "Producto actualizado correctamente",
        "success"
    )


    return redirect(
        url_for("productos")
    )


# =========================
# ELIMINAR PRODUCTO
# =========================

@app.route("/eliminar_producto/<codigo>")
def eliminar_producto(codigo):

    if "usuario" not in session:
        return redirect(url_for("inicio"))

    if session.get("rol") != "Administrador":
        return redirect(url_for("inicio"))


    conexion = obtener_conexion()

    cursor = conexion.cursor()


    sql = """
        DELETE FROM productos
        WHERE codigo=%s
    """


    cursor.execute(
        sql,
        (codigo,)
    )


    conexion.commit()


    flash(
        "Producto eliminado correctamente",
        "success"
    )


    cursor.close()
    conexion.close()


    return redirect(
        url_for("productos")
    )


# =========================
# LOGIN
# =========================

@app.route("/login", methods=["POST"])
def login():

    print("Método:", request.method)
    print("Formulario:", request.form)


    correo = request.form.get("correo")
    password = request.form.get("password")


    if not correo or not password:

        flash(
            "Debe ingresar el correo y la contraseña",
            "danger"
        )

        return redirect(
            url_for("inicio")
        )


    conexion = obtener_conexion()

    cursor = conexion.cursor(dictionary=True)

    # -------------------------------------------------
    # Ya NO comparamos el password en el SQL.
    # Traemos el usuario solo por correo + estado activo,
    # y comparamos el hash en Python con check_password_hash.
    # -------------------------------------------------

    sql = """
        SELECT *
        FROM usuarios
        WHERE correo=%s
        AND estado='Activo'
    """


    cursor.execute(
        sql,
        (correo,)
    )


    usuario = cursor.fetchone()


    cursor.close()
    conexion.close()


    # =========================
    # VERIFICAR CONTRASEÑA CON HASH
    # =========================

    if usuario and check_password_hash(usuario["password"], password):

        session["usuario"] = usuario["nombre"]

        session["rol"] = usuario["rol"]

        session["correo"] = usuario["correo"]

        if usuario["rol"] == "Administrador":

            return redirect(
                url_for("admin")
        )

        elif usuario["rol"] == "Cliente":

            return redirect(
                url_for("dashboard_cliente")
        )

        else:

            flash(
            "Rol de usuario no reconocido",
            "danger"
        )

        return redirect(
            url_for("inicio")
        )



    # =========================
    # LOGIN INCORRECTO
    # =========================

    flash(
        "Correo o contraseña incorrectos",
        "danger"
    )


    return redirect(
        url_for("inicio")
    )


# =========================
# ADMIN
# =========================

@app.route("/admin")
def admin():

    if "usuario" not in session:
        return redirect(url_for("inicio"))

    if session.get("rol") != "Administrador":
        return redirect(url_for("inicio"))

    return render_template("admin.html")


# =========================
# CERRAR SESION
# =========================

@app.route("/logout")
def logout():

    session.clear()

    return redirect(
        url_for("inicio")
    )

# =========================
# REGISTRAR USUARIO
# =========================

@app.route("/registrar_usuario", methods=["POST"])
def registrar_usuario():

    # 1. Obtener datos del formulario
    nombre = request.form.get("nombre", "").strip()
    correo = request.form.get("correo", "").strip()
    telefono = request.form.get("telefono", "").strip()
    password = request.form.get("password", "")
    confirmPassword = request.form.get("confirmPassword", "")

    # 2. Verificar campos vacíos
    if not nombre or not correo or not telefono or not password or not confirmPassword:
        flash("Todos los campos son obligatorios.", "danger")
        return redirect(url_for("inicio"))

    # 3. Verificar que las contraseñas coincidan
    if password != confirmPassword:
        flash("Las contraseñas no coinciden.", "danger")
        return redirect(url_for("inicio"))

    # 4. Conectar a la base de datos
    conexion = obtener_conexion()
    cursor = conexion.cursor()

    # 5. Verificar si el correo ya existe
    cursor.execute(
        "SELECT correo FROM usuarios WHERE correo = %s",
        (correo,)
    )

    usuario_existente = cursor.fetchone()

    if usuario_existente:
        cursor.close()
        conexion.close()

        flash("El correo ya está registrado.", "danger")
        return redirect(url_for("inicio"))

    # 6. Encriptar la contraseña antes de guardarla
    password_hash = generate_password_hash(password)

    # 7. Insertar usuario
    sql = """
        INSERT INTO usuarios
        (nombre, correo, telefono, password, rol, estado)
        VALUES (%s, %s, %s, %s, %s, %s)
    """

    cursor.execute(
        sql,
        (
            nombre,
            correo,
            telefono,
            password_hash,
            "Cliente",
            "Activo"
        )
    )

    # 8. Guardar cambios
    conexion.commit()

    # 9. Cerrar conexión
    cursor.close()
    conexion.close()

    # 10. Mensaje de éxito
    flash("Usuario registrado correctamente.", "success")

    return redirect(url_for("inicio"))

# =========================
# DASHBOARD CLIENTE
# =========================

@app.route("/dashboard_cliente")
def dashboard_cliente():

    if "usuario" not in session:
        return redirect(url_for("inicio"))

    if session.get("rol") != "Cliente":
        return redirect(url_for("inicio"))


    conexion = obtener_conexion()

    cursor = conexion.cursor(dictionary=True)


    sql = """
        SELECT *
        FROM usuarios
        WHERE correo=%s
    """


    cursor.execute(
        sql,
        (session["correo"],)
    )


    usuario = cursor.fetchone()


    cursor.close()
    conexion.close()


    if not usuario:
        return redirect(url_for("inicio"))


    return render_template(
        "dashboard_cliente.html",
        usuario=usuario
    )

# =========================
# ACTUALIZAR PERFIL (CLIENTE)
# =========================

@app.route("/actualizar_perfil", methods=["POST"])
def actualizar_perfil():

    if "usuario" not in session:
        return redirect(url_for("inicio"))

    if session.get("rol") != "Cliente":
        return redirect(url_for("inicio"))


    # ==========================================
    # 1. OBTENER DATOS
    # ==========================================

    nombre = request.form.get("nombre", "").strip()
    telefono = request.form.get("telefono", "").strip()
    password = request.form.get("password", "")
    confirmPassword = request.form.get("confirmPassword", "")

    correo_actual = session["correo"]


    # ==========================================
    # 2. VALIDACIONES BÁSICAS
    # ==========================================

    if not nombre or not telefono:

        flash(
            "Nombre y teléfono son obligatorios.",
            "danger"
        )

        return redirect(
            url_for("dashboard_cliente")
        )


    if len(nombre) < 3:

        flash(
            "El nombre debe tener mínimo 3 caracteres.",
            "danger"
        )

        return redirect(
            url_for("dashboard_cliente")
        )


    # ==========================================
    # 3. VALIDAR CONTRASEÑA (SOLO SI QUIERE CAMBIARLA)
    # ==========================================

    password_hash = None

    if password or confirmPassword:

        if password != confirmPassword:

            flash(
                "Las contraseñas no coinciden.",
                "danger"
            )

            return redirect(
                url_for("dashboard_cliente")
            )

        if len(password) < 4:

            flash(
                "La contraseña debe tener mínimo 4 caracteres.",
                "danger"
            )

            return redirect(
                url_for("dashboard_cliente")
            )

        # Encriptar la nueva contraseña
        password_hash = generate_password_hash(password)


    conexion = obtener_conexion()

    cursor = conexion.cursor()


    # ==========================================
    # 4. ACTUALIZAR (CON O SIN CONTRASEÑA) - CORREO NO SE MODIFICA
    # ==========================================

    if password_hash:

        sql = """
            UPDATE usuarios
            SET nombre=%s,
                telefono=%s,
                password=%s
            WHERE correo=%s
        """

        cursor.execute(
            sql,
            (
                nombre,
                telefono,
                password_hash,
                correo_actual
            )
        )

    else:

        sql = """
            UPDATE usuarios
            SET nombre=%s,
                telefono=%s
            WHERE correo=%s
        """

        cursor.execute(
            sql,
            (
                nombre,
                telefono,
                correo_actual
            )
        )


    conexion.commit()

    cursor.close()
    conexion.close()


    # ==========================================
    # 5. ACTUALIZAR LA SESIÓN (EL CORREO NO CAMBIA)
    # ==========================================

    session["usuario"] = nombre


    flash(
        "Datos actualizados correctamente.",
        "success"
    )

    return redirect(
        url_for("dashboard_cliente")
    )
# =========================
# REPORTE PDF DE PRODUCTOS
# =========================

@app.route("/reporte_productos")
def reporte_productos():

    if "usuario" not in session:
        return redirect(url_for("inicio"))

    if session.get("rol") != "Administrador":
        return redirect(url_for("inicio"))


    # ==========================================
    # 1. OBTENER PRODUCTOS
    # ==========================================

    conexion = obtener_conexion()

    cursor = conexion.cursor(dictionary=True)

    cursor.execute("SELECT * FROM productos")

    productos = cursor.fetchall()

    cursor.close()
    conexion.close()


    # ==========================================
    # 2. CREAR EL PDF EN MEMORIA
    # ==========================================

    buffer = BytesIO()

    documento = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        topMargin=1.5 * cm,
        bottomMargin=1.5 * cm
    )

    elementos = []

    estilos = getSampleStyleSheet()


    # ------ Título ------

    titulo = Paragraph(
        "Reporte de Productos - TechStore",
        estilos["Title"]
    )

    elementos.append(titulo)


    fecha = Paragraph(
        f"Generado el: {datetime.now().strftime('%d/%m/%Y %H:%M')}",
        estilos["Normal"]
    )

    elementos.append(fecha)

    elementos.append(Spacer(1, 20))


    # ------ Encabezados de la tabla ------

    data = [
        ["Código", "Nombre", "Categoría", "Precio"]
    ]


    # ------ Filas con los productos ------

    total_general = 0

    for producto in productos:

        data.append([
            producto["codigo"],
            producto["nombre"],
            producto["categoria"],
            f"$ {producto['precio']:,.2f}"
        ])

        total_general += producto["precio"]


    # ------ Fila de total ------

    data.append([
        "", "", "TOTAL",
        f"$ {total_general:,.2f}"
    ])


    # ------ Construir tabla ------

    tabla = Table(
        data,
        colWidths=[3 * cm, 6 * cm, 4 * cm, 3.5 * cm]
    )

    tabla.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1c1f26")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("ROWBACKGROUNDS", (0, 1), (-1, -2), [colors.whitesmoke, colors.lightgrey]),
        ("FONTNAME", (0, -1), (-1, -1), "Helvetica-Bold"),
        ("BACKGROUND", (0, -1), (-1, -1), colors.HexColor("#f0ad4e")),
    ]))


    elementos.append(tabla)


    # ==========================================
    # 3. GENERAR EL PDF
    # ==========================================

    documento.build(elementos)

    buffer.seek(0)


    return send_file(
        buffer,
        as_attachment=True,
        download_name="reporte_productos.pdf",
        mimetype="application/pdf"
    )


# =========================
# EJECUTAR APP
# =========================

app.run(debug=True)