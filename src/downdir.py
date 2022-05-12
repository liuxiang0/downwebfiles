import sys
from time import time
import requests
import os
#from clint.textui import progress
import argparse
from bs4 import BeautifulSoup as soup
import urllib.request as urlreq
import re

def parser():
    # Construct an argument parser
    all_args = argparse.ArgumentParser(description='下载大文件，支持断点续传，仅供参考！')

    # Add arguments to the parser
    all_args.add_argument("-U", "--url", required=True,
    help="web网址")
    all_args.add_argument("-F", "--downfile", required=False,
    help="文件名")
    #all_args.add_argument("-S", "--savefile", required=False,
    #help="保存的本地文件名(可选)，缺省为原文件名")
    args = vars(all_args.parse_args())  # to Dict
    return args
 
def soupURLs(url):
    '''url: 给定的网络连接website
    return: 指定网站包含的 超链接列表List, 每项形如 <a href="dev-clean.tar.gz">dev-clean.tar.gz</a>
    '''
    
    req = urlreq.Request(url,headers={'User-Agent': 'Mozilla/5.0'})
    client = urlreq.urlopen(req)
    datum = client.read().decode('utf-8') # 解码后的数据集
    client.close() 

    pagesoup = soup(datum, "html.parser") #.contents
    #el = pagesoup.find(href=True), print(el['href']) 
    elements = pagesoup.findAll(href=True)  #type(elements) is <class 'bs4.element.ResultSet'>
    return [elements[i]['href'] for i in range(len(elements))]

def parserURLs(url):
    '''url: 给定的网络连接website
    return: 指定网站包含的 超链接列表List, 每项形如 <a href="dev-clean.tar.gz">dev-clean.tar.gz</a>
    '''
    
    req = urlreq.Request(url,headers={'User-Agent': 'Mozilla/5.0'})
    client = urlreq.urlopen(req)
    datum = client.read().decode('utf-8') # 解码后的数据集
    client.close() 

    pagesoup = soup(datum, "html.parser").contents
    #soup()得到的结果类型 --type(pagesoup)-- 是 <class 'bs4.BeautifulSoup'>
    #soup(*).contents得到列表形式的内容List.

    #raw_text = str(pagesoup) 将列表信息变成字符串信息, 否则报错
    # 建立正则表达式(Regular Expression), 解析出 href 
    res = r"<a .*?href=.*?<\/a>"
    # 仍然含有 href 等字样，改用 soupURLs(url)
    return re.findall(res, str(pagesoup), re.I) 


def download(url, file_path):
    '''
    TODO: 
    1. 对于小文件，无须分段传输，如何分解出小文件的直接下载？
    2. 对于超大文件，如何多线程下载？
    3. 最好都改成 urllib 的调用。
    '''
    # 屏蔽warning信息
    requests.packages.urllib3.disable_warnings()    
    # 第一次请求是为了得到文件总大小
    r1 = requests.get(url, stream=True, verify=False)
    total_size = int(r1.headers['Content-Length'])
 
    # 这重要了，先看看本地文件下载了多少
    if os.path.exists(file_path):
        temp_size = os.path.getsize(file_path)  # 本地已经下载的文件大小
    else:
        temp_size = 0
    # 显示一下下载了多少
    print(temp_size)
    print(total_size)
    # 核心部分，这个是请求下载时，从本地文件已经下载过的后面下载
    headers = {'Range': 'bytes=%d-' % temp_size}
    # 重新请求网址，加入新的请求头的
    r = requests.get(url, stream=True, verify=False, headers=headers)
 
    # 下面写入文件也要注意，看到"ab"了吗？
    # "ab"表示追加形式写入文件
    with open(file_path, "ab") as f:
        #for chunk in progress.bar(r.iter_content(chunk_size = 2391975), expected_size=(total_size/1024) + 1):
        for chunk in r.iter_content(chunk_size=51200): #1024=1K, 51200=500K, 1048576=1M
            if chunk:
                temp_size += len(chunk)
                f.write(chunk)
                f.flush()
 
                ###这是下载实现进度显示####
                done = int(50 * temp_size / total_size)
                sys.stdout.write("\r[%s%s] %d%%" % ('█' * done, ' ' * (50 - done), 100 * temp_size / total_size))
                sys.stdout.flush()
    print()  # 避免上面\r 回车符

def downloadDirectory(url):
    '''下载指定互联网地址中的整个目录'''

    urls = soupURLs(url)
    # Notes: 跳过前面5个没有用的数据
    urls = urls[5:]

    for oneurl in urls:
        download(url, oneurl)


 
if __name__ == '__main__':
    args = parser()
    url = args['url']
    downfile = args['downfile']
    start = time()
    if downfile is None: # 下载整个网页中包含的websites
        downloadDirectory(url)
    else:
        download_url = '/'.join([url,downfile])
        download(download_url, downfile)
    
    print(f"下载用时: {time() - start}")
