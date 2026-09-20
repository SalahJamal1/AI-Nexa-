import os.path
import requests
import torch
import torchvision
from PIL import Image
from datetime import datetime, timezone
from pathlib import Path
from torch import nn
from torch.optim import Optimizer
from torch.utils.data import DataLoader, random_split
from torch.utils.tensorboard import SummaryWriter
from torchmetrics import Accuracy
from torchvision import transforms
from torchvision.datasets import Food101, ImageFolder
from tqdm.auto import tqdm
from zipfile import ZipFile

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")


class ModelTrainer:
    def __init__(
            self,
            model_name: str,
            model: nn.Module,
            optimizer: Optimizer,
            loss_fn: nn.Module,
            device: torch.device,
            epochs: int,
            train_dir: str | None = None,
            test_dir: str | None = None,
            transform: torchvision.transforms.Compose | None = None,
    ):
        self.model_name = model_name
        self.train_dir = train_dir
        self.test_dir = test_dir
        self.device = device
        self.epochs = epochs
        self.model = model
        self.loss_fn = loss_fn
        self.optimizer = optimizer
        self.transform = transform
        self.train_dataloader, self.test_dataloader, self.classes = (
            self.create_dataloader()
        )
        self.acc = Accuracy(task="multiclass", num_classes=len(self.classes)).to(
            self.device
        )
        self.writer = self.create_writer(model_name=model_name)

    def download_data(self, source: str, destination: str):
        file_dir = Path(destination)
        file_dir.mkdir(parents=True, exist_ok=True)
        file_name = Path(source).name
        file_path = file_dir / file_name

        with open(file_path, "wb") as f:
            response = requests.get(source)
            response.raise_for_status()
            f.write(response.content)
        with ZipFile(file_path, "r") as zip_ref:
            zip_ref.extractall(destination)

        os.remove(file_path)

    def create_dataloader(self):
        transform = self.transform
        num_workers = 2
        if transform is None:
            transform = transforms.Compose(
                [
                    transforms.Resize((224, 224)),
                    transforms.ToTensor(),
                    transforms.Normalize(
                        mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]
                    ),
                ]
            )
        if self.train_dir and self.test_dir:
            train_dataset = ImageFolder(
                root=self.train_dir, transform=transform, target_transform=None
            )
            test_dataset = ImageFolder(
                root=self.test_dir, transform=transform, target_transform=None
            )

        else:
            file_dir = Path("data")
            file_dir.mkdir(parents=True, exist_ok=True)
            train_dataset = Food101(
                root=file_dir,
                split="train",
                transform=transform,
                target_transform=None,
                download=True,
            )
            test_dataset = Food101(
                root=file_dir,
                split="test",
                transform=transform,
                target_transform=None,
                download=True,
            )
        classes = train_dataset.classes
        train_dataset = self.spilt_data(train_dataset)[1]
        test_dataset = self.spilt_data(test_dataset)[1]

        train_dataloader = DataLoader(
            dataset=train_dataset,
            batch_size=32,
            shuffle=True,
            num_workers=num_workers,
            pin_memory=True,
        )
        test_dataloader = DataLoader(
            dataset=test_dataset,
            batch_size=32,
            shuffle=False,
            num_workers=num_workers,
            pin_memory=True,
        )
        return train_dataloader, test_dataloader, classes

    def train_step(self) -> tuple[float, float]:
        self.model.train()
        self.acc.reset()
        train_loss, train_acc = 0, 0
        for img, label in self.train_dataloader:
            img, label = img.to(self.device), label.to(self.device)
            logits = self.model(img)
            y_pred = torch.argmax(logits, dim=1)
            loss = self.loss_fn(logits, label)
            self.acc.update(y_pred, label)
            train_loss += loss.item()
            self.optimizer.zero_grad()
            loss.backward()
            self.optimizer.step()
        train_loss /= len(self.train_dataloader)
        train_acc = self.acc.compute().item()
        return train_loss, train_acc

    def test_step(self) -> tuple[float, float]:
        test_loss, test_acc = 0, 0
        self.acc.reset()
        self.model.eval()
        with torch.inference_mode():
            for img, label in self.test_dataloader:
                img, label = img.to(self.device), label.to(self.device)
                logits = self.model(img)
                y_pred = torch.argmax(logits, dim=1)
                loss = self.loss_fn(logits, label)
                self.acc.update(y_pred, label)
                test_loss += loss.item()

        test_loss /= len(self.test_dataloader)
        test_acc = self.acc.compute().item()
        return test_loss, test_acc

    def train(self) -> dict[str, list[float]]:
        results: dict[str, list[float]] = {
            "train_loss": [],
            "train_acc": [],
            "test_loss": [],
            "test_acc": [],
        }

        for epoch in tqdm(range(self.epochs)):
            print(f"\nEpoch {epoch + 1}\n")
            train_loss, train_acc = self.train_step()
            test_loss, test_acc = self.test_step()

            self.writer.add_scalars(
                main_tag="Loss",
                tag_scalar_dict={
                    "train_loss": train_loss,
                    "test_loss": test_loss,
                },
                global_step=epoch,
            )
            self.writer.add_scalars(
                main_tag="Accuracy",
                tag_scalar_dict={
                    "train_acc": train_acc,
                    "test_acc": test_acc,
                },
                global_step=epoch,
            )

            results["train_loss"].append(train_loss)
            results["train_acc"].append(train_acc)
            results["test_loss"].append(test_loss)
            results["test_acc"].append(test_acc)
            print(
                f"Training Loss: {train_loss:.3f}, Train Accuracy: {train_acc:.3f} ,Testing Loss: {test_loss:.3f}, Testing Accuracy: {test_acc:.3f}"
            )
        self.writer.close()
        return results

    def create_writer(self, model_name: str) -> SummaryWriter:
        timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
        log_dir = os.path.join(
            "runs", "experiments", timestamp, model_name, f"epochs_{self.epochs}"
        )
        return SummaryWriter(log_dir=log_dir)

    def save_model(self, destination, model_name: str) -> Path:
        file_dir = Path(destination)
        file_dir.mkdir(parents=True, exist_ok=True)
        file_name = file_dir / model_name
        assert model_name.endswith((".pt", ".pth")), "Invalid model name"
        torch.save(obj=self.model.state_dict(), f=file_name)
        return file_name

    @staticmethod
    def load_model(destination, model_name: str):
        file_dir = Path(destination)
        with open("food_101_classes.txt", "r") as f:
            classes = [line.strip() for line in f]
        model, transform = ModelTrainer.create_vit(len(classes), device)

        file_name = file_dir / model_name
        assert model_name.endswith((".pt", ".pth")), "Invalid model name"
        if not file_name.exists():
            raise FileNotFoundError(f"Model {model_name} does not exist")
        model.load_state_dict(torch.load(f=file_name, map_location=device))
        return model, transform, classes

    def spilt_data(self, dataset):
        train_size = int(len(dataset) * 0.8)
        value_size = len(dataset) - train_size
        train_dataset, val_dataset = random_split(
            dataset=dataset, lengths=[train_size, value_size]
        )
        return train_dataset, val_dataset

    @staticmethod
    def create_vit(
            num_classes: int, device: str
    ) -> tuple[nn.Module, torchvision.transforms.Compose]:
        weights = torchvision.models.ViT_B_16_Weights.DEFAULT
        transform = weights.transforms()
        vit = torchvision.models.vit_b_16(weights=weights)

        for param in vit.parameters():
            param.requires_grad = False
        in_features = vit.heads.head.in_features

        vit.heads = nn.Sequential(
            nn.Dropout(p=0.2),
            nn.Linear(in_features=in_features, out_features=num_classes),
        )

        vit.to(device=device)

        return vit, transform

    @staticmethod
    def prediction(
            model,
            image_path: Path | str,
            device: str,
            classes: list,
            transform: torchvision.transforms.Compose,
    ):
        image = Image.open(image_path).convert("RGB")

        model.eval()
        with torch.inference_mode():
            image_transformer = transform(image).unsqueeze(0).to(device)
            logits = model(image_transformer)
            probs = torch.softmax(logits, dim=1)
            label = torch.argmax(probs, dim=1).item()
            pred_class = classes[label]
            values, indices = torch.topk(probs[0], k=7)
            pred_probs = {
                classes[idx.item()]: prob.item() for prob, idx in zip(values, indices)
            }  # type = ignore
        return pred_class, pred_probs
