from segment_anything import sam_model_registry, SamAutomaticMaskGenerator, SamPredictor
import torch
import cv2
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
import math
import uuid
import os

BASE_DIR = Path(__file__).resolve().parent.parent
image_path = BASE_DIR / "app" / "static" / "uploads" / "f_512v12_0b8" / "frame_1.jpg"

sam_checkpoint = BASE_DIR / "video_processing" / "models" / "sam_vit_l_0b3195.pth"     # sam_vit_h_4b8939.pth  # sam_vit_b_01ec64.pth #sam_vit_l_0b3195.pth
model_type = "vit_l"                        # vit_h  # vit_b # vit_l


image = cv2.imread(image_path)
image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

sam = sam_model_registry[model_type](checkpoint=sam_checkpoint)
predictor = SamPredictor(sam)       # do obslugi z promptow - punkty, bboxy etc


predictor.set_image(image_rgb)

# Valid points

input_points = np.array([[280, 150], [270.5, 222.3]])  # head point, tail point
#input_points = np.array([[390, 74], [350, 85.6]])
#input_points = np.array([[268, 435.9], [290, 437]])
#input_points = np.array([[103.4, 428.4], [160.5, 480.1]])
input_labels = np.array([1, 1])  # foreground


masks, scores, logits = predictor.predict(
    point_coords=input_points,
    point_labels=input_labels,
    multimask_output=True
)

for i, mask in enumerate(masks):
    print(f"Mask {i}:")
    print(f"  Head point: {mask[int(input_points[0][1]), int(input_points[0][0])]}")
    print(f"  Flagellum point: {mask[int(input_points[1][1]), int(input_points[1][0])]}")


# plt.figure(figsize=(8,4))
# for i in range(masks.shape[0]):
#     plt.subplot(1, masks.shape[0], i+1)
#     plt.imshow(masks[i], cmap='gray')
#     plt.title(f'Mask {i+1}')
#     plt.axis('off')
# plt.tight_layout()
# plt.show()

overlay = np.zeros_like(image_rgb, dtype=np.uint8)

# mask 0 -> blue channel
overlay[:,:,2] = (masks[0] * 255).astype(np.uint8)      # head?

# mask 1 -> red channel 
if masks.shape[0] > 1:
    overlay[:,:,0] = (masks[1] * 255).astype(np.uint8)  # flagellum?

# Blend or show overlay
blended = cv2.addWeighted(image_rgb, 0.6, overlay, 0.3, 0)

# plt.figure(figsize=(8,8))
# plt.imshow(blended)
# plt.title('Masks on original frame')
# plt.axis('off')
# plt.show()


# Save mask
mask_filename = f"m_{uuid.uuid4().hex[:6]}.png"
mask_path = BASE_DIR / "video_processing" / "masksTracking" / mask_filename
os.makedirs(mask_path.parent, exist_ok=True)

mask_image = blended
cv2.imwrite(str(mask_path), cv2.cvtColor(mask_image, cv2.COLOR_RGB2BGR))