import socket
import sys
from PIL import Image
import os
from array import array
import cv2
 
host = '127.0.0.1'
port = 4000
addr = (host, port)
img_path = 'C:/Codes/pan.png'
resize_img_path = 'C:/Codes/re_pan.png'
 
pr = ['1.height', '2.width']
 
def run():
  with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    
    try:
      s.connect(addr)
    except Exception as e:
      print('서버 (%s:%s)에 연결 할 수 없습니다.' % addr)
      sys.exit()
    print('서버 (%s:%s)에 연결 되었습니다.' % addr)

    while True:
      #비트맵 바이트로 변환시키기
      img = cv2.imread(img_path,cv2.IMREAD_COLOR)
      image_w = 28 
      image_h = 28 
      resize_img = cv2.resize(img, None, fx=image_w/img.shape[1]*3, fy=image_h/img.shape[0]*3)
      cv2.imwrite(resize_img_path,resize_img)
      
      fd = open(resize_img_path, "rb")
      b = bytearray(fd.read())
      s.sendall(b) # 서버로 보내기
      print('바이트 이미지 전송 완료')
      fd.close()
  
      os.remove(resize_img_path)
  
      resp = s.recv(1024)
      img = cv2.imread(img_path,cv2.IMREAD_COLOR)
      img = cv2.putText(img, resp.decode(), (50, 50), cv2.FONT_HERSHEY_PLAIN, 2, (0, 255, 0), 1, cv2.LINE_AA)
      cv2.imshow("img",img)
      cv2.waitKey()
    s.close()
 
if __name__ == '__main__':
  run()
  cv2.waitKey()