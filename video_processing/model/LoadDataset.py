from torch.utils.data import Dataset
from glob import glob
import natsort
import torch
import cv2
import os
import numpy as np


class SpermDataset(Dataset):
    def __init__(self, path):   #config_data
        self.path = path
        
        self.path_images = natsort.natsorted(glob(os.path.join(path, 'frames', '*.jpg')))
        self.path_head_masks = natsort.natsorted(glob(os.path.join(path, 'head', '*.png')))
        self.path_flagellum_masks = natsort.natsorted(glob(os.path.join(path, 'flagellum', '*.png')))
        
        #self.config_data = config_data

        # MAY BE USED IN THE FUTURE       
        # self._initialize_attributes()
        # self._prepare_sequences()
        # self._prepare_transform()
        # self._prepare_final_images_with_flow()
# <<<<<<< weronika
    
# =======
#         print("Found frames:", len(self.path_images))
#         print("Found head masks:", len(self.path_head_masks))
#         print("Found flagellum masks:", len(self.path_flagellum_masks))

# >>>>>>> do-testu

    def __len__(self):
        
        return len(self.path_images)


    def __getitem__(self, idx):
        # READ IN GRAYSCALE 
        frames = cv2.imread(self.path_images[idx], cv2.IMREAD_GRAYSCALE)
        head_mask = cv2.imread(self.path_head_masks[idx], cv2.IMREAD_GRAYSCALE)
        flagellum_mask = cv2.imread(self.path_flagellum_masks[idx], cv2.IMREAD_GRAYSCALE)

        # RESIZE
        frames = cv2.resize(frames, (256, 256))
        head_mask = cv2.resize(head_mask, (256, 256))
        flagellum_mask = cv2.resize(flagellum_mask, (256, 256))

        # NORMALIZATION 0-1
        frames = frames / 255.0
        head_mask = head_mask / 255.0
        flagellum_mask = flagellum_mask / 255.0

        # ADDING CHANNEL DIMENSION (1, H, W)
        frames = np.expand_dims(frames, axis=0)
        mask = np.stack([head_mask, flagellum_mask], axis=0)  # (2, H, W)
        # head_mask = np.expand_dims(head_mask, axis=0)
        # flagellum_mask = np.expand_dims(flagellum_mask, axis=0)
        

        return torch.tensor(frames, dtype=torch.float32), torch.tensor(mask, dtype=torch.float32)
        
        # torch.tensor(head_mask, dtype=torch.float32), 
        # torch.tensor(flagellum_mask, dtype=torch.float32)
