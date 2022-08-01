import socket
import sys
from PIL import Image
import os
from array import array
import cv2

from PyQt5.QtWidgets import *
from PyQt5.QtCore import QThread, pyqtSlot
from PyQt5 import QtCore 
from PyQt5.QtCore import Qt
from PyQt5 import QtWidgets
from PyQt5 import QtGui
from PyQt5 import uic
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import QCoreApplication
from numpy import sign
 
BUF_SIZE = 1024
host = '127.0.0.1'
port = 9011
addr = (host, port)
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

img_path = 'C:/Codes/pan.png'
resize_img_path = 'C:/Codes/re_pan.png'

pr = ['1.height', '2.width']

def connect_server():
    try:   
        sock.connect(addr)
    except Exception as e:
        print('서버 (%s:%s)에 연결 할 수 없습니다.' % addr)
        sys.exit()
        print('서버 (%s:%s)에 연결 되었습니다.' % addr)

def send_img():
    while True:
        #비트맵 바이트로 변환시키기
        img = cv2.imread(img_path,cv2.IMREAD_COLOR)
        image_w = 28 
        image_h = 28 
        resize_img = cv2.resize(img, None, fx=image_w/img.shape[1]*3, fy=image_h/img.shape[0]*3)
        cv2.imwrite(resize_img_path,resize_img)

        fd = open(resize_img_path, "rb")
        b = bytearray(fd.read())
        sock.sendall(b) # 서버로 보내기
        print('바이트 이미지 전송 완료')
        fd.close()

        os.remove(resize_img_path)

        resp = sock.recv(1024)
        img = cv2.imread(img_path,cv2.IMREAD_COLOR)
        img = cv2.putText(img, resp.decode(), (50, 50), cv2.FONT_HERSHEY_PLAIN, 2, (0, 255, 0), 1, cv2.LINE_AA)
        cv2.imshow("img",img)
        cv2.waitKey()
    sock.close()
 
class Login(QDialog):
    def __init__(self):
        super().__init__()
        self.ui = uic.loadUi("ui/login.ui", self)
        
        self.login_btn.clicked.connect(self.login_btn_clicked)
        self.signup_btn.clicked.connect(self.signup_btn_clicked)
        self.exit_btn.clicked.connect(self.exit_btn_clicked)
        
    def login_btn_clicked(self):
        id = self.ID_text.text()    
        pw = self.PW_text.text()
        
        if id == "" or pw == "":
            QMessageBox().about(self, "error", "입력하지 않은 내용이 있습니다.")
            return
            
        send_msg = f"login/{id}/{pw}"
        sock.send(send_msg.encode())
        recv_msg = sock.recv(BUF_SIZE)
        recv_msg = recv_msg.decode()
        if "OK" in recv_msg:
            window = main_window()
            self.close()
            window.exec_()
        else:
            QMessageBox().about(self, "로그인 실패","아이디 혹은 비밀번호가 틀렸습니다.\n다시 시도해주세요.")

    def signup_btn_clicked(self):
        window = signup()
        window.exec_()
        self.show()
    
    def exit_btn_clicked(self):
        self.close()
        exit(0)
        
