from flask import Flask, render_template, request, redirect, session
import string
import random
import sqlite3

from database import create_database


app = Flask(__name__)

app.secret_key = "secure_password_generator_secret_key"

create_database()


def get_db_connection():

    conn = sqlite3.connect("password_generator.db")

    conn.row_factory = sqlite3.Row

    return conn


# =========================================================
# HOME / PASSWORD GENERATOR
# =========================================================

@app.route("/", methods=["GET", "POST"])
def home():

    if "user_id" not in session:

        return redirect("/login")

    length = 12

    uppercase = False
    lowercase = False
    numbers = False
    symbols = False

    if request.method == "POST":

        length = int(
            request.form.get("length", 12)
        )

        uppercase = "uppercase" in request.form
        lowercase = "lowercase" in request.form
        numbers = "numbers" in request.form
        symbols = "symbols" in request.form

        characters = ""

        if uppercase:
            characters += string.ascii_uppercase

        if lowercase:
            characters += string.ascii_lowercase

        if numbers:
            characters += string.digits

        if symbols:
            characters += string.punctuation

        if not characters:

            return render_template(
                "index.html",
                length=length,
                uppercase=uppercase,
                lowercase=lowercase,
                numbers=numbers,
                symbols=symbols
            )

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

        conn = get_db_connection()

        cursor = conn.cursor()

        cursor.execute(
            """
            INSERT INTO password_history
            (user_id, password)
            VALUES (?, ?)
            """,
            (
                session["user_id"],
                password
            )
        )

        conn.commit()

        conn.close()

        return render_template(
            "generated_password.html",
            password=password,
            strength=strength
        )

    return render_template(
        "index.html",
        length=length,
        uppercase=uppercase,
        lowercase=lowercase,
        numbers=numbers,
        symbols=symbols
    )


# =========================================================
# USER REGISTRATION
# =========================================================

@app.route("/register", methods=["GET", "POST"])
def register():

    message = ""

    if request.method == "POST":

        name = request.form.get(
            "name",
            ""
        ).strip()

        email = request.form.get(
            "email",
            ""
        ).strip()

        mobile = request.form.get(
            "mobile",
            ""
        ).strip()

        dob = request.form.get(
            "dob",
            ""
        ).strip()

        password = request.form.get(
            "password",
            ""
        )

        conn = get_db_connection()

        cursor = conn.cursor()

        try:

            cursor.execute(
                """
                INSERT INTO users
                (name, email, mobile, dob, password)
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    name,
                    email or None,
                    mobile or None,
                    dob,
                    password
                )
            )

            conn.commit()

            message = (
                "Registration successful! "
                "Please login."
            )

        except sqlite3.IntegrityError:

            message = (
                "Email or Mobile Number "
                "already registered."
            )

        conn.close()

    return render_template(
        "register.html",
        message=message
    )


# =========================================================
# USER LOGIN
# =========================================================

@app.route("/login", methods=["GET", "POST"])
def login():

    message = ""

    if request.method == "POST":

        login_value = request.form.get(
            "login",
            ""
        ).strip()

        password = request.form.get(
            "password",
            ""
        )

        conn = get_db_connection()

        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT *
            FROM users
            WHERE
                (email = ? OR mobile = ?)
                AND password = ?
            """,
            (
                login_value,
                login_value,
                password
            )
        )

        user = cursor.fetchone()

        conn.close()

        if user:

            session["user_id"] = user["id"]

            session["user_name"] = user["name"]

            return redirect("/")

        message = (
            "Invalid Email/Mobile or Password."
        )

    return render_template(
        "login.html",
        message=message
    )


# =========================================================
# FORGOT PASSWORD
# =========================================================

@app.route("/forgot-password", methods=["GET", "POST"])
def forgot_password():

    message = ""

    if request.method == "POST":

        login_value = request.form.get(
            "login",
            ""
        ).strip()

        dob = request.form.get(
            "dob",
            ""
        ).strip()

        new_password = request.form.get(
            "new_password",
            ""
        )

        confirm_password = request.form.get(
            "confirm_password",
            ""
        )


        # DEBUG INFORMATION

        print(
            "FORGOT LOGIN:",
            repr(login_value)
        )

        print(
            "FORGOT DOB:",
            repr(dob)
        )


        # CHECK PASSWORD MATCH

        if new_password != confirm_password:

            message = (
                "Passwords do not match."
            )

            return render_template(
                "forgot_password.html",
                message=message
            )


        # DATABASE CHECK

        conn = get_db_connection()

        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT *
            FROM users
            WHERE
                (
                    email = ?
                    OR mobile = ?
                )
                AND dob = ?
            """,
            (
                login_value,
                login_value,
                dob
            )
        )

        user = cursor.fetchone()


        print(
            "FORGOT USER FOUND:",
            user
        )


        # USER FOUND

        if user:

            cursor.execute(
                """
                UPDATE users
                SET password = ?
                WHERE id = ?
                """,
                (
                    new_password,
                    user["id"]
                )
            )

            conn.commit()

            message = (
                "Password reset successful! "
                "Please login."
            )


        # USER NOT FOUND

        else:

            message = (
                "Details not found. "
                "Please check your information."
            )


        conn.close()


    return render_template(
        "forgot_password.html",
        message=message
    )


# =========================================================
# PROFILE
# =========================================================

@app.route("/profile")
def profile():

    if "user_id" not in session:

        return redirect("/login")

    conn = get_db_connection()

    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT *
        FROM users
        WHERE id = ?
        """,
        (
            session["user_id"],
        )
    )

    user = cursor.fetchone()

    conn.close()

    return render_template(
        "profile.html",
        user=user
    )


