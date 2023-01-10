# -*- coding: utf-8 -*-
"""Monet_Conn_Coarsen.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1UHpCgLf_EWGpGbTOpzovRnURZvyF9SCS
"""

# Commented out IPython magic to ensure Python compatibility.
from google.colab import drive
drive.mount("/content/gdrive")
# %cd gdrive/My\ Drive/GCN_AD/GCN-17-master/lib3
!pip install dgl-cu100

import argparse
import time
import numpy as np
import networkx as nx
import torch
import torch.nn as nn
import torch.nn.functional as F
import dgl
from torch.utils.data import DataLoader
from torchvision import datasets, transforms
from dgl.data import register_data_args, load_data
from dgl.nn.pytorch.conv import ChebConv, GMMConv
from dgl.nn.pytorch.glob import MaxPooling
from grid_graph import grid_graph
from coarsening import coarsen
from coordinate import get_coordinates, z2polar
argparser = argparse.ArgumentParser("Monet")
argparser.add_argument("--gpu", type=int, default=-1,
                       help="gpu id, use cpu if set to -1")
argparser.add_argument("--model", type=str, default="chebnet",
                       help="model to use, chebnet/monet")
argparser.add_argument("--batch-size", type=int, default=1,
                       help="batch size")
argparser.add_argument("--fold", type=int, default=10,
                       help="Number of folds")
args, unknown = argparser.parse_known_args()

import os 
import scipy.io
from scipy import stats
from __future__ import print_function


import numpy as np
from matplotlib import pyplot as plt
import pandas as pd

test=scipy.io.loadmat('../data/adni_connectome_aparc_length.mat')
aparcl=np.array(test['connectome_aparc0x2Baseg_length'])
print("Length 1:",aparcl.shape)

test=scipy.io.loadmat('../data/adni_connectome_aparc_count.mat')
aparcc=np.array(test['connectome_aparc0x2Baseg_count'])
print("Count 1:", aparcc.shape)

test=scipy.io.loadmat('../data/adni_connectome_aparc2009_length.mat')
aparc2l=np.array(test['connectome_aparc0x2Ea2009s0x2Baseg_length'])
print("Length 2:",aparc2l.shape)

test=scipy.io.loadmat('../data/adni_connectome_aparc2009_count.mat')
aparc2c=np.array(test['connectome_aparc0x2Ea2009s0x2Baseg_count'])
print("Count 2:",aparc2c.shape)

#zeromatal=np.zeros([164,164,179])
#zeromatac=np.zeros([164,164,179])

#zeromatal[40:124,40:124,:]=aparcl
#zeromatac[40:124,40:124,:]=aparcc

#aparcl=zeromatal
#aparcc=zeromatac

X=np.zeros([164,164,179])


X=aparc2c.transpose([2,0,1])
#print(X.shape)

data=pd.read_csv('../data/adni_data_1_mor.csv',header=0)
data=np.array(data)
#print(data.shape)
datasubjid=data[:,0]
#print(datasubjid.shape)
matsubjid=pd.read_csv('../data/adni_connectome_subjectlist.csv',header=0)
matsubjid=np.array(matsubjid)
#print(matsubjid.shape)

filtindex=np.isin(datasubjid,matsubjid)
filtindex=filtindex.ravel()
labels=data[:,13]
y=labels[filtindex]
#print(y.shape)

import pandas as pd
from sklearn.model_selection import StratifiedKFold, train_test_split
import random
from sklearn.utils import shuffle
import scipy
bin_ixs = []


# smi=1 , mci=2, ad=3

smiloc=np.asarray(np.where(y==1))
smiloc=np.ndarray.transpose(smiloc)
mciloc=np.asarray(np.where(y==2))
mciloc=np.ndarray.transpose(mciloc)
adloc=np.asarray(np.where(y==3))
adloc=np.ndarray.transpose(adloc)

