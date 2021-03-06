import sys
sys.path.append('../')
from src.Hive import Hive
from src.IO2 import RLE
from src.EyerissF import EyerissF as EF
import numpy as np
import skimage.io as io
from skimage.util import pad
import os
from model.lenet import LeNet5
import torch
net = LeNet5()

for i, (name, param) in enumerate(net.named_parameters()):
    print(name)
    data = np.load("../filter/"+name+".npy")
    param.data = torch.from_numpy(data)
net.eval()
dir_name = "../mnist_png/mnist_png/training/5"
#dir_name = "mnist_png/mnist_png/one_pic"
files = os.listdir(dir_name)
batch_size = 4
r = RLE(1)
ef = EF()
hive = Hive(ef)
for f in range(0, len(files), batch_size):
    pics = []
    for i in range(batch_size):
        load_from = os.path.join(dir_name,files[f+i])
        image = io.imread(load_from, as_gray=True)
        image = pad(image,((2,2),(2,2)), 'median')
        pic = np.array(image/255).reshape(1,image.shape[0],-1)
        pics.append(pic) 
    pics=np.array(pics)
    inputs=torch.tensor(pics,dtype=torch.float32)
    
  
    flts = np.load("../filter/convnet.c1.weight.npy")
    pics = r.Compress(pics)
    flts = r.Compress(flts)
    pics= hive.Conv2d(pics,flts)
    
    #pics = np.swapaxes(pics,1,3)
    #pics= pics+np.float16(np.load("filter/convnet.c1.bias.npy"))
    #pics = np.swapaxes(pics,1,3)
    pics = hive.PreProcess(pics)
    pics = hive.ReLU(pics)
    pics=hive.Pooling(pics)
    
    flts = np.float16(np.load("../filter/convnet.c3.weight.npy"))
    flts = r.Compress(flts)
    pics = r.Compress(pics)
    #print('pic', pics.shape,'flt', flts.shape)
    pics = hive.Conv2d(pics,flts)
    #pics = np.swapaxes(pics,1,3)
    #pics= pics+np.float16(np.load("filter/convnet.c3.bias.npy"))
    #pics = np.swapaxes(pics,1,3)
    #pics = Extension.NumpyAddExtension(hive.Decompress(r)) 
    pics = hive.PreProcess(pics)
    pics = hive.ReLU(pics)
    pics=hive.Pooling(pics)
    
    
    
    
    
    #print('after pooling pic', pics.shape)
    
    flts = np.float16(np.float16(np.load("../filter/convnet.c5.weight.npy")))
    flts = r.Compress(flts)
    pics = r.Compress(pics)
    #print('pic', pics.shape,'flt', flts.shape)
    pics = hive.Conv2d(pics, flts) 
    
    #pics = np.swapaxes(pics,1,3)
    #pics= pics+np.float16(np.load("filter/convnet.c5.bias.npy"))
    #pics = np.swapaxes(pics,1,3)
    #pics = Extension.NumpyAddExtension(hive.Decompress(r)) 
    pics = hive.PreProcess(pics)
    pics = hive.ReLU(pics)

    
    res = inputs
    for i in range(8):
        res = net.convnet[i](res)
    print(res.shape)
    diff = pics-res.data.numpy()
    for i in range(len(res)):
        for j in range(len(res[0])):
            if np.any(np.abs(diff[i][j])>10e-4): print(diff[i][j])
    #break
    
    
    vector = pics.reshape(batch_size, -1)
    vector = hive.FullConnect(vector, np.load('../filter/fc.f6.weight.npy'))
    vector = hive.ReLU(vector)
    #vector = vector+np.float16(np.load("filter/fc.f6.bias.npy"))
    vector = hive.FullConnect(vector, np.load('../filter/fc.f7.weight.npy'))
    #vector = vector+np.float16(np.load("filter/fc.f7.bias.npy"))

    print("this number is : ",vector.argmax(axis = 1))
