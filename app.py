from flask import Flask, render_template, request, redirect
import string
import random

app = Flask(__name__)

password_history = []


@app.route("/", methods=["GET", "POST"])
def home():
    password = ""
    strength = ""

    if request.method == "POST":
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
                random.choice(characters) for _ in range(length)
            )

            if length < 8:
                strength = "Weak"
            elif length < 12:
                strength = "Medium"
            elif length < 16:
                strength = "Strong"
            else:
                strength = "Very Strong"

            password_history.insert(0, password)

            if len(password_history) > 5:
                password_history.pop()

    return render_template(
        "index.html",
        password=password,
        strength=strength,
        history=password_history
    )


@app.route("/clear-history", methods=["POST"])
def clear_history():
    password_history.clear()
    return redirect("/")


if __name__ == "__main__":
    app.run(debug=True)