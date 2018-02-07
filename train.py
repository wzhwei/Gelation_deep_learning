#!/software/anaconda2/bin/python

import sys, tensorflow
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator

from keras.utils import to_categorical
from keras.layers import Dense, Dropout
from keras.models import Sequential
from keras.optimizers import SGD
from keras.callbacks import ModelCheckpoint
from keras import regularizers
from sklearn.utils import shuffle

def generate_one_layer_fnn(l1, kernel, shape0):
    '''
    Input:
    l1 is the number of units in the hidden layer
    kernel is the l2 regularization strength
    shape0 is the number of rows in the training sample
    
    Output:
    model is a fully connected neural network with "l1" units in hidden layer and l2 regularization strenght of "kernel"
    '''
    model = Sequential()
    model.add(Dense(l1, kernel_regularizer=regularizers.l2(kernel), activity_regularizer=regularizers.l2(0.00), input_shape=(shape0,), activation='relu'))
    model.add(Dense(2, activation='softmax'))
    my_optimizer=SGD(lr=0.01)
    model.compile(optimizer=my_optimizer, loss='categorical_crossentropy', metrics=['accuracy'])
    return model

def plot_train_history(history):
    '''
    Input:
    history object from model.fit() 
    Its history.history attribute is a record of training loss values and metrics values at successive epochs, 
    as well as validation loss values and validation metrics values (if applicable).
    
    Output:
    No return. Will save a png file showing the loss and accuray as a function of epoch. 
    '''
    plt.switch_backend('agg')
    fig, (ax1, ax2) = plt.subplots(2,1,sharex=True)
    ax1.plot(history.history['loss'])
    ax1.plot(history.history['val_loss'])
    ax1.xaxis.set_major_locator(MaxNLocator(integer=True))
    ax1.set_ylabel('loss')
    ax1.legend(['train', 'test'], loc='upper right')

    ax2.plot(history.history['acc'])
    ax2.plot(history.history['val_acc'])
    ax2.xaxis.set_major_locator(MaxNLocator(integer=True))
    ax2.set_ylabel('accuracy')
    ax2.set_xlabel('epoch')
    ax2.set_ylim([0,1])
    ax2.legend(['train', 'test'], loc='lower right')

    plt.savefig('l1_' + str(l1) + '_kernel_%.2f' % kernel + '.png')

if __name__ == '__main__':
    data = pd.read_csv('data.dat', header=None, sep=' ')
    data = shuffle(data) # Shuffle the data before splitting out the validation data set
    n_cols = data.shape[1]

    gel_state = data.iloc[:, n_cols-2].values # The n_cols-2 column in data is the target
    target = to_categorical(gel_state)
    train = data.iloc[:, :n_cols-2] - 0.5 
    data_train = train.values
    # The 0 to n_cols-2 column in data is the training data with range of [0,1] and avarage of about 0.5. 
    # Subtract the average so that the training data has both positive and negative
    
    for l1 in np.arange(20,101,20): # Parameter search for different number of layers and regularization strength
        for kernel in np.arange(0.00,0.051,0.01):
            model = generate_one_layer_fnn(l1, kernel, n_cols-2) # Generete fully connected neural nets
            filepath = 'l1_' + str(l1) + '_kernel_%.2f' % kernel + '.h5'
            checkpoint = ModelCheckpoint(filepath, monitor = 'val_loss', verbose=0, save_best_only=True, mode='max') # Save the model with the lowest validation loss
            history = model.fit(data_train, target, epochs=50, validation_split=0.3, callbacks=[checkpoint], verbose=0) # Split the data into train and validation tests
            plot_train_history(history) # Save the loss and accuray as a function of epoch in a png
