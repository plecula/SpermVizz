# Full U-Net model

from unet_parts import *

class UNet(nn.Module):
    def __init__(self, n_channels, n_classes):
        super(UNet, self).__init__()
        self.inconv = inConv(n_channels, 64)
        self.down1 = DownSample(64, 128)
        self.down2 = DownSample(128, 256)
        self.down3 = DownSample(256, 512)
        self.down4 = DownSample(512, 512)
        self.up1 = UpSample(1024, 256)
        self.up2 = UpSample(512, 128)
        self.up3 = UpSample(256, 64)
        self.up4 = UpSample(128, 64)
        self.outconv = outConv(64, n_classes)

    def forward(self, x):
        x1 = self.inconv(x)
        x2, p1 = self.down1(x1)
        x3, p2 = self.down2(p1)
        x4, p3 = self.down3(p2)
        x5, p4 = self.down4(p3)
        x = self.up1(x5, x4)
        x = self.up2(x, x3)
        x = self.up3(x, x2)
        x = self.up4(x, x1)
        x = self.outconv(x)
        
        #return torch.sigmoid(x)    # We use BCEWithLogitsLoss() in train.py which is more stable in values
        return x