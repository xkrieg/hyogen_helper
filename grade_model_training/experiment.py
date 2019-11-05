# -*- coding: utf-8 -*-

#Set seed
seed_no = 3223
from numpy.random import seed
seed(seed_no)
from tensorflow import set_random_seed
set_random_seed(seed_no)

#Import libraries
import numpy as np
import pandas as pd
import talos as ta
import tensorflow as tf
from talos.utils.gpu_utils import multi_gpu
from talos.model.normalizers import lr_normalizer
from sklearn.preprocessing import StandardScaler
from tensorflow import test
from tensorflow.python.client import device_lib
from keras.optimizers import Adam, Nadam, RMSprop, SGD
from keras.callbacks import EarlyStopping
import os

#Local libraries
from model.model_archt import get_model
from datahelpers.preprocess import preprocessing

#Check gpu support
def get_available_gpus():
    local_device_protos = device_lib.list_local_devices()
    return len([x.name for x in local_device_protos if x.device_type == 'GPU'])

def gpu_select(implement = True):
    
    #Suppress Tensorflow information
    os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
    
    #Ensure GPU functioning
    if implement == True:
        if test.gpu_device_name():
            print('Default GPU Device: {}'.format(test.gpu_device_name()))
            if get_available_gpus() > 1: #Add multi-gpu support if available
                model = multi_gpu(model)
        else:
            print("Please install GPU version of TF")
            quit()

def import_model(X_train, y_train, X_val, y_val, params):
    
    #Load model architecture
    model = get_model(X_train, y_train, params['dense_one'], params['dense_two'],
                      params['dense_three'], params['activation'],
                      params['last_activation'], initialize = True)
    
    #Add multi-gpu support if available
    if get_available_gpus() > 1:
        model = multi_gpu(model)
    
    #Compile model
    model.compile(loss = params['losses'], metrics=['mean_squared_error', 
                 'mean_absolute_error', 'mean_absolute_percentage_error'], 
                 optimizer = params['optimizer'](lr=lr_normalizer(params['lr'], 
                                                 params['optimizer'])))

    #Set early stopping
    earlystop = EarlyStopping(monitor='categorical_accuracy', min_delta=0.01,
                              patience=9, mode='auto')

    #Train model
    out = model.fit(X_train, y_train, batch_size = params['batch_size'],
                    epochs = params['epochs'], validation_data=[X_val, y_val],
                    verbose=0, callbacks = [earlystop])

    return out, model

def run_experiment(time_sec, params, outfile):
    X, y = preprocessing('grade_model_training/data/deep_learn_data.csv')

    #Set scan paramters
    scan_object = ta.Scan(X, y, model = import_model, params = params, 
                          dataset_name = "grade_model_training/output/results", 
                          experiment_no = outfile, grid_downsample = .2)

    return scan_object
    
if __name__ == "__main__":
    
    #Suppress Tensorflow information
    tf.logging.set_verbosity(tf.logging.ERROR)
    os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
    
    for seconds in [3]:#, 45, 60]:
    
        #print("".join(["Number of Seconds: ", str(seconds)]))
    
        #Determine parameters
        p = {'dense_one': [32, 64, 128, 256, 512, 1024],
             'dense_two': [32, 64, 128, 256, 512, 1024],
             'dense_three': [32, 64, 128, 256, 512, 1024],
             'activation': ['relu'],
             'last_activation': [''],
             'losses': ['mse'],
             'lr': [.00001, .0001, .0005, .001, .005],
             'optimizer': [Adam, Nadam, RMSprop, SGD],
             'batch_size': [2, 10, 50, 200, 500],
             'epochs': [200]}
    
        #Force Use GPU?
        gpu_select(False)
    
        #Name experiment
        expname = "_".join(["layer", str(seconds)])
    
        #Start experiment
        scanned = run_experiment(seconds, p, expname)
        r = ta.Reporting(scanned)
        
        #Create graph
        call(['Rscript', 'data_helper/plot_gen.R', expname])
        
        #Display cursory results
        print("The highest model achieved an accuracy of %s \n" % r.high('val_categorical_accuracy'))
        print("The best identified parameters are as follows:")
        print(r.data.ix[r.rounds2high('val_categorical_accuracy')])
