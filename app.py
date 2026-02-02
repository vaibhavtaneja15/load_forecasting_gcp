from flask import Flask, request, jsonify, render_template
from datetime import datetime
import logging

from predict_load import predict_load
from google.cloud import bigquery

# ================= APP INIT =================
app = Flask(__name__, template_folder="templates", static_folder="static")

# ================= LOGGING (Cloud Logging auto-captures this) =================
logging.basicConfig(level=logging.INFO)

# ================= BIGQUERY =================
bq_client = bigquery.Client()
BQ_TABLE = "load_forecasting.predictions"   # dataset.table

# ================= NORMALIZATION CONSTANTS =================
TEMP_MIN, TEMP_MAX = 5.3, 46.2
HUM_MIN, HUM_MAX = 5.0, 100.0
last_load_norm = 0.5  # initial previous load (cold start)

def minmax(x, xmin, xmax):
    return (x - xmin) / (xmax - xmin)

# ================= ROUTES =================

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/methodology")
def methodology():
    return render_template("methodology.html")

@app.route("/predict", methods=["POST"])
def predict():
    global last_load_norm

    try:
        data = request.get_json()
        date = datetime.strptime(data["date"], "%Y-%m-%d")

        # -------- INPUT VECTOR (MUST MATCH TRAINING ORDER) --------
        x = [
            date.day / 31,
            date.month / 12,
            14 / 23,  # default hour
            minmax(float(data["temperature"]), TEMP_MIN, TEMP_MAX),
            minmax(float(data["humidity"]), HUM_MIN, HUM_MAX),
            1 if data["daytype"] == "weekend" else 0,
            1 if data["daytype"] == "weekday" else 0,
            1 if data["season"] == "summer" else 0,
            1 if data["season"] == "monsoon" else 0,
            1 if data["season"] == "winter" else 0,
            last_load_norm
        ]

        # -------- MODEL PREDICTION --------
        mw = predict_load(x)

        # Update rolling previous load
        last_load_norm = last_load_norm * 0.7 + (mw / 9000) * 0.3

        # -------- BIGQUERY LOGGING --------
        row = [{
            "date": data["date"],
            "temperature": float(data["temperature"]),
            "humidity": float(data["humidity"]),
            "season": data["season"],
            "daytype": data["daytype"],
            "predicted_load": float(mw),
            "timestamp": datetime.utcnow().isoformat()

        }]

        errors = bq_client.insert_rows_json(BQ_TABLE, row)
        if errors:
            logging.error(f"BigQuery insert error: {errors}")

        logging.info("Prediction successful and logged")

        return jsonify({"predicted_load": round(mw, 2)})

    except Exception as e:
        logging.error("Prediction failed", exc_info=True)
        return jsonify({"error": str(e)}), 500


# ================= ENTRY POINT =================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
