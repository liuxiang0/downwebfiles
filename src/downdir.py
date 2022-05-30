from secrets import choice
import sys
from time import time, localtime
from cv2 import HoughCircles
import requests
import os
#from clint.textui import progress
from bs4 import BeautifulSoup as soup
import urllib.request as urlreq
import re

from parsers import parser, spend, getUA

SMALLFILE = 512000  # 500KB 

def getHRefs(url):
    '''url: 给定的网络连接website
    return: 指定网站包含的超链接列表
    调用模块：requests

    '''
    response = requests.get(url, headers=getUA())
    if response.status_code == 200:
        rData = response.text
    else:
        rData = ''
        raise ConnectionError()

    #print(response.headers)  #debug info
    response.close()

    if rData == '':
        return None
    refsList = soup(rData, "html.parser").findAll(href=True)
    return [refsList[i]['href'] for i in range(len(refsList))]


def parserHRefs(url):
    '''url: 给定的网络连接website
    return: 指定网站包含的 超链接列表List, 每项形如 <a href="dev-clean.tar.gz">dev-clean.tar.gz</a>
    '''
    
    req = requests.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    datum = req.text
    req.close() 

    pagesoup = soup(datum, "html.parser").contents
    #soup()得到的结果类型 --type(pagesoup)-- 是 <class 'bs4.BeautifulSoup'>
    #soup(*).contents得到列表形式的内容List.

    #raw_text = str(pagesoup) 将列表信息变成字符串信息, 否则报错
    # TypeError: cannot use a string pattern on a bytes-like object Solution
    # 建立正则表达式(Regular Expression), 解析出 href 
    res = r'<a href="(.*?)">'
    # 仍然含有 href 等字样，改用 getHRefs(url)
    return re.findall(res, str(pagesoup), re.I) 


def downone(url, savedfile):
    '''一次性下载小文件，并保存至 savedfile.'''

    response = requests.get(url, headers=getUA())
    if response.status_code == 200:
        rData = response.content
    else:
        raise ConnectionError()
        #rData = ''
    response.close()
    with open(savedfile, "wb") as f:
        f.write(rData)


def download(url, file_path):
    '''
    TODO: 
    1. 对于小文件，无须分段传输，如何分解出小文件的直接下载？
    2. 对于超大文件，如何多线程下载？
    3. 最好都改成 urllib 的调用。
    4. 如果中途退出，如何无人值守自动启动上一次命令？
    '''
    # 屏蔽warning信息
    requests.packages.urllib3.disable_warnings()    
    # 第一次请求是为了得到文件总大小
    r1 = requests.get(url, stream=True, verify=False)
    total_size = int(r1.headers['Content-Length'])
    
    if os.path.exists(file_path):
        temp_size = os.path.getsize(file_path)  # 本地已经下载的文件大小
    else:
        temp_size = 0
    # 显示一下下载了多少, 共有多少
    print("已下载了{0}，共有{1} !".format(temp_size, total_size))
    # 核心部分，请求下载时，从本地文件已经下载过的后面下载，断点续传开始...
    headers = {'Range': 'bytes=%d-' % temp_size}
    # 重新请求网址，加入新的请求头
    r = requests.get(url, stream=True, verify=False, headers=headers)

    # 写入文件要注意:"ab"表示追加形式写入文件
    with open(file_path, "ab") as f:
        #for chunk in progress.bar(r.iter_content(chunk_size = 2391975), expected_size=(total_size/1024) + 1):
        for chunk in r.iter_content(chunk_size=SMALLFILE): #51200=500K, 1048576=1M
            if chunk:
                temp_size += len(chunk)
                f.write(chunk)
                f.flush()

                #这是下载实现进度显示
                done = int(50 * temp_size / total_size)
                sys.stdout.write("\r[%s%s] %d%%" % ('█' * done, ' ' * (50 - done), 100 * temp_size / total_size))
                sys.stdout.flush()
    print()  # 避免上面\r 回车符


def downloadDirectory(url, savedir):
    '''下载指定互联网地址中的整个目录下的 href 超链接内容'''

    urls = getHRefs(url)
    # Notes: 跳过前面5个没有用的数据
    # urls = urls[5:]
    for one in urls:
        print("正在下载{0}...".format(one))
        download('/'.join([url,one]), '/'.join([savedir, one]))

 
if __name__ == '__main__':
    args = parser()
    url = args['url']
    downfile = args['downfile']

    start = time()
    
    # 创建目录
    savedir = ''
    a = url.split('/')  #有没有'\'为分隔符?
    for i in range(1, len(a)):
        if a[-i] != '':
            savedir = a[-i]
            break
    if not os.path.exists(savedir):
        os.makedirs(savedir)

    if downfile is None: # 下载整个网页中包含的websites
        downloadDirectory(url, savedir)
    else:
        download_url = '/'.join([url, downfile])
        download(download_url, '/'.join([savedir, downfile]))
    
    print(r"下载用时: {0}".format(spend(time() - start)))
    print(r"结束时间：{}".format(localtime()))