#mci= 0 ad=1
#2v3, mci=0, ad=1
totalsize=len(mciloc)+len(adloc)
y_admci=np.zeros([totalsize])
X_admci=np.zeros([totalsize,164,164])
for i in range(len(mciloc)):
    y_admci[i]=0
    X_admci[i,:]=X[mciloc[i],:]
for j in range(len(adloc)):
    y_admci[len(mciloc)+j]=1
    X_admci[len(mciloc)+j,:]=X[adloc[j],:]
#print(y_admci.shape)
#print(X_admci.shape)



skf = StratifiedKFold(n_splits=args.fold,shuffle=True,random_state=23)
for train_index, test_index in skf.split(X_admci, y_admci):
    bin_ixs.append(test_index)


test_ixs = bin_ixs[-2:]
train_ixs = bin_ixs[:-2]
train_index = []
test_index = []
for b in list(range(len(train_ixs))):
  train_index = np.concatenate((train_index,train_ixs[b]))
for b in list(range(len(test_ixs))):
  test_index = np.concatenate((test_index,test_ixs[b]))
#print(train_index, len(train_index))
#print(y_admci)
#print(bin_ixs)
features = X_admci
labels = y_admci  
#print(len(train_index),len(test_index))


#print(len(test_ixs),len(train_ixs))
#print(labels)

train_index=train_index.astype('int')
test_index=test_index.astype('int')
#print(features[train_index].shape,labels[train_index].shape)

X_train = features[train_index]
y_train = labels[train_index]
X_test = features[test_index]
y_test = features[test_index]
from torch.utils.data import DataLoader, TensorDataset
from torch import Tensor


trainset = TensorDataset( Tensor(X_train), Tensor(y_train) )
testset = TensorDataset( Tensor(X_test), Tensor(y_test) )

import argparse
import time
import numpy as np
import networkx as nx
import torch
import torch.nn as nn
import torch.nn.functional as F
import dgl
from torch.utils.data import DataLoader
from torchvision import datasets, transforms
from dgl.data import register_data_args, load_data
from dgl.nn.pytorch.conv import ChebConv, GMMConv
from dgl.nn.pytorch.glob import MaxPooling
from grid_graph import grid_graph
from coarsening import coarsen
from coordinate import get_coordinates, z2polar

argparser = argparse.ArgumentParser("MNIST")
argparser.add_argument("--gpu", type=int, default=-1,
                       help="gpu id, use cpu if set to -1")
argparser.add_argument("--model", type=str, default="monet",
                       help="model to use, chebnet/monet")
argparser.add_argument("--batch-size", type=int, default=1,
                       help="batch size")
args, unknown = argparser.parse_known_args()

grid_side = 164
number_edges = 8
metric = 'euclidean'

A = grid_graph(164, 8, metric)

coarsening_levels = 4
L, perm = coarsen(A, coarsening_levels)
g_arr = [dgl.from_scipy(csr) for csr in L]

coordinate_arr = get_coordinates(g_arr, grid_side, coarsening_levels, perm)
for g, coordinate_arr in zip(g_arr, coordinate_arr):
    g.ndata['xy'] = coordinate_arr
    g.apply_edges(z2polar)

def batcher(batch):
    g_batch = [[] for _ in range(coarsening_levels + 1)]
    x_batch = []
    y_batch = []
    for x, y in batch:
        x = torch.cat([x.view(-1), x.new_zeros(len(perm) - 164 ** 2)], 0)
        x = x[perm]
        x_batch.append(x)
        y_batch.append(y)
        for i in range(coarsening_levels + 1):
            g_batch[i].append(g_arr[i])

    x_batch = torch.cat(x_batch).unsqueeze(-1)
    y_batch = torch.LongTensor(y_batch)
    g_batch = [dgl.batch(g) for g in g_batch]
    return g_batch, x_batch, y_batch

train_loader = DataLoader(trainset,
                          batch_size=args.batch_size,
                          shuffle=True,
                          collate_fn=batcher,
                          num_workers=6)
