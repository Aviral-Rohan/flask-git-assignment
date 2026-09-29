import json
import os

import certifi
from dotenv import load_dotenv
from flask import Flask, jsonify, redirect, render_template, request, url_for
from pymongo import MongoClient
from pymongo.errors import PyMongoError

# Load secret values (like the MongoDB password) from the .env file
load_dotenv()

app = Flask(__name__)

DATA_FILE = os.path.join(os.path.dirname(__file__), "data.json")
MONGO_URI = os.getenv("MONGO_URI")


def get_collection():
    """Connect to MongoDB Atlas and return the 'users' collection."""
    if not MONGO_URI:
        raise RuntimeError("MONGO_URI is missing. Add it to your .env file.")
    client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000, tlsCAFile=certifi.where())
    return client["flask_assignment"]["users"]


# ---------- Task 1: JSON API route ----------
@app.route("/api")
def api():
    with open(DATA_FILE) as f:
        data = json.load(f)
    return jsonify(data)


# ---------- Task 3 (master_1): To-Do page ----------
@app.route("/todo")
def todo():
    return render_template("todo.html")


# ---------- Task 2: Form that saves to MongoDB Atlas ----------
@app.route("/", methods=["GET", "POST"])
def form():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip()

        if not name or not email:
            return render_template("index.html", error="Name and Email are both required.",
                                   name=name, email=email)
        try:
            get_collection().insert_one({"name": name, "email": email})
            return redirect(url_for("success"))
        except (PyMongoError, RuntimeError) as e:
            # Stay on the same page and show the error
            return render_template("index.html", error=str(e), name=name, email=email)

    return render_template("index.html")


@app.route("/success")
def success():
    return render_template("success.html")


if __name__ == "__main__":
    app.run(debug=True, port=5000)
