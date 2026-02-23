import os
from flask import Flask, render_template, request, redirect, url_for
import psycopg2
from psycopg2.extras import RealDictCursor

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "clave-local")


# =========================
# CONEXIÓN A BASE DE DATOS
# =========================
def get_db():
    database_url = os.environ.get("DATABASE_URL")

    if database_url:
        # Render (producción)
        return psycopg2.connect(
            database_url,
            sslmode="require",
            cursor_factory=RealDictCursor
        )
    else:
        # Local
        return psycopg2.connect(
            host="localhost",
            port=5432,
            database="inscripciones_local",
            user="inscripciones_user",
            password="inscripciones123",
            cursor_factory=RealDictCursor
        )


# =========================
# INICIALIZAR BASE
# =========================
def init_db():
    conn = get_db()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS inscripciones (
            id SERIAL PRIMARY KEY,
            nombre TEXT NOT NULL,
            apellido TEXT NOT NULL,
            dni TEXT,
            email TEXT,
            telefono TEXT,
            curso TEXT NOT NULL,
            turno TEXT NOT NULL,
            perfil TEXT
        )
    """)

    conn.commit()
    cur.close()
    conn.close()


# =========================
# LISTADO
# =========================
@app.route("/")
def index():
    conn = get_db()
    cur = conn.cursor()

    cur.execute("SELECT * FROM inscripciones ORDER BY id DESC")
    inscripciones = cur.fetchall()

    cur.execute("SELECT DISTINCT curso FROM inscripciones")
    cursos = cur.fetchall()

    cur.close()
    conn.close()

    return render_template(
        "index.html",
        inscripciones=inscripciones,
        cursos=cursos
    )


# =========================
# AGREGAR
# =========================
@app.route("/add", methods=["GET", "POST"])
def add():
    if request.method == "POST":
        data = (
            request.form["nombre"],
            request.form["apellido"],
            request.form["dni"],
            request.form["email"],
            request.form["telefono"],
            request.form["curso"],
            request.form["turno"],
            request.form["perfil"]
        )

        conn = get_db()
        cur = conn.cursor()

        cur.execute("""
            INSERT INTO inscripciones
            (nombre, apellido, dni, email, telefono, curso, turno, perfil)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
        """, data)

        conn.commit()
        cur.close()
        conn.close()

        return redirect(url_for("index"))

    return render_template("form.html")


# =========================
# EDITAR
# =========================
@app.route("/edit/<int:id>", methods=["GET", "POST"])
def edit(id):
    conn = get_db()
    cur = conn.cursor()

    if request.method == "POST":
        data = (
            request.form["nombre"],
            request.form["apellido"],
            request.form["dni"],
            request.form["email"],
            request.form["telefono"],
            request.form["curso"],
            request.form["turno"],
            request.form["perfil"],
            id
        )

        cur.execute("""
            UPDATE inscripciones
            SET nombre=%s, apellido=%s, dni=%s, email=%s,
                telefono=%s, curso=%s, turno=%s, perfil=%s
            WHERE id=%s
        """, data)

        conn.commit()
        cur.close()
        conn.close()

        return redirect(url_for("index"))

    cur.execute("SELECT * FROM inscripciones WHERE id=%s", (id,))
    registro = cur.fetchone()

    cur.close()
    conn.close()

    return render_template("edit.html", registro=registro)


# =========================
# SOLO PARA DESARROLLO LOCAL
# =========================
if __name__ == "__main__":
    init_db()  # Solo se ejecuta localmente
    app.run(debug=True)