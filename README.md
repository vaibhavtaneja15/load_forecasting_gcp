# Electrical Load Forecasting using Artificial Neural Network (GCP)

## Project Overview
This project implements a **short-term electrical load forecasting system** using an **Artificial Neural Network (ANN)** developed in **PyTorch** and deployed on **Google Cloud Platform (GCP)**.

The system predicts electrical load (in megawatts) using weather variables, calendar features, and previous load values. The solution is designed following **cloud-native and production-ready principles**, integrating multiple GCP services for scalability, reliability, and monitoring.

---

## Machine Learning Model
- **Framework:** PyTorch  
- **Model Type:** Artificial Neural Network (ANN)  
- **Architecture:** 11 → 90 → 90 → 1  
- **Activation Function:** Tanh  
- **Loss Function:** Smooth L1 Loss  
- **Optimizer:** LBFGS  

### Input Features
1. Day (normalized)  
2. Month (normalized)  
3. Hour (normalized)  
4. Temperature  
5. Humidity  
6. Weekday indicator  
7. Weekend / holiday indicator  
8. Summer season indicator  
9. Monsoon season indicator  
10. Winter season indicator  
11. Previous electrical load (autoregressive feature)  

### Output
- Predicted electrical load (MW)

---

## Model Performance
- **Test Mean Squared Error (MSE):** ~0.0028  
- **Test R² Score:** ~0.77  

The inclusion of previous load as an input enables **state-dependent forecasting**, making predictions more realistic for real-world power system behavior.

---

## Cloud Architecture (Google Cloud Platform)

| Service | Purpose |
|-------|--------|
| Cloud Run | Hosting the Flask-based inference API |
| Cloud Storage | Secure storage of trained ANN model artifacts |
| BigQuery | Logging predictions for time-series analysis |
| Cloud Build | Container build and deployment pipeline |
| Cloud Logging | Application monitoring and debugging |
| Vertex AI | Future-ready model training and lifecycle management |

---

## System Workflow
User Interface
↓
Flask API (Cloud Run)
↓
ANN Inference (PyTorch)
↓
Predicted Load (MW)
↓
BigQuery (Prediction Logging)
↓
Cloud Logging (Monitoring)


---

## Local Execution (Docker)

```bash
docker build -t load-forecasting-app .
docker run -p 8080:8080 load-forecasting-app
Access locally at:

http://localhost:8080
Live Deployment
The application is deployed on Google Cloud Run and is publicly accessible at:

https://load-forecasting-app-105738184753.asia-south1.run.app
Key Features
End-to-end machine learning pipeline from training to deployment

Cloud-native and serverless deployment architecture

Autoregressive load forecasting using previous load values

Scalable and cost-efficient inference using Cloud Run

Clean version control with model artifacts stored outside GitHub



Notes
Model artifacts are intentionally excluded from the GitHub repository and are stored securely in Google Cloud Storage, following industry best practices for reproducibility and security.


---

### What to do next
```powershell
git add README.md
git commit -m "Add professional project README"
git push
