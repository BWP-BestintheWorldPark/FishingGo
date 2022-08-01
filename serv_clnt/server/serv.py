import queue
import socket, threading
import sys
from PIL import Image
import os
import numpy as np
import cv2
import h5py
from numpy import argmax 
from keras.models import load_model
from paramiko import HostKeys
import pymysql

host = '127.0.0.1'
port = 9011
 
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

#분류할 카테고리 지정
categories = ["Tuna", "Sunfish", "Octopus", "Mackerel", "Cutlassfish"]
ko_categories = ["참치", "개복치", "문어", "고등어", "갈치"]
pr = ['height', 'width', '']

image_dir = "C:/Codes/iim/" #테스트할 이미지 폴더 경로
img_path = 'C:/Codes/iim/Image.png'
sock_list = []
# thread_list = []
BUF_SIZE = 1024

def Dataization(img_path): 
    image_w = 28 
    image_h = 28 
    img = cv2.imread(img_path)
    img = cv2.resize(img, None, fx=image_w/img.shape[1]*3, fy=image_h/img.shape[0]*3)
    return (img/256) 
  
def con_db():
    con = pymysql.connect(host = '10.10.20.44', user='admin', 
                          password='1234', db='fishgo')
    cur = con.cursor()
    return con, cur

class TCPServer(threading.Thread):
    def __init__(self, HOST, PORT):
        threading.Thread.__init__(self)
 
        self.HOST = HOST
        self.PORT = PORT
        
        self.serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.serverSocket.bind((self.HOST, self.PORT))
        self.serverSocket.listen(1)
  
    def run(self):
        global sock_list, thread_list
        try:
            print( 'tcp server :: server wait...')
            while True:
                sock, clnt_addr = self.serverSocket.accept()
                sock_list.append(sock)
                print("tcp server :: connect :", clnt_addr)
    
                subThread = TCPServerThread(sock, clnt_addr)
                subThread.start()
                # thread_list.append(subThread)
        except:
            print("tcp server :: serverThread error")
 
    # def sendAll(self, message):
    #     try:
    #         self.thread_list[0].send(message)
    #     except:
    #         pass

class TCPServerThread(threading.Thread):
    def __init__(self, sock, clnt_addr):
        threading.Thread.__init__(self)
 
        self.sock = sock
        self.clnt_addr = clnt_addr
 
    def run(self):
        global sock_list, thread_list
        while True:
            recv_msg = self.sock.recv(BUF_SIZE)
            if not recv_msg:
                sock_list.remove(self.sock)
                # thread_list.remove(self)
                break
            recv_msg = recv_msg.decode()
            print(recv_msg)
            if recv_msg.startswith('login/'):
                self.login(recv_msg)
            elif recv_msg.startswith('id_check/'):
                self.id_check(recv_msg)
            elif recv_msg.startswith('signup/'):
                self.signup(recv_msg)
            elif recv_msg.startswith('compare'):
                self.compare_fish()
                
    def login(self, recv_msg):
        con, cur = con_db()
        recv_list = recv_msg.split('/')
        query = f"SELECT userpw FROM user WHERE userid=\'{recv_list[1]}\'"
        
        try:
            cur.execute(query)
        except pymysql.err.InternalError as error:
            code, msg = error.args
            self.sock.send("sql_error".encode())
            print(f"error code {code}: {msg}")

        user_pw = cur.fetchone()
        if not user_pw or (recv_list[2],) != user_pw:
            self.sock.send("NO".encode())
        else:
            self.sock.send("OK".encode())
        
        con.close()
        return
    
    def id_check(self, recv_msg):
        con, cur = con_db()
        recv_list = recv_msg.split('/')
        query = f"SELECT userid FROM user WHERE userid = \'{recv_list[1]}\'"
        print(query)
        try:
            cur.execute(query)
        except pymysql.err.InternalError as error:
            code, msg = error.args
            self.sock.send("sql_error".encode())
            print(f"error code {code}: {msg}")
        
        result = cur.fetchone()
        if not result:
            self.sock.send("OK".encode())
        else:
            self.sock.send("NO".encode())
        
        con.close()
                
        
    
    def signup(self, recv_msg):
        con, cur = con_db()
        recv_list = recv_msg.split('/')
        
        query = f"INSERT INTO user(userid, userpw, username) VALUES(\'{recv_list[1]}\', \'{recv_list[2]}\', \'{recv_list[3]}\')" 
        try:
            cur.execute(query)
            con.commit()
        except pymysql.err.InternalError as error:
            code, msg = error.args
            self.sock.send("sql_error".encode())
            print(f"error code {code}: {msg}")
        
        self.sock.send("OK".encode())
        con.close()
        return
                    
    def compare_fish(self):
        global test, name, src
        src = [] 
        name = [] 
        test = []
        #바이트로 바꾼 이미지 받는 부분
        self.sock.send("send_image")
        byte_image = self.sock.recv(65536)
        for i in pr:
            # when break connection
            if(i == ""):
                data = np.fromstring(byte_image, dtype='uint8')
                decimg=cv2.imdecode(data,1)

                cv2.imwrite(img_path,decimg)
                gray = cv2.cvtColor(decimg, cv2.COLOR_RGB2GRAY)
                ret, binary = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)
                binary = cv2.bitwise_not(binary)
                contours, hierarchy = cv2.findContours(binary, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_NONE)

                for i in range(len(contours)):
                    cv2.drawContours(decimg, [contours[i]], 0, (0, 0, 255), 2)
                    cv2.putText(decimg, "", tuple(contours[i][0][0]), cv2.FONT_HERSHEY_COMPLEX, 0.8, (0, 255, 0), 1)

                #cv2.imwrite(img_path,decimg)

                for file in os.listdir(image_dir): 
                    if (file.find('.png') != -1):       
                        src.append(image_dir + file) 
                        name.append(file)
                test.append(Dataization(image_dir + file)) 


                test = np.array(test) 
                model = load_model('C:/Codes/opencv/Fish.h5') #사용할 모델 불러오기
                predict = model.predict_classes(test)
                
                for i in range(len(test)): 
                    print("결과" + " : "+ categories[predict[i]] + "/" + ko_categories[predict[i]])
                    self.sock.send(ko_categories[predict[i]].encode())
                cv2.waitKey(0)
                break
            data = 1000
 
    def send(self, message):
        print('tcp server :: ',message)
        try:
            for i in range(len(self.sock_list)):
                self.sock_list[i].sendall(message.encode())
        except:
             pass

andRaspTCP = TCPServer(host, port)
andRaspTCP.start()