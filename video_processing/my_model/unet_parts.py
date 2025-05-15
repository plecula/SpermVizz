# U-Net model parts

import torch
import torch.nn as nn
import torch.nn.functional as F

# Double Convolution Sequence with normalization

class DoubleConv(nn.Module):
    def __init__(self,in_channels, out_channels):
        super(DoubleConv, self).__init__()
        self.conv = nn.Sequential(
            nn.Conv2d(in_channels,out_channels, kernel_size=3, padding=1),
            nn.BatchNorm2d(out_channels),
            nn.ReLU(inplace=True),
            nn.Conv2d(out_channels,out_channels,kernel_size=3, padding=1),
            nn.BatchNorm2d(out_channels),
            nn.ReLU(inplace=True)
        )

    def forward(self,x):
        return self.conv(x)


# First block - searching for basic features

class inConv(nn.Module):
    def __init__(self,in_channels, out_channels):
        super(inConv, self).__init__()
        self.conv = DoubleConv(in_channels, out_channels)

    def forward(self, x):
        x = self.conv(x)
       
        return x

# Last block - changes channels count

class outConv(nn.Module):
    def __init__(self,in_channels, out_channels):
        super(outConv, self).__init__()
        self.conv = nn.Conv2d(in_channels, out_channels, 1)
    
    def forward(self, x):
        x = self.conv(x)

        return x

# Downsampling

class DownSample(nn.Module):
    def __init__(self,in_channels, out_channels):
        super(DownSample, self).__init__()
        self.conv = DoubleConv(in_channels,out_channels)
        self.pool = nn.MaxPool2d(kernel_size=2, stride=2)

    def forward(self, x):
        down = self.conv(x)
        p = self.pool(down)

        return down, p
    
# Upsampling

class UpSample(nn.Module):
    def __init__(self,in_channels, out_channels, bilinear=True):
        super(UpSample, self).__init__()

        ### Memory optymalization

        if bilinear:
            self.up = nn.Upsample(scale_factor=2, mode='bilinear', align_corners=True)
        else:
            self.up = nn.ConvTranspose2d(in_channels//2, in_channels//2, kernel_size=2, stride=2)
        
        ###

        self.conv = DoubleConv(in_channels,out_channels)

    def forward(self, x1, x2):  # (self, x1 upsampling, x2 skip connection)
        x1 = self.up(x1)
       
       # BCHW 
        diffY = x2.size()[2] - x1.size()[2]     # Height
        diffX = x2.size()[3] - x1.size()[3]     # Width

        x1 = F.pad(x1, (diffX // 2, diffX - diffX//2,
                           diffY // 2, diffY - diffY//2))

        x = torch.cat([x2, x1], dim=1)
    
        return self.conv(x)