class signup(QDialog):
    def __init__(self):
        super().__init__()
        self.ui = uic.loadUi("ui/signup.ui", self)
        
        self.check = ""
        
        self.check_btn.clicked.connect(self.check_btn_clicked)
        self.signup_btn.clicked.connect(self.signup_btn_clicked)
        self.exit_btn.clicked.connect(self.exit_btn_clicked)
        
    def check_btn_clicked(self):
        id = self.ID_text.text()
        
        if id == "":
            QMessageBox().about(self, "error", "아이디 칸에 아무것도 입력하지 않았습니다.")
            return
        
        send_msg = f"id_check/{id}"
        sock.send(send_msg.encode())
        recv_msg = sock.recv(BUF_SIZE)
        recv_msg = recv_msg.decode()
        if "OK" in recv_msg:
            QMessageBox().about(self, "확인 완료", "중복 확인 완료")
            self.check = id
        else:
            QMessageBox().about(self, "아이디 중복", "중복되는 아이디입니다.\n 다시 시도해주세요.")

    def signup_btn_clicked(self):
        id = self.ID_text.text()
        pw = self.PW_text.text()
        name = self.Name_text.text()
        
        if id == "" or pw == "" or name =="":
            QMessageBox().about(self, "error", "입력하지 않은 내용이 있습니다.")
            return
        
        if self.check == "" or self.check != id:
            QMessageBox().about(self, "error", "중복 확인이 필요합니다.")
            return
        
        send_msg = f"signup/{id}/{pw}/{name}"
        sock.send(send_msg.encode())
        recv_msg = sock.recv(BUF_SIZE)
        recv_msg = recv_msg.decode()
        if "OK" in recv_msg:
            QMessageBox().about(self, "회원가입 성공", "가입을 환영합니다.")
            self.close()
        elif "sql_error" in recv_msg:
            QMessageBox().about(self, "데이터베이스 오류", "데이터베이스 오류.\n 프로그램을 종료합니다.")
            exit(1)
        else:
            QMessageBox().about(self, "아이디 중복", "중복되는 아이디입니다.\n 다시 시도해주세요.")
    
    def exit_btn_clicked(self):
        self.close()
        
class main_window(QDialog):
    def __init__(self):
        super().__init__()
        self.ui = uic.loadUi("ui/main_window.ui", self)

        self.cap_btn.clicked.connect(self.cap_btn_clicked)
        self.upload_btn.clicked.connect(self.upload_btn_clicked)
        
    def cap_btn_clicked(self):
        window = capture()
        self.hide()
        window.exec_()
        self.show()
    
    def upload_btn_clicked(self):
        window = load()
        self.hide()
        window.exec_()
        self.show()
  
class capture(QDialog):
    def __init__(self):
        super().__init__()
        self.ui = uic.loadUi("ui/capture.ui", self)
        
        self.flag = 0
        self.cam = cv2.VideoCapture(0)
        
        self.ret, self.frame = self.cam.read()
        self.height, self.width = self.frame.shape[:2]
        
        self.VideoSignal1 = QtCore.pyqtSignal(QtGui.QImage)
        self.VideoSignal2 = QtCore.pyqtSignal(QtGui.QImage)
          
class load(QDialog):
    def __init__(self):
        super().__init__()
        self.ui = uic.loadUi("ui/load.ui", self)
        self.pixmap = QPixmap()
        self.pixmap = self.pixmap.scaled(430, 330, Qt.KeepAspectRatio)
        self.image_path = ""
        
        self.load_btn.clicked.connect(self.load_btn_clicked)
        self.send_btn.clicked.connect(self.send_btn_clicked)
        self.exit_btn.clicked.connect(self.exit_btn_clicked)
        
        
    def load_btn_clicked(self):
        image = QFileDialog.getOpenFileName(self, 'Fish Image Load', './picture', 'Image File(*.png *.jpg *.jpeg)')
        if image[0]:
            print("image file loaded: " + image[0])
            self.image_path = image[0]
        else:
            print("image not loaded")
            return
        
        self.pixmap.load(self.image_path)
        self.pic_label.setPixmap(self.pixmap)    

    def send_btn_clicked(self):
        sock.send("compare".encode())
        recv_msg = sock.recv(BUF_SIZE)
        if recv_msg == "send_image":
            fd = open(resize_img_path, "rb")
            byte_image = bytearray(fd.read())
            sock.sendall(byte_image) # 서버로 보내기
            print('바이트 이미지 전송 완료')
            fd.close() 
    
    def exit_btn_clicked(self):
        self.close()
        
        
if __name__ == '__main__':
    #send_img()
    connect_server()
    app = QApplication(sys.argv)
    window = Login(); 
    window.show();
    app.exec_()         
