import torch
from torch import optim, nn
from torch.utils.data import DataLoader, random_split
from tqdm import tqdm
import os

#from .unet_parts import *
from unet_model import UNet
from LoadDataset import SpermDataset

def dice_loss(pred, target, smooth = 1.):
    pred = torch.sigmoid(pred)
    pred = pred.contiguous()
    target = target.contiguous()    

    intersection = (pred * target).sum(dim=(2, 3))
    loss = 1 - ((2. * intersection + smooth) / 
               (pred.sum(dim=(2, 3)) + target.sum(dim=(2, 3))+ smooth))
    return loss.mean()

def train():
    LEARNING_RATE = 3e-4
    BATCH_SIZE = 4
    EPOCHS = 20
    DATA_PATH = r'D:/studia/studia sem. VI/RAIM/SpermVizz-weronika/dataset/private'
    MODEL_SAVE_PATH = r'D:/studia/studia sem. VI/RAIM/SpermVizz-weronika/video_processing/model'

    device = "cuda" if torch.cuda.is_available() else "cpu"
    train_dataset = SpermDataset(DATA_PATH)

    generator = torch.Generator().manual_seed(42)
    train_dataset, val_dataset = random_split(train_dataset, [0.8, 0.2], generator=generator)

    train_dataloader = DataLoader(dataset=train_dataset,
                                  batch_size=BATCH_SIZE,
                                  shuffle=True,
                                  num_workers=0)
    val_dataloader = DataLoader(dataset=val_dataset,
                                batch_size=BATCH_SIZE,
                                shuffle=True,
                                num_workers=0)
    
    model = UNet(n_channels=1, n_classes=2).to(device)
    optimizer = optim.Adam(model.parameters(), lr=LEARNING_RATE)
    criterion = nn.BCEWithLogitsLoss()

    for epoch in tqdm(range(EPOCHS)):
        model.train()
        train_running_loss = 0

        for images, masks in train_dataloader:
            images, masks = images.to(device), masks.to(device)
            
            preds = model(images)

            loss_head = dice_loss(preds[:, 0:1, :, :], masks[:, 0:1, :, :])    # [B, C, H, W]
            loss_flagellum = dice_loss(preds[:, 1:2, :, :], masks[:, 1:2, :, :])

            loss = (loss_head + loss_flagellum) /2

            optimizer.zero_grad()
            loss.backward()
            optimizer.step()

            train_running_loss += loss.item()

    avg_loss = train_running_loss / len(train_dataloader)
    print(f'Epoch {epoch+1}, Average Loss: {avg_loss:.4f}')

    torch.save(model.state_dict(), os.path.join(MODEL_SAVE_PATH, 'sperm_unet_2channels.pth'))
    print("Model saved!")

if __name__ == "__main__":
    train()