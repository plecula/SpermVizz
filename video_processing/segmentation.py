from segment_anything import sam_model_registry, SamAutomaticMaskGenerator
import torch
import cv2
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
import math

BASE_DIR = Path(__file__).resolve().parent.parent
image_path = BASE_DIR / "app" / "static" / "uploads" / "2a5322ac-52e8-447c-96c2-fe20200b573c" / "frame_1.jpg"

sam_checkpoint = BASE_DIR / "video_processing" / "models" / "sam_vit_l_0b3195.pth"     # sam_vit_h_4b8939.pth  # sam_vit_b_01ec64.pth #sam_vit_l_0b3195.pth
model_type = "vit_l"                        # vit_h  # vit_b # vit_l
 
sam = sam_model_registry[model_type](checkpoint=sam_checkpoint)
sam.to("cpu")  # or "cuda"

mask_generator = SamAutomaticMaskGenerator(sam)

image = cv2.imread(image_path)
#image = cv2.resize(image, (512, 512))  

masks = mask_generator.generate(image)

#print(masks)

# IoU metric sorted
masks_sorted = sorted(masks, key=lambda x: x['predicted_iou'], reverse=True)
best_mask = masks_sorted[0]['segmentation']

plt.figure(figsize=(6,6))
plt.imshow(1-best_mask, cmap='gray')  # True - white
plt.title('Mask')
plt.axis('off')
plt.show()

# num_masks = len(masks)
# cols = 4 
# rows = math.ceil(num_masks / cols)

# plt.figure(figsize=(4 * cols, 4 * rows))

# for idx, mask in enumerate(masks):
#     plt.subplot(rows, cols, idx + 1)
#     plt.imshow(mask['segmentation'], cmap='gray')
#     plt.title(f"IoU: {mask['predicted_iou']:.2f}")
#     plt.axis('off')

# plt.tight_layout()
# plt.show()