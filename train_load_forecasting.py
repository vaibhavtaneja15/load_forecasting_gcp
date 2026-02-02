import pandas as pd
import numpy as np
import torch
import torch.nn as nn
from sklearn.metrics import mean_squared_error, r2_score
from model import LoadForecastingANN
from google.cloud import storage
import os

torch.manual_seed(42)
np.random.seed(42)

BUCKET = "load-forecasting-models-2026"

def load_data():
    X_df = pd.read_excel("normalized_predictors_train.xlsx")
    y_df = pd.read_excel("normalized_responses_train.xlsx")

    X_df["Date"] = pd.to_datetime(X_df["Date"])
    X_df["Time"] = pd.to_datetime(X_df["Time"], errors="coerce")

    X_df["date_norm"] = X_df["Date"].dt.day / 31
    X_df["month_norm"] = X_df["Date"].dt.month / 12
    X_df["time_norm"] = X_df["Time"].dt.hour.fillna(0) / 23

    y_df["prev_load"] = y_df.iloc[:, 0].shift(1)

    X_df = X_df.iloc[1:].reset_index(drop=True)
    y_df = y_df.dropna().reset_index(drop=True)

    temp_col = [c for c in X_df.columns if "temp" in c.lower()][0]
    hum_col = [c for c in X_df.columns if "humid" in c.lower()][0]

    X = X_df[
        ["date_norm", "month_norm", "time_norm",
         temp_col, hum_col,
         "Weekend/Public Holiday", "Weekday",
         "Summer", "Monsoon", "Winter"]
    ].astype(np.float32)

    X["prev_load"] = y_df["prev_load"].astype(np.float32)
    y = y_df.iloc[:, 0].astype(np.float32).values

    return X.values, y

def split(X, y):
    n = len(X)
    return X[:int(.7*n)], y[:int(.7*n)], X[int(.7*n):int(.85*n)], y[int(.7*n):int(.85*n)], X[int(.85*n):], y[int(.85*n):]

def train(model, Xtr, ytr, Xv, yv):
    opt = torch.optim.LBFGS(model.parameters(), lr=0.8)
    loss_fn = nn.SmoothL1Loss()

    best = 1e9
    for _ in range(200):
        def closure():
            opt.zero_grad()
            loss = loss_fn(model(Xtr), ytr)
            loss.backward()
            return loss
        opt.step(closure)

        with torch.no_grad():
            val = loss_fn(model(Xv), yv).item()
            if val < best:
                best = val
                torch.save(model.state_dict(), "best.pth")

    model.load_state_dict(torch.load("best.pth"))
    return model

def upload_to_gcs(local, bucket, remote):
    client = storage.Client()
    client.bucket(bucket).blob(remote).upload_from_filename(local)

if __name__ == "__main__":
    X, y = load_data()
    Xtr, ytr, Xv, yv, Xt, yt = split(X, y)

    model = LoadForecastingANN()
    model = train(
        model,
        torch.FloatTensor(Xtr),
        torch.FloatTensor(ytr).view(-1,1),
        torch.FloatTensor(Xv),
        torch.FloatTensor(yv).view(-1,1)
    )

    with torch.no_grad():
        preds = model(torch.FloatTensor(Xt))

    mse = mean_squared_error(yt, preds.numpy())
    r2 = r2_score(yt, preds.numpy())

    torch.save({
        "model_state_dict": model.state_dict(),
        "input_size": 11,
        "hidden_size": 90,
        "output_size": 1,
        "mse": mse,
        "r2": r2
    }, "load_model.pth")

    upload_to_gcs("load_model.pth", BUCKET, "models/load_model.pth")

    if "AIP_MODEL_DIR" in os.environ:
        print(f"VERTEX_METRIC mse={mse}")
        print(f"VERTEX_METRIC r2={r2}")
