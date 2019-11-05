# -*- coding: utf-8 -*-

#Import libraries
from numpy import floor
from keras.models import Sequential
from keras.initializers import TruncatedNormal
from keras.layers import Dense, InputLayer
from keras.layers import Masking, TimeDistributed

#Build basic model architecture
def get_model(X, y, dense_one, dense_two, dense_three, activation, 
              last_activation, initialize = False, print_model = False):
    
    #Create model
    model = Sequential()
    model.add(InputLayer(input_shape = (X.shape[1],)))

    #Set up replicable initializers
    if initialize == True:
        my_init = TruncatedNormal(mean=0.0, stddev=0.05, seed=3223)
        model.add(Dense(dense_one, activation = activation,
                  kernel_initializer = my_init, bias_initializer = my_init))
    else:
        model.add(Dense(dense_one, activation = activation))
    

    model.add(Dense(dense_two, activation = activation))
    model.add(Dense(dense_three, activation = activation))
    model.add(Dense(y.shape[1]))
    if print_model is True:
        print(model.summary())
    
    return model
