import pandas as pd
import numpy as np
import torch
import torch.nn as nn
from torch.utils.data import DataLoader, TensorDataset
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import classification_report, confusion_matrix
import matplotlib.pyplot as plt
import seaborn as sns
import joblib
import os

print("PRISM — Autoencoder Anomaly Detection")
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

# ── Preprocess ────────────────────────────────────
print("\nPreprocessing data...")

df_numeric = df.select_dtypes(include=[np.number])
df_numeric = df_numeric.fillna(0)

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

scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)
print(f"Features: {X.shape[1]}")

# ── Build Autoencoder ─────────────────────────────
input_dim = X_scaled.shape[1]

class Autoencoder(nn.Module):
    def __init__(self, input_dim):
        super(Autoencoder, self).__init__()
        self.encoder = nn.Sequential(
            nn.Linear(input_dim, 64),
            nn.ReLU(),
            nn.Linear(64, 32),
            nn.ReLU(),
            nn.Linear(32, 16)
        )
        self.decoder = nn.Sequential(
            nn.Linear(16, 32),
            nn.ReLU(),
            nn.Linear(32, 64),
            nn.ReLU(),
            nn.Linear(64, input_dim)
        )

    def forward(self, x):
        encoded = self.encoder(x)
        decoded = self.decoder(encoded)
        return decoded

model = Autoencoder(input_dim)
criterion = nn.MSELoss()
optimizer = torch.optim.Adam(model.parameters(), lr=0.001)

# ── Train ─────────────────────────────────────────
print("\nTraining Autoencoder...")

X_tensor = torch.FloatTensor(X_scaled)
dataset = TensorDataset(X_tensor)
dataloader = DataLoader(dataset, batch_size=256, shuffle=True)

losses = []
epochs = 20

for epoch in range(epochs):
    epoch_loss = 0
    for batch in dataloader:
        inputs = batch[0]
        outputs = model(inputs)
        loss = criterion(outputs, inputs)
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()
        epoch_loss += loss.item()
    avg_loss = epoch_loss / len(dataloader)
    losses.append(avg_loss)
    print(f"Epoch {epoch+1}/{epochs} — Loss: {avg_loss:.6f}")

print("Training complete!")

# ── Detect Anomalies ──────────────────────────────
print("\nDetecting anomalies...")

model.eval()
with torch.no_grad():
    reconstructed = model(X_tensor)
    reconstruction_errors = torch.mean(
        (X_tensor - reconstructed) ** 2, dim=1
    ).numpy()

# Set threshold at 95th percentile
threshold = np.percentile(reconstruction_errors, 95)
predictions_binary = (reconstruction_errors > threshold).astype(int)
total_anomalies = sum(predictions_binary)
print(f"Threshold: {threshold:.6f}")
print(f"Anomalies detected: {total_anomalies} out of {len(predictions_binary)}")

# ── Evaluation ────────────────────────────────────
if y is not None:
    print("\nModel Evaluation:")
    y_binary = (y != 0).astype(int)
    print(confusion_matrix(y_binary, predictions_binary))
    print(classification_report(y_binary, predictions_binary))

    # Confusion Matrix Plot
    plt.figure(figsize=(6, 4))
    cm = confusion_matrix(y_binary, predictions_binary)
    sns.heatmap(cm, annot=True, fmt='d', cmap='Oranges',
                xticklabels=['Normal', 'Anomaly'],
                yticklabels=['Normal', 'Anomaly'])
    plt.title('Autoencoder — Confusion Matrix')
    plt.ylabel('Actual')
    plt.xlabel('Predicted')
    plt.tight_layout()
    plt.savefig("ml-model/autoencoder_confusion_matrix.png")
    print("Confusion matrix saved!")

# ── Training Loss Plot ────────────────────────────
plt.figure(figsize=(8, 4))
plt.plot(range(1, epochs+1), losses, marker='o', color='orange')
plt.title('Autoencoder — Training Loss per Epoch')
plt.xlabel('Epoch')
plt.ylabel('Loss')
plt.tight_layout()
plt.savefig("ml-model/autoencoder_training_loss.png")
print("Training loss plot saved!")

# ── Reconstruction Error Plot ─────────────────────
plt.figure(figsize=(8, 4))
plt.hist(reconstruction_errors, bins=50, color='orange', edgecolor='black')
plt.axvline(x=threshold, color='red', linestyle='--', label=f'Threshold: {threshold:.4f}')
plt.title('Autoencoder — Reconstruction Error Distribution')
plt.xlabel('Reconstruction Error')
plt.ylabel('Frequency')
plt.legend()
plt.tight_layout()
plt.savefig("ml-model/autoencoder_reconstruction_errors.png")
print("Reconstruction error plot saved!")

# ── Save Model ────────────────────────────────────
torch.save(model.state_dict(), "ml-model/autoencoder_model.pth")
joblib.dump(scaler, "ml-model/autoencoder_scaler.pkl")
np.save("ml-model/autoencoder_threshold.npy", threshold)
print("\nModel saved to ml-model/autoencoder_model.pth")
print(f"Threshold saved: {threshold:.6f}")
print("\nAutoencoder training complete!")