# -*- coding: utf-8 -*-
"""diplo.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1D6sMB0DXMuv5KK1Kz-GSqFqTvVE3W05B
"""

# Commented out IPython magic to ensure Python compatibility.


# %matplotlib inline
import os

import torch
import torch.nn as nn
import torch.nn.functional as F

num_epochs = 20
batch_size = 32
learning_rate = 1e-3
use_gpu = True
checkpointing = False
PATH = "C:\\Users\\hrebe\\Desktop\\Diplomovka\\places_model.pt"

import numpy as np
from skimage import color
import cv2
import torchvision
import torchvision.transforms as transforms
from torch.utils.data import DataLoader, Dataset
import numpy as np
from skimage import color, io

import matplotlib.pyplot as plt

import torchvision.utils
import time

# converts the PIL image to a pytorch tensor containing an LAB image
def import_image(img):
    return torch.cuda.FloatTensor(np.transpose(color.rgb2lab(np.array(img)), (2, 0, 1)))
    
img_transform = transforms.Compose([
    # transforms.Resize(256),
    transforms.Lambda(import_image)
])

# train_path ='C:\\Users\\hrebe\\Desktop\\Diplomovka\\data\\train_color'
# test_path ='C:\\Users\\hrebe\\Desktop\\Diplomovka\\data\\test_color'

places_path = 'C:\\Users\\hrebe\\Desktop\\Diplomovka\\places'

class ImageDataset(Dataset):
  def __init__(self,img_folder,transform):
    self.transform=transform
    self.img_folder=img_folder
  

  def __getitem__(self,index):
    
    image=cv2.imread(self.img_folder)
    image=self.transform(image)

    return image

  def __len__(self):
    return len(self.image)
# train_dataset = torchvision.datasets.ImageFolder(train_path, transform = img_transform)
# test_dataset = torchvision.datasets.ImageFolder(test_path, transform = img_transform)

dataset = torchvision.datasets.ImageFolder(places_path, transform = img_transform)
n = len(dataset)  # total number of examples
n_test = int(0.05 * n)  # take ~10% for test
test_dataset = torch.utils.data.Subset(dataset, range(n_test))  # take first 10%
train_dataset = torch.utils.data.Subset(dataset, range(n_test, int(0.3 * n)))  # take the rest   


train_dataloader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)
test_dataloader = DataLoader(test_dataset, batch_size=batch_size, shuffle=True)

class ColorNet(nn.Module):
    def __init__(self, d=128):
        super(ColorNet, self).__init__()
        
        self.conv1 = nn.Conv2d(1, 32, kernel_size=4, stride=2, padding=1) # out: 32 x 16 x 16
        self.conv1_bn = nn.BatchNorm2d(32)
        self.conv2 = nn.Conv2d(32, 64, kernel_size=4, stride=2, padding=1) # out: 64 x 8 x 8
        self.conv2_bn = nn.BatchNorm2d(64)
        self.conv3 = nn.Conv2d(64, 128, kernel_size=4, stride=2, padding=1) # out: 128 x 4 x 4
        self.conv3_bn = nn.BatchNorm2d(128)
        self.conv4 = nn.Conv2d(128, 128, kernel_size=3, stride=1, padding=1) # out: 128 x 4 x 4
        self.conv4_bn = nn.BatchNorm2d(128)
        self.conv5 = nn.Conv2d(128, 128, kernel_size=3, stride=1, padding=1) # out: 128 x 4 x 4
        self.conv5_bn = nn.BatchNorm2d(128)
        self.conv6 = nn.Conv2d(128, 128, kernel_size=3, stride=1, padding=1) # out: 128 x 4 x 4
        self.conv6_bn = nn.BatchNorm2d(128)
        self.tconv1 = nn.ConvTranspose2d(128, 64, kernel_size=4, stride=2, padding=1) # out: 64 x 8 x 8
        self.tconv1_bn = nn.BatchNorm2d(64)
        self.tconv2 = nn.ConvTranspose2d(64, 32, kernel_size=4, stride=2, padding=1) # out: 32 x 16 x 16
        self.tconv2_bn = nn.BatchNorm2d(32)
        self.tconv3 = nn.ConvTranspose2d(32, 2, kernel_size=4, stride=2, padding=1) # out: 2 x 32 x 32

    def forward(self, input):
        x = F.relu(self.conv1_bn(self.conv1(input)))
        x = F.relu(self.conv2_bn(self.conv2(x)))
        x = F.relu(self.conv3_bn(self.conv3(x)))
        x = F.relu(self.conv4_bn(self.conv4(x)))
        x = F.relu(self.conv5_bn(self.conv5(x)))
        x = F.relu(self.conv6_bn(self.conv6(x)))
        x = F.relu(self.tconv1_bn(self.tconv1(x)))
        x = F.relu(self.tconv2_bn(self.tconv2(x)))
        x = self.tconv3(x)

        return x

cnet = ColorNet()

