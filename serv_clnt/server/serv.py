import queue
import socket, threading
import sys
from PIL import Image
import os
from cv2 import imshow
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

# image_dir = "../../iim" #테스트할 이미지 폴더 경로
# img_path = 'C:/Codes/iim/Image.png'
sock_list = []
# thread_list = []
BUF_SIZE = 1024

def Dataization(img): 
    image_w = 28 
    image_h = 28
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
            elif recv_msg.startswith('rank/'):
                self.send_rank()
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
     
    def send_rank(self, recv_msg):
        con, cur = con_db()
        recv_list = recv_msg.split('/')
        id_msg = "id"
        count_msg = "count"
        
        query = f"SELECT userid, fish_count FROM fish_record WHERE fishname = {recv_list[1]} ORDER BY fish_count DESC LIMIT 5"
        try:
            cur.execute(query)
        except pymysql.err.InternalError as error:
            code, msg = error.args
            self.sock.send("sql_error".encode())
            print(f"error code {code}: {msg}")
            
        result = cur.fetchall()
        result = list(result)
        for data in list:
            id_msg = id_msg+"/"+data[0]
            count_msg = count_msg+"/"+data[1]
        self.sock.send(id_msg.encode())
        check = self.sock.recv(BUF_SIZE)
        if check == "OK":
            self.sock.send(count_msg.encode())
        con.close()
        return
            
                    
    def compare_fish(self):
        global test, name, src
        src = [] 
        name = [] 
        test = []
        #바이트로 바꾼 이미지 받는 부분
        self.sock.send("send_image".encode())
        img_len = self.sock.recv(BUF_SIZE)
        img_len = img_len.decode()
        print("imglen: "+img_len)
        byte_image = self.sock.recv(int(img_len))

        encode_data = np.frombuffer(byte_image, dtype= np.uint8)
        decoded_img=cv2.imdecode(encode_data, cv2.IMREAD_COLOR)

        gray = cv2.cvtColor(decoded_img, cv2.COLOR_RGB2GRAY)
        ret, binary = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)
        binary = cv2.bitwise_not(binary)
        contours, hierarchy = cv2.findContours(binary, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_NONE)

        for i in range(len(contours)):
            cv2.drawContours(decoded_img, [contours[i]], 0, (0, 0, 255), 2)
            cv2.putText(decoded_img, "", tuple(contours[i][0][0]), cv2.FONT_HERSHEY_COMPLEX, 0.8, (0, 255, 0), 1)

        # for file in os.listdir(image_dir): 
        #     if (file.find('.png') != -1):       
        #         src.append(image_dir + file) 
        #         name.append(file)
        
        test_arr = np.array(list(Dataization(decoded_img))) 
        
        model = load_model('../../opencv/Fish.h5') #사용할 모델 불러오기
        predict = model.predict_classes(test_arr)
        
        print("결과" + " : "+ categories[predict[i]] + "/" + ko_categories[predict[i]])
        #self.sock.send(ko_categories[predict[i]].encode())
        
 
    def send(self, message):
        print('tcp server :: ',message)
        try:
            for i in range(len(self.sock_list)):
                self.sock_list[i].sendall(message.encode())
        except:
             pass
if __name__ == '__main__':
    andRaspTCP = TCPServer(host, port)
    andRaspTCP.start()