# -*- coding: utf-8 -*-

#Import required libraries
from sklearn.preprocessing import MultiLabelBinarizer, StandardScaler
from progressbar import ProgressBar
import numpy as np
import pandas as pd
import os
import gc

#Read relevant files and return X, y
def preprocessing(file):

    #Load file
    df = pd.read_csv(file)
    df = df.reindex(np.random.RandomState(seed=3223).permutation(df.index))

    #Make X Window Stack
    X = df.values[:,4:]
    X = StandardScaler().fit_transform(X)
    print(X.shape)
    
    #Extract likert outcomes
    y = df.values[:, :1].astype('int8')
    print(y.shape)
    
    return(X, y)

#Simple test script
if __name__ == "__main__":
    preprocessing('grade_model_training/data/deep_learn_data.csv')