device = torch.device('cuda:0')
cnet = cnet.to(device)

num_params = sum(p.numel() for p in cnet.parameters() if p.requires_grad)
print('Number of parameters: %d' % (num_params))

optimizer = torch.optim.Adam(params=cnet.parameters(), lr=learning_rate)
print(cnet)
# set to training mode
cnet.train()

train_loss_avg = []
if checkpointing:
    checkpoint = torch.load(PATH)
    cnet.load_state_dict(checkpoint['model_state_dict'])
    optimizer.load_state_dict(checkpoint['optimizer_state_dict'])
else:
    print('Training ...')
    for epoch in range(num_epochs):
        train_loss_avg.append(0)
        num_batches = 0
        t0 = time.time()
        print('Epoch:', epoch+1 ,'/',num_epochs,':')
        for lab_batch, _ in train_dataloader:
        
            lab_batch = lab_batch.to(device)
        
            # apply the color net to the luminance component of the Lab images
            # to get the color (ab) components
            predicted_ab_batch = cnet(lab_batch[:, 0:1, :, :])
        
            # loss is the L2 error to the actual color (ab) components
            loss = F.mse_loss(predicted_ab_batch, lab_batch[:, 1:3, :, :])
        
            # backpropagation
            optimizer.zero_grad()
            loss.backward()
        
            # one step of the optmizer (using the gradients from backpropagation)
            optimizer.step()
        
            train_loss_avg[-1] += loss.item()
            num_batches += 1
        
        train_loss_avg[-1] /= num_batches
        print('Epoch [%d / %d] average reconstruction error: %f time(m): %f' % (epoch+1, num_epochs, train_loss_avg[-1], (time.time() - t0)/60))
        LOSS = train_loss_avg[-1]
        PATH2 = "C:\\Users\\hrebe\\Desktop\\Diplomovka\\places_model_%d.pt" % (epoch+1)
        torch.save({
                'epoch': epoch,
                'model_state_dict': cnet.state_dict(),
                'optimizer_state_dict': optimizer.state_dict(),
                'loss': LOSS,
                }, PATH2)



plt.ion()

fig = plt.figure(figsize=(15, 5))
plt.plot(train_loss_avg)
plt.xlabel('Epochs')
plt.ylabel('Loss')
plt.savefig("C:\\Users\\hrebe\\Desktop\\Diplomovka\\plot_places.png")
plt.show()

cnet.eval()

test_loss_avg, num_batches = 0, 0
for lab_batch, _ in test_dataloader:

    with torch.no_grad():

        lab_batch = lab_batch.to(device)

        # apply the color net to the luminance component of the Lab images
        # to get the color (ab) components
        predicted_ab_batch = cnet(lab_batch[:, 0:1, :, :])

        # loss is the L2 error to the actual color (ab) components
        loss = F.mse_loss(predicted_ab_batch, lab_batch[:, 1:3, :, :])

        test_loss_avg += loss.item()
        num_batches += 1
    
test_loss_avg /= num_batches
print('average loss: %f' % (test_loss_avg))

plt.ion()


with torch.no_grad():

    # pick a random subset of images from the test set
    image_inds = np.random.choice(len(test_dataset), 25, replace=False)
    lab_batch = torch.stack([test_dataset[i][0] for i in image_inds])
    lab_batch = lab_batch.to(device)

    # predict colors (ab channels)
    predicted_ab_batch = cnet(lab_batch[:, 0:1, :, :])
    predicted_lab_batch = torch.cat([lab_batch[:, 0:1, :, :], predicted_ab_batch], dim=1)

    lab_batch = lab_batch.cpu()
    predicted_lab_batch = predicted_lab_batch.cpu()

    # convert to rgb
    rgb_batch = []
    predicted_rgb_batch = []
    for i in range(lab_batch.size(0)):
        rgb_img = color.lab2rgb(np.transpose(lab_batch[i, :, :, :].numpy().astype('float64'), (1, 2, 0)))
        rgb_batch.append(torch.FloatTensor(np.transpose(rgb_img, (2, 0, 1))))
        predicted_rgb_img = color.lab2rgb(np.transpose(predicted_lab_batch[i, :, :, :].numpy().astype('float64'), (1, 2, 0)))
        predicted_rgb_batch.append(torch.FloatTensor(np.transpose(predicted_rgb_img, (2, 0, 1))))

    # plot images
    fig, ax = plt.subplots(figsize=(45,45), nrows=1, ncols=2)
    ax[0].imshow(np.transpose(torchvision.utils.make_grid(torch.stack(predicted_rgb_batch), nrow=5).numpy(), (1, 2, 0)))
    ax[0].title.set_text('re-colored')
    ax[1].imshow(np.transpose(torchvision.utils.make_grid(torch.stack(rgb_batch), nrow=5).numpy(), (1, 2, 0)))
    ax[1].title.set_text('original')
    plt.savefig("C:\\Users\\hrebe\\Desktop\\Diplomovka\\pls_places.png")
    plt.show()