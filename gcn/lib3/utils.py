import os 
import scipy.io
import numpy as np
from matplotlib import pyplot as plt
import pandas as pd 
from sklearn.feature_selection import SelectFromModel
from sklearn.linear_model import Lasso
def load_connect():
    import os 
    import scipy.io
    import numpy as np
    from matplotlib import pyplot as plt
    import pandas as pd  
    test=scipy.io.loadmat('../data/adni_connectome_aparc_length.mat')
    aparcl=np.array(test['connectome_aparc0x2Baseg_length'])
    print("Length 1:", aparcl.shape)
    
    test=scipy.io.loadmat('../data/adni_connectome_aparc_count.mat')
    aparcc=np.array(test['connectome_aparc0x2Baseg_count'])
    print("Count 1:", aparcc.shape)
    
    test=scipy.io.loadmat('../data/adni_connectome_aparc2009_length.mat')
    aparc2l=np.array(test['connectome_aparc0x2Ea2009s0x2Baseg_length'])
    print("Length 2:", aparc2l.shape)
    
    test=scipy.io.loadmat('../data/adni_connectome_aparc2009_count.mat')
    aparc2c=test['connectome_aparc0x2Ea2009s0x2Baseg_count']
    print("Count 2:", aparc2c.shape)
    
    return (aparcl,aparcc,aparc2l,aparc2c)
    
def load_mor():
    test=scipy.io.loadmat('../data/ADNI_morph_100.mat')
    morphdata = np.array(test['M1_new'])
    print("Morphometry Data Shape:", morphdata.shape)
    
    return morphdata

def load_y():
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
    #print("y shape:",y.shape)
    return y
    
def feat_sel(X,y,nfeat):
    print("X SHAPE:", X.shape, "\ny SHAPE:",y.shape)
    clf = Lasso(alpha=0.001, normalize=True).fit(X, y)
    importance = np.abs(clf.coef_)
    count = 0
    a = []
    b = []
    for ix,i in enumerate(importance):
      if i != 0:
        count +=1
        a.append(i)
        b.append(ix)
    #print(count,a,b)
    idx_oho = importance.argsort()[-(nfeat+1)]
    threshold = importance[idx_oho] + 0.000000000001
    
    idx_features = (-importance).argsort()[:nfeat]
    #print(X[idx_features])
    print('Selected features: {}'.format(idx_features))
    
    sfm = SelectFromModel(clf, threshold=threshold)
    sfm.fit(X, y)
    X_transform = sfm.transform(X)
    
    n_features = sfm.transform(X).shape[1]
    print("# Features Selected:", n_features)
    
    return X_transform
    
def imp_arg():
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
    argparser.add_argument("--model", type=str, default="monet",
                           help="model to use, chebnet/monet")
    argparser.add_argument("--batch-size", type=int, default=1,
                           help="batch size")
    argparser.add_argument("--fold", type=int, default=10,
                           help="Number of folds")
    args, unknown = argparser.parse_known_args()
    
    return args, unknown