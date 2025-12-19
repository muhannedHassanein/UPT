from flask import Flask, jsonify, render_template, request
import requests
import torch
from datetime import datetime

app = Flask(__name__)

# ================= Firebase config =================
DATABASE_URL = "https://upt-prototype-default-rtdb.firebaseio.com/sensors.json"

# ================= AI model =======================
model = torch.jit.load("AI model/RandomForest_Improved.pt")
model.eval()

# ================= Routes =========================

@app.route("/")
def home():
    return render_template("index.html")


@app.route("/dashboard")
def dashboard():
    return render_template("dashboard.html")


@app.route("/prediction")
def prediction_page():
    return render_template("predict.html")


@app.route("/about")
def about_page():
    return render_template("About_upt.html")


# --------- Fetch Latest Data ---------
@app.route("/data")
def get_latest_data():
    try:
        response = requests.get(DATABASE_URL)
        raw_data = response.json()

        if not raw_data:
            return jsonify({"error": "No data found"})

        if isinstance(raw_data, dict):
            last_key = list(raw_data.keys())[-1]
            last_entry = raw_data[last_key]
        else:
            last_entry = raw_data[-1]

        return jsonify({
            "temperature": last_entry.get("temperature", 0),
            "gas": last_entry.get("gas", 0),
            "light": last_entry.get("light", 0),
            "motion": last_entry.get("motion", 0),
            "time": last_entry.get("time", "")
        })

    except Exception as e:
        return jsonify({"error": str(e)})


# --------- Fetch All Data ---------
@app.route("/all-data")
def get_all_data():
    try:
        response = requests.get(DATABASE_URL)
        data = response.json()

        all_readings = []

        if isinstance(data, dict):
            for key, entry in data.items():

                # 🔥 تجاهل أي قيمة مش dict
                if not isinstance(entry, dict):
                    continue

                all_readings.append({
                    "temperature": float(entry.get("temperature", 0)),
                    "gas": int(entry.get("gas", 0)),
                    "light": int(entry.get("light", 0)),
                    "motion": int(entry.get("motion", 0)),
                    "time": entry.get("time", "")
                })

        elif isinstance(data, list):
            for entry in data:
                if not isinstance(entry, dict):
                    continue

                all_readings.append({
                    "temperature": float(entry.get("temperature", 0)),
                    "gas": int(entry.get("gas", 0)),
                    "light": int(entry.get("light", 0)),
                    "motion": int(entry.get("motion", 0)),
                    "time": entry.get("time", "")
                })

        return jsonify(all_readings)

    except Exception as e:
        return jsonify({"error": str(e)})

# --------- AI Prediction ---------
@app.route("/predict", methods=["GET", "POST"])
def predict():
    if request.method == "GET":
        return render_template("predict.html")

    try:
        # ===== Read form data =====
        depth_m = float(request.form["depth_m"])
        temp_c = float(request.form["temp_c"])
        pH = float(request.form["pH"])
        salinity = float(request.form["salinity"])
        dissolved_oxygen = float(request.form["dissolved_oxygen"])
        co2_ppm = float(request.form["co2_ppm"])
        light_intensity = float(request.form["light_intensity"])
        turbidity = float(request.form["turbidity"])
        change_factor = float(request.form["change_factor"])

        now = datetime.now()

        # ===== EXACT model features (10) =====
        features = [
            dissolved_oxygen,
            turbidity,
            depth_m,
            light_intensity,
            temp_c,
            change_factor,
            now.month,
            pH,
            salinity,
            co2_ppm
        ]

        input_tensor = torch.tensor(features, dtype=torch.float32).unsqueeze(0)

        # ===== Prediction =====
        with torch.no_grad():
            output = model(input_tensor)
            pred = torch.argmax(output).item()

        classes = ["Stable", "Unstable", "Dangerous"]
        result = classes[pred]

        return render_template("predict.html", result=result)

    except Exception as e:
        return render_template("predict.html", result=f"Error: {str(e)}")


# ================= Run server =====================
if __name__ == "__main__":
    app.run()
