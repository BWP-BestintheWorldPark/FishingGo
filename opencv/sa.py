from keras.models import Sequential
from keras.layers import Dropout, Activation, Dense
from keras.layers import Flatten, Convolution2D, MaxPooling2D
from keras.models import load_model
import numpy as np
import h5py
import cv2
import warnings

warnings.filterwarnings('ignore')

categories = ["Tuna", "Sunfish", "Octopus", "Mackerel", "Cutlassfish"]
num_classes = len(categories)

X_train, X_test, Y_train, Y_test = np.load('C:/Codes/opencv/fish.npy', allow_pickle = True)

model = Sequential()
model = Sequential()

model.add(Convolution2D(16, 16, 3, border_mode='same', activation='relu', 
                        input_shape=X_train.shape[1:]))

model.add(MaxPooling2D(pool_size=(2, 2)))
model.add(Dropout(0.25))

model.add(Convolution2D(64, 3, 3, activation='relu'))
model.add(MaxPooling2D(pool_size=(2, 2)))
model.add(Dropout(0.25))

model.add(Convolution2D(64, 3, 3))
model.add(MaxPooling2D(pool_size=(2, 2)))
model.add(Dropout(0.25))

model.add(Flatten())
model.add(Dense(256, activation = 'relu'))
model.add(Dropout(0.5))
model.add(Dense(num_classes,activation = 'softmax'))

model.compile(loss='binary_crossentropy',optimizer='Adam',metrics=['accuracy'])
model.fit(X_train, Y_train, batch_size=32, nb_epoch=149)

model.save('C:/Codes/opencv/Fish.h5')