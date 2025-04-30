import torch
import torch.nn as nn
import torch.optim as optim

inputs = torch.tensor([
    [1,1,1,1,1,1,0],
    [0,1,1,0,0,0,0],
    [1,1,0,1,1,0,1],
    [1,1,1,1,0,0,1],
    [0,1,1,0,0,1,1],
    [1,0,1,1,0,1,1],
    [1,0,1,1,1,1,1],
    [1,1,1,0,0,0,0],
    [1,1,1,1,1,1,1],
    [1,1,1,1,0,1,1],
], dtype=torch.float32)

targets = torch.tensor([
    [0,0,0,0],
    [0,0,0,1],
    [0,0,1,0],
    [0,0,1,1],
    [0,1,0,0],
    [0,1,0,1],
    [0,1,1,0],
    [0,1,1,1],
    [1,0,0,0],
    [1,0,0,1],
], dtype=torch.float32)

class MLP(nn.Module):
    def __init__(self):
        super().__init__()
        self.layers = nn.Sequential(
            nn.Linear(7, 16),
            nn.ReLU(),
            nn.Linear(16, 16),
            nn.ReLU(),
            nn.Linear(16, 4),
            nn.Sigmoid()
        )

    def forward(self, x):
        return self.layers(x)

model = MLP()
criterion = nn.BCELoss()
optimizer = optim.SGD(model.parameters(), lr=0.1)

for epoch in range(5000):
    outputs = model(inputs)
    loss = criterion(outputs, targets)

    optimizer.zero_grad()
    loss.backward()
    optimizer.step()

    if epoch % 100 == 0:
        print(f"Epoch {epoch}, Loss: {loss.item():.4f}")

with torch.no_grad():
    test_outputs = model(inputs).round()
    for i, pred in enumerate(test_outputs):
        binary = ''.join(str(int(bit)) for bit in pred)
        print(f"{inputs[i].int().tolist()} => {binary}")
