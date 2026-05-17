import pandas as pd
import numpy as np
import torch
import torch.nn as nn
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import (classification_report, confusion_matrix,
                             roc_auc_score, roc_curve, f1_score,
                             precision_score, recall_score)
import matplotlib.pyplot as plt
import seaborn as sns
import joblib
import time

print("PRISM — ML Model Comparison")
print("=" * 50)

# ── Load Dataset ──────────────────────────────────
print("Loading dataset...")
try:
    df = pd.read_parquet("datasets/UNSW_NB15_training-set.parquet")
    print(f"Loaded UNSW-NB15 — {len(df)} records")
except:
    df = pd.read_csv("datasets/Train_Test_Network.csv")
    print(f"Loaded TON_IoT — {len(df)} records")

# ── Preprocess ────────────────────────────────────
df_numeric = df.select_dtypes(include=[np.number]).fillna(0)

label_col = None
for col in ['label', 'Label', 'attack_cat', 'Attack', 'type']:
    if col in df_numeric.columns:
        label_col = col
        break

if label_col:
    y = (df_numeric[label_col] != 0).astype(int)
    X = df_numeric.drop(columns=[label_col])
else:
    print("No label column found — cannot compare models.")
    exit()

scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# ── Isolation Forest ──────────────────────────────
print("\nEvaluating Isolation Forest...")
start = time.time()
iso_model = joblib.load("ml-model/isolation_forest_model.pkl")
iso_predictions = iso_model.predict(X_scaled)
iso_binary = [1 if p == -1 else 0 for p in iso_predictions]
iso_scores = iso_model.decision_function(X_scaled)
iso_time = round(time.time() - start, 2)

iso_precision = round(precision_score(y, iso_binary, zero_division=0), 3)
iso_recall = round(recall_score(y, iso_binary, zero_division=0), 3)
iso_f1 = round(f1_score(y, iso_binary, zero_division=0), 3)
try:
    iso_auc = round(roc_auc_score(y, -iso_scores), 3)
except:
    iso_auc = "N/A"

print(f"Precision: {iso_precision} | Recall: {iso_recall} | F1: {iso_f1} | AUC: {iso_auc}")

# ── Autoencoder ───────────────────────────────────
print("\nEvaluating Autoencoder...")

input_dim = X_scaled.shape[1]

class Autoencoder(nn.Module):
    def __init__(self, input_dim):
        super(Autoencoder, self).__init__()
        self.encoder = nn.Sequential(
            nn.Linear(input_dim, 64), nn.ReLU(),
            nn.Linear(64, 32), nn.ReLU(),
            nn.Linear(32, 16)
        )
        self.decoder = nn.Sequential(
            nn.Linear(16, 32), nn.ReLU(),
            nn.Linear(32, 64), nn.ReLU(),
            nn.Linear(64, input_dim)
        )
    def forward(self, x):
        return self.decoder(self.encoder(x))

ae_model = Autoencoder(input_dim)
ae_model.load_state_dict(torch.load("ml-model/autoencoder_model.pth",
                                     weights_only=True))
ae_model.eval()
threshold = np.load("ml-model/autoencoder_threshold.npy")

start = time.time()
X_tensor = torch.FloatTensor(X_scaled)
with torch.no_grad():
    reconstructed = ae_model(X_tensor)
    errors = torch.mean((X_tensor - reconstructed) ** 2, dim=1).numpy()
ae_binary = (errors > threshold).astype(int)
ae_time = round(time.time() - start, 2)

ae_precision = round(precision_score(y, ae_binary, zero_division=0), 3)
ae_recall = round(recall_score(y, ae_binary, zero_division=0), 3)
ae_f1 = round(f1_score(y, ae_binary, zero_division=0), 3)
try:
    ae_auc = round(roc_auc_score(y, errors), 3)
except:
    ae_auc = "N/A"

print(f"Precision: {ae_precision} | Recall: {ae_recall} | F1: {ae_f1} | AUC: {ae_auc}")

# ── Comparison Table ──────────────────────────────
print("\n" + "=" * 50)
print("MODEL COMPARISON RESULTS")
print("=" * 50)
print(f"{'Metric':<20} {'Isolation Forest':<20} {'Autoencoder':<20}")
print("-" * 60)
print(f"{'Precision':<20} {iso_precision:<20} {ae_precision:<20}")
print(f"{'Recall':<20} {iso_recall:<20} {ae_recall:<20}")
print(f"{'F1 Score':<20} {iso_f1:<20} {ae_f1:<20}")
print(f"{'ROC-AUC':<20} {iso_auc:<20} {ae_auc:<20}")
print(f"{'Inference Time(s)':<20} {iso_time:<20} {ae_time:<20}")
print("=" * 50)

# ── Bar Chart Comparison ──────────────────────────
metrics = ['Precision', 'Recall', 'F1 Score']
iso_values = [iso_precision, iso_recall, iso_f1]
ae_values = [ae_precision, ae_recall, ae_f1]

x = np.arange(len(metrics))
width = 0.35

fig, ax = plt.subplots(figsize=(8, 5))
bars1 = ax.bar(x - width/2, iso_values, width, label='Isolation Forest',
               color='steelblue')
bars2 = ax.bar(x + width/2, ae_values, width, label='Autoencoder',
               color='orange')

ax.set_ylabel('Score')
ax.set_title('PRISM — Model Comparison: Isolation Forest vs Autoencoder')
ax.set_xticks(x)
ax.set_xticklabels(metrics)
ax.set_ylim(0, 1)
ax.legend()
ax.bar_label(bars1, padding=3, fmt='%.3f')
ax.bar_label(bars2, padding=3, fmt='%.3f')
plt.tight_layout()
plt.savefig("ml-model/model_comparison_chart.png")
print("\nComparison chart saved!")

# ── ROC Curves ────────────────────────────────────
plt.figure(figsize=(8, 5))
try:
    iso_fpr, iso_tpr, _ = roc_curve(y, -iso_scores)
    plt.plot(iso_fpr, iso_tpr, color='steelblue',
             label=f'Isolation Forest (AUC = {iso_auc})')
except:
    pass
try:
    ae_fpr, ae_tpr, _ = roc_curve(y, errors)
    plt.plot(ae_fpr, ae_tpr, color='orange',
             label=f'Autoencoder (AUC = {ae_auc})')
except:
    pass

plt.plot([0, 1], [0, 1], 'k--', label='Random Classifier')
plt.xlabel('False Positive Rate')
plt.ylabel('True Positive Rate')
plt.title('PRISM — ROC Curve Comparison')
plt.legend()
plt.tight_layout()
plt.savefig("ml-model/roc_curve_comparison.png")
print("ROC curve saved!")

print("\nModel comparison complete!")