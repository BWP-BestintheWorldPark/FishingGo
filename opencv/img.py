from urllib.request import urlopen
from bs4 import BeautifulSoup as bs
from urllib.parse import quote_plus
from google_images_download import google_images_download

names = ["갈치"]

def file_download(* keyword):
    """ 키워드에 따른 이미지 파일을 크롤링(필요한 패키지 및 저장소 설치)

    Args:
     keyword :: str
         찾고자 하는 이미지의 키워드
    """
    search = ','.join(keyword)

    #실질적인 이미지 크롤링 수행 로직
    # 100개씩 이미지를 downloads 폴더에 받아옴
    response = google_images_download.googleimagesdownload()
    arguments = {"keywords": search,"limit":100,"print_urls":True, "output_directory" : "downloads", "format":"jpg"}
    paths = response.download(arguments)
    print(paths)

for a in names:
    file_download(a)