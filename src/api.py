from flask import Flask, request, jsonify
from flask_cors import CORS
import tensorflow as tf
import numpy as np
from PIL import Image
import io

app = Flask(__name__)
CORS(
    app,
    supports_credentials=True,
    resources={r"/*": {"origins": ["https://medcheck-nzla.onrender.com"]}}
)

model = tf.keras.models.load_model("model.keras")
dummy = np.zeros((1, 224, 224, 3), dtype=np.float32)
_ = model.predict(dummy)

IMG_SIZE = (224, 224)
THRESHOLD = 0.40

def preprocess(image):
    image = image.resize(IMG_SIZE)
    image = np.array(image).astype(np.float32)

    # MobileNetV2 normalization
    image = (image / 127.5) - 1.0

    image = np.expand_dims(image, axis=0)
    return image


@app.route("/")
def home():
    return "API running"

@app.route("/predict", methods=["POST"])
def predict():

    if "file" not in request.files:
        return "No file uploaded", 400

    file = request.files["file"]

    try:
        image = Image.open(io.BytesIO(file.read())).convert("RGB")
    except:
        return "Invalid image", 400

    img = preprocess(image)

    pred = model.predict(img)[0][0]

    label = "Suspicious" if pred > THRESHOLD else "Authentic"
    confidence = pred if label == "Suspicious" else (1 - pred)

    return jsonify({
        "prediction": label,
        "confidence": round(float(confidence), 4),
        "raw_score": round(float(pred), 4)
    })


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)