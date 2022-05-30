'''Download large files from web in python
1. To download large file, use urllib.request.urlopen() to download a file like object, and then save it to local file with shutil.copyfileobj. This will avoid reading the whole thing into memory at once.

import urllib.request
import shutil
with urllib.request.urlopen('https://www.example.com/big.txt') as response:
    with open('local_big.txt', 'wb') as local_file:
        shutil.copyfileobj(response, local_file)

2. The requests library also support to download big files, set stream=True in the request. This streams the file to disk without using excessive memory with shutil.copyfileobj.

import requests
import shutil

with requests.get('https://www.example.com/big.txt', stream=True) as response:
    if response.status_code == 200:
        with open('local_big.txt', 'wb') as local_file:
            shutil.copyfileobj(response.raw, local_file)

3. Use requests library in streaming code, you can read the large file chunk by chunk. Also need set stream=True in the request.

import requests
with requests.get('https://www.example.com/big.txt', stream=True) as response:
    with open('local_big.txt', "wb") as local_file:    
        for chunk in response.iter_content(chunk_size=1024): 
            if chunk:   
                local_file.write(chunk)

                
The HTTP response content (r.content) is nothing but a string which is storing the file data. So, it won’t be possible to save all the data in a single string in case of large files. To overcome this problem, we do some changes to our program:

Since all file data can’t be stored by a single string, we use r.iter_content method to load data in chunks, specifying the chunk size.
 r = requests.get(URL, stream = True)
Setting stream parameter to True will cause the download of response headers only and the connection remains open. This avoids reading the content all at once into memory for large responses. A fixed chunk will be loaded each time while r.iter_content is iterated.

Here is an example:'''

import requests
from  parsers import parser_one, spend
from time import time, localtime
import os,sys

SMALLFILE = 512000

args = parser_one()
file = args['downfile'] 
url = file
savedfile = file.split('/')[-1]

start = time()

# 屏蔽warning信息
requests.packages.urllib3.disable_warnings()
# 第一次请求是为了得到文件总大小
r1 = requests.get(url, stream=True, verify=False)
total_size = int(r1.headers['Content-Length'])

if os.path.exists(savedfile):
    temp_size = os.path.getsize(savedfile)  # 本地已经下载的文件大小
else:
    temp_size = 0
# 显示一下下载了多少, 共有多少
print("已下载了{0}，共有{1} !".format(temp_size, total_size))
# 核心部分，请求下载时，从本地文件已经下载过的后面下载，断点续传开始...
headers = {'Range': 'bytes=%d-' % temp_size}
# 重新请求网址，加入新的请求头
r = requests.get(url, stream=True, verify=False, headers=headers)

# 写入文件要注意:"ab"表示追加形式写入文件
with open(savedfile, "ab") as f:
    #for chunk in progress.bar(r.iter_content(chunk_size = 2391975), expected_size=(total_size/1024) + 1):
    for chunk in r.iter_content(chunk_size=SMALLFILE): #512000=500K, 1048576=1M
        if chunk:
            temp_size += len(chunk)
            f.write(chunk)
            f.flush()

            #这是下载实现进度显示
            done = int(50 * temp_size / total_size)
            sys.stdout.write("\r[%s%s] %d%%" % ('█' * done, ' ' * (50 - done), 100 * temp_size / total_size))
            sys.stdout.flush()
print()  # 避免上面\r 回车符

print(r"下载用时: {0}".format(spend(time() - start)))
print(r"结束时间：{}".format(localtime()))
