import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import classification_report, confusion_matrix, roc_auc_score
import matplotlib.pyplot as plt
import seaborn as sns
import joblib
import os

print("PRISM — Isolation Forest Anomaly Detection")
print("=" * 50)

# ── Load Dataset ──────────────────────────────────
print("Loading dataset...")

try:
    df = pd.read_parquet("datasets/UNSW_NB15_training-set.parquet")
    print(f"Loaded UNSW-NB15 — {len(df)} records")
except:
    try:
        df = pd.read_csv("datasets/Train_Test_Network.csv")
        print(f"Loaded TON_IoT — {len(df)} records")
    except Exception as e:
        print(f"Error loading dataset: {e}")
        exit()

print(f"Columns: {list(df.columns)}")
print(f"Shape: {df.shape}")

# ── Preprocess ────────────────────────────────────
print("\nPreprocessing data...")

# Drop non-numeric columns
df_numeric = df.select_dtypes(include=[np.number])

# Fill missing values
df_numeric = df_numeric.fillna(0)

# Separate label column if it exists
label_col = None
for col in ['label', 'Label', 'attack_cat', 'Attack', 'type']:
    if col in df_numeric.columns:
        label_col = col
        break

if label_col:
    y = df_numeric[label_col]
    X = df_numeric.drop(columns=[label_col])
else:
    X = df_numeric
    y = None

# Scale features
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)
print(f"Features after preprocessing: {X.shape[1]}")

# ── Train Model ───────────────────────────────────
print("\nTraining Isolation Forest model...")

model = IsolationForest(
    n_estimators=100,
    contamination=0.1,
    random_state=42,
    verbose=1
)

model.fit(X_scaled)
print("Training complete!")

# ── Predict ───────────────────────────────────────
print("\nRunning predictions...")
predictions = model.predict(X_scaled)
anomaly_scores = model.decision_function(X_scaled)

# Convert: Isolation Forest returns 1 (normal) and -1 (anomaly)
predictions_binary = [1 if p == -1 else 0 for p in predictions]
total_anomalies = sum(predictions_binary)
print(f"Anomalies detected: {total_anomalies} out of {len(predictions_binary)}")

# ── Evaluation ────────────────────────────────────
if y is not None:
    print("\nModel Evaluation:")
    y_binary = (y != 0).astype(int)
    print(confusion_matrix(y_binary, predictions_binary))
    print(classification_report(y_binary, predictions_binary))

# ── Confusion Matrix Plot ─────────────────────────
if y is not None:
    plt.figure(figsize=(6, 4))
    cm = confusion_matrix(y_binary, predictions_binary)
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues',
                xticklabels=['Normal', 'Anomaly'],
                yticklabels=['Normal', 'Anomaly'])
    plt.title('Isolation Forest — Confusion Matrix')
    plt.ylabel('Actual')
    plt.xlabel('Predicted')
    plt.tight_layout()
    plt.savefig("ml-model/isolation_forest_confusion_matrix.png")
    print("Confusion matrix saved!")

# ── Anomaly Score Distribution ────────────────────
plt.figure(figsize=(8, 4))
plt.hist(anomaly_scores, bins=50, color='steelblue', edgecolor='black')
plt.axvline(x=0, color='red', linestyle='--', label='Threshold')
plt.title('Isolation Forest — Anomaly Score Distribution')
plt.xlabel('Anomaly Score')
plt.ylabel('Frequency')
plt.legend()
plt.tight_layout()
plt.savefig("ml-model/isolation_forest_scores.png")
print("Score distribution plot saved!")

# ── Save Model ────────────────────────────────────
os.makedirs("ml-model", exist_ok=True)
joblib.dump(model, "ml-model/isolation_forest_model.pkl")
joblib.dump(scaler, "ml-model/scaler.pkl")
print("\nModel saved to ml-model/isolation_forest_model.pkl")
print("Scaler saved to ml-model/scaler.pkl")
print("\nIsolation Forest training complete!")