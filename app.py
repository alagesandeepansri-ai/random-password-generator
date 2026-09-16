from flask import Flask, render_template, request, redirect, session
import string
import random
import sqlite3
from database import create_database

app = Flask(__name__)

app.secret_key = "random-password-generator-secret-key"

# Create database and tables automatically
create_database()


def get_db_connection():

    conn = sqlite3.connect("password_generator.db")

    conn.row_factory = sqlite3.Row

    return conn


# =========================
# USER HOME
# =========================

@app.route("/")
def home():

    if "user_id" not in session:

        return redirect("/login")

    conn = get_db_connection()

    history_rows = conn.execute("""
        SELECT password, created_at
        FROM password_history
        WHERE user_id = ?
        ORDER BY id DESC
    """, (session["user_id"],)).fetchall()

    conn.close()

    return render_template(
        "index.html",
        password="",
        strength="",
        history=history_rows
    )


# =========================
# USER REGISTRATION
# =========================

@app.route("/register", methods=["GET", "POST"])
def register():

    message = ""

    if request.method == "POST":

        name = request.form["name"]

        email = request.form.get("email")

        mobile = request.form.get("mobile")

        dob = request.form["dob"]

        password = request.form["password"]

        if not email and not mobile:

            message = "Please enter Email or Mobile Number."

            return render_template(
                "register.html",
                message=message
            )

        conn = get_db_connection()

        try:

            conn.execute("""
                INSERT INTO users
                (name, email, mobile, dob, password)
                VALUES (?, ?, ?, ?, ?)
            """, (
                name,
                email,
                mobile,
                dob,
                password
            ))

            conn.commit()

            conn.close()

            return redirect("/login")

        except sqlite3.IntegrityError:

            conn.close()

            message = "Email or Mobile Number already registered."

    return render_template(
        "register.html",
        message=message
    )


# =========================
# USER LOGIN
# =========================

@app.route("/login", methods=["GET", "POST"])
def login():

    message = ""

    if request.method == "POST":

        login_value = request.form["login_value"]

        password = request.form["password"]

        conn = get_db_connection()

        user = conn.execute("""
            SELECT *
            FROM users
            WHERE (email = ? OR mobile = ?)
            AND password = ?
        """, (
            login_value,
            login_value,
            password
        )).fetchone()

        conn.close()

        if user:

            session["user_id"] = user["id"]

            session["user_name"] = user["name"]

            return redirect("/")

        else:

            message = "Invalid Email/Mobile Number or Password."

    return render_template(
        "login.html",
        message=message
    )


# =========================
# USER LOGOUT
# =========================

@app.route("/logout")
def logout():

    session.clear()

    return redirect("/login")


# =========================
# PASSWORD GENERATION
# =========================

@app.route("/", methods=["POST"])
def generate_password():

    if "user_id" not in session:

        return redirect("/login")

    password = ""

    strength = ""

    length = int(request.form["length"])

    characters = ""

    if request.form.get("uppercase"):

        characters += string.ascii_uppercase

    if request.form.get("lowercase"):

        characters += string.ascii_lowercase

    if request.form.get("numbers"):

        characters += string.digits

    if request.form.get("symbols"):

        characters += string.punctuation

    if characters:

        password = "".join(
            random.choice(characters)
            for _ in range(length)
        )

        if length < 8:

            strength = "Weak"

        elif length < 12:

            strength = "Medium"

        elif length < 16:

            strength = "Strong"

        else:

            strength = "Very Strong"

        # Save generated password

        conn = get_db_connection()

        conn.execute("""
            INSERT INTO password_history
            (user_id, password)
            VALUES (?, ?)
        """, (
            session["user_id"],
            password
        ))

        conn.commit()

        conn.close()

    # Get complete password history

    conn = get_db_connection()

    history_rows = conn.execute("""
        SELECT password, created_at
        FROM password_history
        WHERE user_id = ?
        ORDER BY id DESC
    """, (session["user_id"],)).fetchall()

    conn.close()

    return render_template(
        "index.html",
        password=password,
        strength=strength,
        history=history_rows
    )


# =========================
# CLEAR PASSWORD HISTORY
# =========================

@app.route("/clear-history", methods=["POST"])
def clear_history():

    if "user_id" not in session:

        return redirect("/login")

    conn = get_db_connection()

    conn.execute("""
        DELETE FROM password_history
        WHERE user_id = ?
    """, (session["user_id"],))

    conn.commit()

    conn.close()

    return redirect("/")


# =========================
# ADMIN LOGIN
# =========================

@app.route("/admin-login", methods=["GET", "POST"])
def admin_login():

    message = ""

    if request.method == "POST":

        username = request.form["username"]

        password = request.form["password"]

        conn = get_db_connection()

        admin = conn.execute("""
            SELECT *
            FROM admin
            WHERE username = ?
            AND password = ?
        """, (
            username,
            password
        )).fetchone()

        conn.close()

        if admin:

            session["admin_id"] = admin["id"]

            session["admin_username"] = admin["username"]

            return redirect("/admin-dashboard")

        else:

            message = "Invalid Admin Username or Password."

    return render_template(
        "admin_login.html",
        message=message
    )


# =========================
# ADMIN DASHBOARD
# =========================

@app.route("/admin-dashboard")
def admin_dashboard():

    if "admin_id" not in session:

        return redirect("/admin-login")

    conn = get_db_connection()

    # Get user details and password count

    users = conn.execute("""
        SELECT
            users.id,
            users.name,
            users.email,
            users.mobile,
            users.dob,
            COUNT(password_history.id) AS password_count
        FROM users
        LEFT JOIN password_history
        ON users.id = password_history.user_id
        GROUP BY users.id
        ORDER BY users.id DESC
    """).fetchall()

    # Total registered users

    user_count = conn.execute("""
        SELECT COUNT(*) AS total
        FROM users
    """).fetchone()["total"]

    # Total generated passwords

    password_count = conn.execute("""
        SELECT COUNT(*) AS total
        FROM password_history
    """).fetchone()["total"]

    conn.close()

    return render_template(
        "admin_dashboard.html",
        users=users,
        user_count=user_count,
        password_count=password_count
    )


# =========================
# ADMIN LOGOUT
# =========================

@app.route("/admin-logout")
def admin_logout():

    session.pop("admin_id", None)

    session.pop("admin_username", None)

    return redirect("/admin-login")


# =========================
# RUN APPLICATION
# =========================

if __name__ == "__main__":

    app.run(debug=True)
