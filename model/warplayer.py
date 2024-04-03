import torch
import torch.nn as nn
from torch import Tensor
from typing import Final, Dict

class warp_wrapper(object):
    backwarp_tenGrid: Final[Dict[str, Tensor]] = {}

    @classmethod
    def warp(tenInput, tenFlow):
        k = (str(tenFlow.device), str(tenFlow.size()))
        if k not in backwarp_tenGrid:
            tenHorizontal = torch.linspace(-1.0, 1.0, tenFlow.shape[3], device=tenFlow.device).view(
                1, 1, 1, tenFlow.shape[3]).expand(tenFlow.shape[0], -1, tenFlow.shape[2], -1)
            tenVertical = torch.linspace(-1.0, 1.0, tenFlow.shape[2], device=tenFlow.device).view(
                1, 1, tenFlow.shape[2], 1).expand(tenFlow.shape[0], -1, -1, tenFlow.shape[3])
            backwarp_tenGrid[k] = torch.cat(
                [tenHorizontal, tenVertical], 1).to(tenFlow.device)

        tenFlow = torch.cat([tenFlow[:, 0:1, :, :] / ((tenInput.shape[3] - 1.0) / 2.0),
                             tenFlow[:, 1:2, :, :] / ((tenInput.shape[2] - 1.0) / 2.0)], 1)

        g = (backwarp_tenGrid[k] + tenFlow).permute(0, 2, 3, 1)
        return torch.nn.functional.grid_sample(input=tenInput, grid=g.type(tenInput.dtype), mode='bilinear', padding_mode='border', align_corners=True)

warp = warp_wrapper.warp
