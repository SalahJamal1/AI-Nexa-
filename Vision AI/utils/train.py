import torch
from torch import nn

from utils.modelTrainer import ModelTrainer, device

with open("../food_101_classes.txt", "r") as f:
    classes = [line.strip() for line in f]

vit, transform = ModelTrainer.create_vit(num_classes=101, device=device)
optimizer = torch.optim.Adam(params=vit.parameters(), lr=0.001)
loss_fn = nn.CrossEntropyLoss()
model_trainer = ModelTrainer(
    model_name="vit",
    model=vit,
    device=device,
    loss_fn=loss_fn,
    optimizer=optimizer,
    epochs=3,
    transform=transform,
)
try:
    results = model_trainer.train()
    model_trainer.save_model(destination="model", model_name="vit.pth")
except Exception as e:
    print(e)
