import os
from flask import Flask, render_template, request, jsonify
from chatbot import get_response, get_medicine_info
from keywords import get_specialist
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = "static/uploads"
app.config["MAX_CONTENT_LENGTH"] = 10 * 1024 * 1024  # 10MB max
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "webp"}

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    user_message = request.form.get("message", "")
    image_path = None

    if "image" in request.files:
        file = request.files["image"]
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            image_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
            file.save(image_path)

    reply = get_response(user_message, image_path)
    specialist = get_specialist(user_message)
    return jsonify({"reply": reply, "specialist": specialist})

@app.route("/medicine", methods=["POST"])
def medicine():
    data = request.get_json()
    name = data.get("name", "")
    info = get_medicine_info(name)
    return jsonify({"info": info})

@app.route("/specialist", methods=["POST"])
def specialist_route():
    data = request.get_json()
    text = data.get("text", "")
    specialist = get_specialist(text)
    return jsonify({"specialist": specialist})

if __name__ == "__main__":
    os.makedirs("static/uploads", exist_ok=True)
    app.run(debug=True)