test_loader = DataLoader(testset,
                         batch_size=args.batch_size,
                         shuffle=False,
                         collate_fn=batcher,
                         num_workers=6)

class MoNet(nn.Module):
    def __init__(self,
                 n_kernels,
                 in_feats,
                 hiddens,
                 out_feats):
        super(MoNet, self).__init__()
        self.pool = nn.MaxPool1d(2)
        self.layers = nn.ModuleList()
        self.readout = MaxPooling()

        # Input layer
        self.layers.append(
            GMMConv(in_feats, hiddens[0], 2, n_kernels))

        # Hidden layer
        for i in range(1, len(hiddens)):
            self.layers.append(GMMConv(hiddens[i - 1], hiddens[i], 2, n_kernels))

        self.cls = nn.Sequential(
            nn.Linear(hiddens[-1], out_feats),
            nn.LogSoftmax()
        )

    def forward(self, g_arr, feat):
        for g, layer in zip(g_arr, self.layers):
            u = g.edata['u']
            feat = self.pool(layer(g, feat, u).transpose(-1, -2).unsqueeze(0))\
                .squeeze(0).transpose(-1, -2)
            print(feat.shape)
        #print(g_arr[-1].batch_size)
        return self.cls(self.readout(g_arr[-1], feat))

class ChebNet(nn.Module):
    def __init__(self,
                 k,
                 in_feats,
                 hiddens,
                 out_feats):
        super(ChebNet, self).__init__()
        self.pool = nn.MaxPool1d(2)
        self.layers = nn.ModuleList()
        self.readout = MaxPooling()

        # Input layer
        self.layers.append(
            ChebConv(in_feats, hiddens[0], k))

        for i in range(1, len(hiddens)):
            self.layers.append(
                ChebConv(hiddens[i - 1], hiddens[i], k))

        self.cls = nn.Sequential(
            nn.Linear(hiddens[-1], out_feats),
            nn.LogSoftmax()
        )

    def forward(self, g_arr, feat):
        for g, layer in zip(g_arr, self.layers):
            feat = self.pool(layer(g, feat, [2] * g.batch_size).transpose(-1, -2).unsqueeze(0))\
                .squeeze(0).transpose(-1, -2)
        return self.cls(self.readout(g_arr[-1], feat))

if args.gpu == -1:
    device = torch.device('cpu')
else:
    device = torch.device(args.gpu)

if args.model == 'chebnet':
    model = ChebNet(2, 1, [32, 64, 128, 256], 2)
else:
    model = MoNet(10, 1, [32, 64, 128, 256], 2)

model = model.to(device)

optimizer = torch.optim.Adam(model.parameters(), lr=1e-3)
log_interval = 50

for epoch in range(10):
    print('epoch {} starts'.format(epoch))
    model.train()
    hit, tot = 0, 0
    loss_accum = 0
    for i, (g, x, y) in enumerate(train_loader):
        x = x.to(device)
        y = y.to(device)
        g = [g_i.to(device) for g_i in g]
        out = model(g, x)
        hit += (out.max(-1)[1] == y).sum().item()
        tot += len(y)
        loss = F.nll_loss(out, y)
        loss_accum += loss.item()

        if (i + 1) % log_interval == 0:
            print('loss: {}, acc: {}'.format(loss_accum / log_interval, hit / tot))
            hit, tot = 0, 0
            loss_accum = 0

        optimizer.zero_grad()
        loss.backward()
        optimizer.step()

    # model.eval()
    # hit, tot = 0, 0
    # for g, x, y in test_loader:
    #     x = x.to(device)
    #     y = y.to(device)
    #     out = model(g, x)
    #     hit += (out.max(-1)[1] == y).sum().item()
    #     tot += len(y)

    # print('test acc: ', hit / tot)

# Commented out IPython magic to ensure Python compatibility.
# %tb

