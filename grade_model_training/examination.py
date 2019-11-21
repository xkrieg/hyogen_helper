# -*- coding: utf-8 -*-

#Import libraries
import pandas as pd
import tensorflow as tf
from tensorflow import test
from keras.optimizers import Nadam, SGD, Adam, RMSprop
from keras.callbacks import EarlyStopping
import datetime
import os

#Local libraries
from datahelpers.preprocess import preprocessing
from experiment import get_available_gpus, gpu_select
from model.model_archt import get_model

if __name__ == "__main__":

    #Suppress Tensorflow information
    os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
    
    time_sec = 10
    X, y = preprocessing("grade_model_training/data/deep_learn_data.csv")
    
    #Force Use GPU?
    gpu_select(False)
    
    #Get model
    model = get_model(X[50:, :], y[50:, :], dense_one = 512, 
                      dense_two = 256, dense_three = 1024, activation = 'relu', 
                      last_activation = 'sigmoid', initialize = False, 
                      print_model = True)
                      
    #Compile model
    model.compile(loss='mse', optimizer = SGD(lr = .005, clipnorm = 1.),
                  metrics=['mean_squared_error', 'mean_absolute_error', 
                           'mean_absolute_percentage_error'])
    
    #Set early stopping
    earlystop = EarlyStopping(monitor = 'mean_squared_error', min_delta = 0.001,
                              patience = 9, mode = 'auto')
    
    #Train model
    out = model.fit(X, y, batch_size = 10, epochs = 1000, validation_split = .10,
                    callbacks = [earlystop])
                    
    #Serialize weights to HDF5
    current_date = str(datetime.datetime.now())
    model.save_weights("_".join(["grade_model_training/model/weights", current_date, ".h5"]))
    print("Saved model to disk")
    
    #Predict
    y_pred = pd.DataFrame(model.predict(X[0:50, :].round(0)))
    y_pred.columns = ["predicted_grade"]
    
    #Check
    y_pred["actual_grade"] = y[0:50, :]
    
    print(y_pred)
