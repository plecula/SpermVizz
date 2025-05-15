import torch

import cv2
import numpy as np
import matplotlib.pyplot as plt
from unet_model import UNet 
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent
image_path = BASE_DIR / "app" / "static" / "uploads" / "199_9854.png"         #UPLOADED IMAGES

# INITIALIZE MODEL
model = UNet(n_channels=1, n_classes=2)
model.load_state_dict(torch.load("sperm_unet_2channels.pth", map_location='cpu'))   # or 'cuda'
model.eval()

image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
image = cv2.resize(image, (512, 512))
input_image = image / 255.0
input_image = np.expand_dims(input_image, axis=0)  # [H, W] -> [1, H, W]
input_image = torch.from_numpy(input_image).unsqueeze(0).float()  # [1, 1, H, W]

# MASK PREDICTION
with torch.no_grad():
    output = model(input_image)
    predicted_mask = torch.sigmoid(output) 
    predicted_mask = predicted_mask.squeeze().cpu().numpy()  # [1, 1, H, W] -> [H, W]

# # Shows masks separated
# plt.figure(figsize=(8,4))
# plt.subplot(1,2,1)
# plt.imshow(predicted_mask[0], cmap='gray')
# plt.title('Mask - head')
# plt.axis('off')

# plt.subplot(1,2,2)
# plt.imshow(predicted_mask[1], cmap='gray')
# plt.title('Mask - flagellum')
# plt.axis('off')

# plt.tight_layout()
# plt.show()

# RGB mask
overlay = np.zeros((512, 512, 3), dtype=np.uint8)

# head - blue channel
overlay[:,:,0] = (predicted_mask[0] * 255).astype(np.uint8)

# flagellum - red channel
overlay[:,:,2] = (predicted_mask[1] * 255).astype(np.uint8)


#blended = cv2.addWeighted(cv2.cvtColor(image, cv2.COLOR_GRAY2BGR), 0.6, overlay, 0.4, 0)
blended = overlay

plt.figure(figsize=(8,8))
plt.imshow(cv2.cvtColor(blended, cv2.COLOR_BGR2RGB))
plt.title('Masks on original frame')
plt.axis('off')
plt.show()