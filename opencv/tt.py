import os, re, glob 
import cv2  #openCV 라이브러리 import하기
import numpy as np 
import shutil 
import h5py
from numpy import argmax 
from keras.models import load_model 
 

#분류할 카테고리 지정
categories = ["Tuna", "Sunfish", "Octopus", "Mackerel", "Cutlassfish"]

def Dataization(img_path): 
    image_w = 28 
    image_h = 28 
    img = cv2.imread(img_path)
    img = cv2.resize(img, None, fx=image_w/img.shape[1]*3, fy=image_h/img.shape[0]*3)
    return (img/256) 
  
src = [] 
name = [] 
test = [] 
image_dir = "C:/Codes/iim/" #테스트할 이미지 폴더 경로

for file in os.listdir(image_dir): 
    if (file.find('.png') is not -1):       
        src.append(image_dir + file) 
        name.append(file)
        test.append(Dataization(image_dir + file)) 
  
  
test = np.array(test) 
model = load_model('C:/Codes/opencv/Fish.h5') #사용할 모델 불러오기
predict = model.predict_classes(test) 
  
for i in range(len(test)): 
    print(name[i] + " : "+ str(categories[predict[i]]))