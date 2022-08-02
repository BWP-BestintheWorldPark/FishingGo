#로컬 이미지로 데이터셋 만들기 
import os, re, glob  
import cv2  #openCV 라이브러리 import하기
import numpy as np  
from sklearn.model_selection import train_test_split 

 

#현재 로컬 이미지 폴더 구조

#dataset/25/road, water, building, green
imagePath = 'C:/Codes/image'
categories = ["Tuna", "Sunfish", "Octopus", "Mackerel", "Cutlassfish"]

#dataset/25 하위 폴더의 이름이 카테고리가 됨. 동일하게 맞춰줘야한다.
nb_classes = len(categories)  

image_w = 28 
image_h = 28 

X = []  
Y = []
contours = []

for idx, cate in enumerate(categories):  
    label = [0 for i in range(nb_classes)]  
    label[idx] = 1  
    image_dir = imagePath+'/'+cate+'/'  
     
    for top, dir, f in os.walk(image_dir): 
        for filename in f:  
            print(image_dir+filename)
            img = cv2.imread(image_dir+filename,cv2.IMREAD_COLOR)
            gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
            ret, binary = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)
            binary = cv2.bitwise_not(binary)
            contours, hierarchy = cv2.findContours(binary, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_NONE)
            for i in range(len(contours)):
                cv2.drawContours(img, [contours[i]], 0, (0, 0, 255), 2)
                cv2.putText(img, "", tuple(contours[i][0][0]), cv2.FONT_HERSHEY_COMPLEX, 0.8, (0, 255, 0), 1)
            img = cv2.resize(img, None, fx=image_w/img.shape[1]*3, fy=image_h/img.shape[0]*3)
            X.append(img/256)  
            Y.append(label)
             
X = np.array(X)  
Y = np.array(Y)  

X_train, X_test, Y_train, Y_test = train_test_split(X,Y)  
xy = (X_train, X_test, Y_train, Y_test) 

 

#생성된 데이터셋을 저장할 경로와 파일이름 지정
np.save("C:/Codes/opencv/fish.npy", xy)