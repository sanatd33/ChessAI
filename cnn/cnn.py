import torch
import torch.nn as nn
import torch.nn.functional as F

from torch import Tensor
from torch.nn import Module

class CNN(Module):
    def __init__(self):
        super().__init__()
        channels = 128

        self.layers = nn.Sequential(
            nn.Conv2d(18, channels, kernel_size=3, padding=1),
            nn.BatchNorm2d(channels),
            nn.LeakyReLU(0.01),
            *[self.ResidualBlock(channels) for _ in range(10)],
            nn.AdaptiveAvgPool2d((1, 1)),
            nn.Flatten(),
            nn.Linear(channels, 256),
            nn.LeakyReLU(0.01),
            nn.Dropout(0.2), 
            nn.Linear(256, 1)
        )

    def forward(self, x : Tensor):
        return self.layers(x)

    class ResidualBlock(nn.Module):
        def __init__(self, channels):
            super().__init__()
            self.block = nn.Sequential(
                nn.Conv2d(channels, channels, 3, padding=1),
                nn.BatchNorm2d(channels),
                nn.LeakyReLU(0.01),
                nn.Conv2d(channels, channels, 3, padding=1),
                nn.BatchNorm2d(channels),
            )

        def forward(self, x):
            return F.leaky_relu(x + self.block(x), 0.01)