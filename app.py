from flask import Flask, render_template, request, redirect, flash
import mysql.connector
import re

app = Flask(__name__)
app.secret_key = "leads_tracker"

DB_CONFIG = {
    "host": "34.224.156.181",
    "user": "root",
    "password": "Ruby120",
    "database":"leadsdb"
}

def get_connection():
    return mysql.connector.connect(**DB_CONFIG)

# ---------------- HOME ----------------
@app.route("/")
def index():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM leads ORDER BY created_at DESC")
    leads = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template("index.html", leads=leads)

# ---------------- CREATE ----------------
@app.route("/add", methods=["POST"])
def add_lead():

    name = request.form["name"].strip()
    email = request.form["email"].strip()
    phone = request.form["phone"].strip()
    service = request.form["service"]

    # Validación nombre
    if not re.match(r'^[A-Za-zÁÉÍÓÚáéíóúÑñ ]{3,100}$', name):
        flash("Nombre inválido", "danger")
        return redirect("/")

    # Validación email
    if not re.match(r'^[\w\.-]+@[\w\.-]+\.\w+$', email):
        flash("Correo inválido", "danger")
        return redirect("/")

    # Validación teléfono
    if phone and not re.match(r'^\d{9}$', phone):
        flash("Teléfono debe tener 9 dígitos", "danger")
        return redirect("/")

    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO leads(name,email,phone,service)
            VALUES (%s,%s,%s,%s)
        """, (name, email, phone, service))

        conn.commit()
        cursor.close()
        conn.close()

        flash("Lead registrado correctamente", "success")

    except mysql.connector.IntegrityError:
        flash("El correo ya existe", "danger")

    return redirect("/")

# ---------------- DELETE ----------------
@app.route("/delete/<int:id>")
def delete(id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM leads WHERE id=%s", (id,))
    conn.commit()
    cursor.close()
    conn.close()
    flash("Lead eliminado", "success")
    return redirect("/")

# ---------------- UPDATE STATUS ----------------
@app.route("/update/<int:id>")
def update(id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE leads SET status='Contactado' WHERE id=%s", (id,))
    conn.commit()
    cursor.close()
    conn.close()
    flash("Lead actualizado", "success")
    return redirect("/")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
