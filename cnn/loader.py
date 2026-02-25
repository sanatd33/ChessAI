import torch
import torch.nn as nn
import torch.optim as optim
import matplotlib.pyplot as plt

from torch.utils.data import Dataset, DataLoader

class ChessDataset(Dataset):
    def __init__(self, examples):
        self.data = examples

    def __len__(self):
        return len(self.data)

    def __getitem__(self, idx):
        tensor, value = self.data[idx]
        return tensor.clone().detach(), torch.tensor([value], dtype=torch.float32)
    
def weighted_mse_loss(pred, target):
    # Increase weight for losses
    weight = torch.where(target < 0, 2.0, 1.0)
    return ((pred - target) ** 2 * weight).mean()

def train_model(model: nn.Module, data, device, epochs=50, batch_size=8192, patience=10):
    split = int(0.9 * len(data))
    train_data = data[:split]
    val_data = data[split:]

    train_loader = DataLoader(ChessDataset(train_data), batch_size=batch_size, shuffle=True)
    val_loader = DataLoader(ChessDataset(val_data), batch_size=batch_size, shuffle=False)

    optimizer = optim.Adam(model.parameters(), lr=1e-3)
    scheduler = torch.optim.lr_scheduler.ReduceLROnPlateau(optimizer, mode='min', patience=3, factor=0.5)
    loss_fn = weighted_mse_loss

    scaler = torch.amp.GradScaler('cuda')
    model = model.to(device, memory_format=torch.channels_last)

    best_val_loss = float('inf')
    epochs_no_improve = 0

    for epoch in range(epochs):
        model.train()
        total_loss = 0

        for x, y in train_loader:
            x = x.to(device, torch.float32, memory_format=torch.channels_last)
            y = y.to(device)
            optimizer.zero_grad()

            with torch.amp.autocast('cuda'):
                out = model(x)
                loss = loss_fn(out, y)

            scaler.scale(loss).backward()
            scaler.step(optimizer)
            scaler.update()

            total_loss += loss.item() * x.size(0)

        avg_train_loss = total_loss / len(train_loader.dataset)

        # Validation
        model.eval()
        val_loss = 0.0
        val_mae = 0.0

        with torch.no_grad():
            for x, y in val_loader:
                x = x.to(device, torch.float32)
                y = y.to(device)
                out = model(x)
                val_loss += loss_fn(out, y).item() * x.size(0)
                val_mae += (out - y).abs().sum().item()

        val_loss /= len(val_loader.dataset)
        val_mae /= len(val_loader.dataset)
        scheduler.step(val_loss)


        print(f"Epoch {epoch+1}: Train Loss = {avg_train_loss:.4f} | Val Loss = {val_loss:.4f} | Val MAE = {val_mae:.4f}")

        if val_loss < best_val_loss:
            best_val_loss = val_loss
            epochs_no_improve = 0
            torch.save(model.state_dict(), "best_model.pt")
            print("New best model saved.")
        else:
            epochs_no_improve += 1
            if epochs_no_improve >= patience:
                print("Early stopping triggered.")
                break

    model.load_state_dict(torch.load("best_model.pt"))
    model.eval()
    preds, targets = [], []
    with torch.no_grad():
        for x, y in val_loader:
            x = x.to(device, torch.float32)
            out = model(x).cpu().numpy()
            preds.extend(out.flatten())
            targets.extend(y.cpu().numpy().flatten())

    plt.figure(figsize=(6, 6))
    plt.scatter(targets, preds, s=1, alpha=0.3)
    plt.plot([min(targets), max(targets)], [min(targets), max(targets)], 'r--')
    plt.xlabel("True CP")
    plt.ylabel("Predicted CP")
    plt.title("Model Predictions vs True Centipawns")
    plt.grid(True)
    plt.tight_layout()
    plt.show()

