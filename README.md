# 📚 Jeddah Library Intelligence Platform

> End-to-end ML pipeline + live dashboard for predicting hourly book rental demand across public library branches in Jeddah, Saudi Arabia.

[![Deploy](https://github.com/FahadAlshehrii/jeddah-library-intelligence/actions/workflows/deploy.yml/badge.svg)](https://github.com/FahadAlshehrii/jeddah-library-intelligence/actions)
![Python](https://img.shields.io/badge/Python-3.11-blue)
![Streamlit](https://img.shields.io/badge/Streamlit-1.35-red)
![Azure](https://img.shields.io/badge/Azure-App_Service-0078D4)
![R2](https://img.shields.io/badge/R²_Score-0.92-brightgreen)

---

## 🎯 Problem Statement

Library management has no reliable way to predict hourly rental demand per branch. This leads to overstaffing during quiet hours and understaffing during peak periods — wasting budget and frustrating visitors.

**This platform solves it:** input any combination of branch, time, and weather conditions → get a predicted rental count + staffing recommendation instantly.

---

## 🏗️ Architecture

![Architecture Diagram](jeddah_architecture_final.png)



---

## 📊 Model Results

| Model | R² | MAE | RMSE |
|---|---|---|---|
| **Neural Network** ⭐ | **0.9311** | **3.99** | **5.52** |
| Random Forest | 0.9205 | 4.28 | 5.93 |
| Linear Regression | 0.8628 | 6.07 | 7.79 |
| Decision Tree | 0.8613 | 5.88 | 7.83 |

Neural Network wins on all three metrics. It captures complex non-linear interactions between hour, temperature, branch, and demand that tree-based models approximate but cannot fully model. Trained with early stopping to prevent overfitting.

> *Note: Neural Network achieves R²=0.9311 on GPU (Colab). On CPU, Random Forest is the best (R²=0.9205). The pipeline automatically selects the best model for your hardware.*
---

##  Dashboard Features

### Tab 1 — Demand Predictor
- Input: branch, hour, day, season, weather conditions, membership type
- Output: predicted hourly rentals + staffing recommendation (1–4 staff)
- Visual: branch-specific hourly demand curve with selected hour marker

### Tab 2 — Branch Analytics
- Total rentals by branch, season, hour, day of week
- Membership type distribution
- Actionable business insights for management

### Tab 3 — Model Comparison
- R², MAE, RMSE across all 4 models
- Top 10 feature importances (Random Forest)
- Written conclusion with management recommendations

---

## 🔑 Key Findings

- **Peak demand:** 16:00–19:00 daily — schedule 3–4 staff during these hours
- **Busiest branch:** Downtown Central — highest total rental volume
- **Weekend effect:** Friday & Saturday show noticeably different patterns (Saudi weekend)
- **Top predictors:** Hour of day, temperature, humidity, and branch location
- **Temperature insight:** Moderate (25–35°C "Warm") days drive the highest demand

---

## 🛠️ Stack

| Layer | Technology |
|---|---|
| Data & ML | Python, Pandas, NumPy, Scikit-learn |
| Visualization | Matplotlib, Seaborn, Plotly |
| Dashboard | Streamlit |
| Containerization | Docker |
| CI/CD | GitHub Actions |
| Cloud Registry | Azure Container Registry |
| Hosting | Azure App Service |

---

## 🏃 Run Locally

```bash
git clone https://github.com/FahadAlshehrii/jeddah-library-intelligence
cd jeddah-library-intelligence

pip install -r requirements.txt

# Run the full ML pipeline (generates model_artifacts.pkl)
python jeddah_library_rentals_SOLUTION.py

# Launch the dashboard
streamlit run dashboard.py
```

---

## 🐳 Docker

```bash
docker build -t jeddah-library-intelligence .
docker run -p 8501:8501 jeddah-library-intelligence
# Open http://localhost:8501
```

---

## 📁 Project Structure

```
jeddah-library-intelligence/
├── jeddah_library_rentals.csv          # Raw dataset
├── jeddah_library_rentals_SOLUTION.py  # Full ML pipeline
├── dashboard.py                        # Streamlit app
├── model_artifacts.pkl                 # Trained model + scaler
├── requirements.txt
├── Dockerfile
├── outputs/                            # EDA plots + comparison CSV
└── .github/
    └── workflows/
        └── deploy.yml                  # CI/CD pipeline
```

---

## 👤 Author

**Fahad Alshehri**
[LinkedIn](https://linkedin.com/in/f-alshehrii) · [GitHub](https://github.com/FahadAlshehri)

---

> *This architecture is modular and can be applied to any tabular demand forecasting problem in the public services sector — retail, healthcare, transportation, and more.*