# =========================================================
# CHANGE PASSWORD
# =========================================================

@app.route("/change-password", methods=["GET", "POST"])
def change_password():

    if "user_id" not in session:

        return redirect("/login")

    message = ""

    if request.method == "POST":

        current_password = request.form.get(
            "current_password",
            ""
        )

        new_password = request.form.get(
            "new_password",
            ""
        )

        confirm_password = request.form.get(
            "confirm_password",
            ""
        )

        conn = get_db_connection()

        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT password
            FROM users
            WHERE id = ?
            """,
            (
                session["user_id"],
            )
        )

        user = cursor.fetchone()

        if not user:

            message = "User not found."

        elif user["password"] != current_password:

            message = (
                "Current password is incorrect."
            )

        elif new_password != confirm_password:

            message = (
                "New passwords do not match."
            )

        else:

            cursor.execute(
                """
                UPDATE users
                SET password = ?
                WHERE id = ?
                """,
                (
                    new_password,
                    session["user_id"]
                )
            )

            conn.commit()

            message = (
                "Password changed successfully."
            )

        conn.close()

    return render_template(
        "change_password.html",
        message=message
    )


# =========================================================
# PASSWORD HISTORY
# =========================================================

@app.route("/password-history")
def password_history():

    if "user_id" not in session:

        return redirect("/login")

    conn = get_db_connection()

    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT password, created_at
        FROM password_history
        WHERE user_id = ?
        ORDER BY id DESC
        """,
        (
            session["user_id"],
        )
    )

    history = cursor.fetchall()

    conn.close()

    return render_template(
        "password_history.html",
        history=history
    )


# =========================================================
# CLEAR PASSWORD HISTORY
# =========================================================

@app.route("/clear-history", methods=["POST"])
def clear_history():

    if "user_id" not in session:

        return redirect("/login")

    conn = get_db_connection()

    cursor = conn.cursor()

    cursor.execute(
        """
        DELETE FROM password_history
        WHERE user_id = ?
        """,
        (
            session["user_id"],
        )
    )

    conn.commit()

    conn.close()

    return redirect("/password-history")


# =========================================================
# USER LOGOUT
# =========================================================

@app.route("/logout")
def logout():

    session.clear()

    return redirect("/login")


# =========================================================
# ADMIN LOGIN
# =========================================================

@app.route("/admin-login", methods=["GET", "POST"])
def admin_login():

    message = ""

    if request.method == "POST":

        username = request.form.get(
            "username",
            ""
        ).strip()

        password = request.form.get(
            "password",
            ""
        )

        conn = get_db_connection()

        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT *
            FROM admin
            WHERE username = ?
            AND password = ?
            """,
            (
                username,
                password
            )
        )

        admin = cursor.fetchone()

        conn.close()

        if admin:

            session["admin_id"] = admin["id"]

            session["admin_username"] = admin["username"]

            return redirect(
                "/admin-dashboard"
            )

        message = (
            "Invalid admin username "
            "or password."
        )

    return render_template(
        "admin_login.html",
        message=message
    )


# =========================================================
# ADMIN DASHBOARD
# =========================================================

@app.route("/admin-dashboard")
def admin_dashboard():

    if "admin_id" not in session:

        return redirect("/admin-login")

    conn = get_db_connection()

    cursor = conn.cursor()


    # TOTAL USERS

    cursor.execute(
        """
        SELECT COUNT(*) AS total
        FROM users
        """
    )

    total_users = cursor.fetchone()["total"]


    # TOTAL PASSWORDS

    cursor.execute(
        """
        SELECT COUNT(*) AS total
        FROM password_history
        """
    )

    total_passwords = cursor.fetchone()["total"]


    # USER DETAILS

    cursor.execute(
        """
        SELECT
            users.id,
            users.name,
            users.email,
            users.mobile,
            users.dob,
            COUNT(password_history.id)
            AS password_count
        FROM users

        LEFT JOIN password_history

        ON users.id = password_history.user_id

        GROUP BY users.id

        ORDER BY users.id DESC
        """
    )

    users = cursor.fetchall()

    conn.close()

    return render_template(
        "admin_dashboard.html",
        total_users=total_users,
        total_passwords=total_passwords,
        users=users
    )


# =========================================================
# ADMIN LOGOUT
# =========================================================

@app.route("/admin-logout")
def admin_logout():

    session.pop(
        "admin_id",
        None
    )

    session.pop(
        "admin_username",
        None
    )

    return redirect("/admin-login")


# =========================================================
# RUN APPLICATION
# =========================================================

if __name__ == "__main__":

    app.run(debug=True)
