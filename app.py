from flask import Flask, render_template, request, redirect, url_for, flash
import requests
import os

app = Flask(__name__)

app.secret_key = os.getenv("FLASK_SECRET_KEY")

API_URL = "http://127.0.0.1:8000/analyze"

@app.route("/", methods=["GET", "POST"])
def index():
    result = None
    if request.method == "POST":
        file = request.files.get("file")
        main_symptoms = request.form.get("main_symptoms")
        additional_symptoms = request.form.get("additional_symptoms")
        allergies = request.form.get("allergies")

        if not file:
            flash("Please upload a file.")
            return redirect(request.url)

        data = {
            "main_symptoms": main_symptoms,
            "additional_symptoms": additional_symptoms,
            "allergies": allergies
        }

        files = {"file": (file.filename, file.stream, file.content_type)}
        try:
            response = requests.post(API_URL, data=data, files=files)
            response.raise_for_status()
            result = response.json()
        except Exception as e:
            result = {"error": str(e)}

    return render_template("index.html", result=result)

if __name__ == "__main__":
    app.run(debug=True)
