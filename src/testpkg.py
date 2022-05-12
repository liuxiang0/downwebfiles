import argparse
import os
from bs4 import BeautifulSoup as soup
import urllib.request as urlreq
import re

def parserArgs():
    '''指定程序运行的参数设置'''
    # Construct an argument parser
    all_args = argparse.ArgumentParser()

    # Add arguments to the parser
    all_args.add_argument("-U", "--url", required=True,
    help="指定网址")
    all_args.add_argument("-F", "--downfile", required=True,
    help="指定下载文件")
    all_args.add_argument("-S", "--savefile", required=False,
    help="保留文件名（可选）")
    args = vars(all_args.parse_args())  # vars() is locals(), vars()
    #print("Args {1}, {2}, {0}".format(args['url'], args['downfile'], args['savefile']))
    return args  # Dict object

def getDatum(url):

    req = urlreq.Request(url,headers={'User-Agent': 'Mozilla/5.0'})
    client = urlreq.urlopen(req)
    datum = client.read().decode('utf-8') # 解码后的数据集
    client.close()
    return datum

def soupURLs(url):
    '''url: 给定的网络连接website
    return: 指定网站包含的超链接列表, 包含href=后面的地址tes.tar, 其它内容已经过滤掉了。
            <a href="tes.tar">tes.tar</a>
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
    return: 指定网站包含的 超链接列表, 每项形如 <a href="dev-clean.tar.gz">dev-clean.tar.gz</a>; 还需要继续提取网址（href=后面的内容）
    '''
    
    req = urlreq.Request(url,headers={'User-Agent': 'Mozilla/5.0'})
    client = urlreq.urlopen(req)
    datum = client.read().decode('utf-8') # 解码后的数据集
    client.close() 

    pagesoup = soup(datum, "html.parser").contents
    #soup()得到的结果类型 --type(pagesoup)-- 是 <class 'bs4.BeautifulSoup'>
    #soup(*).contents得到列表形式的内容List.

    #raw_text = str(pagesoup) 将列表信息变成字符串信息
    # 建立正则表达式(Regular Expression), 解析出 href 
    res = r"<a .*?href=.*?<\/a>"   
    return re.findall(res, str(pagesoup), re.I) 


from pathlib import Path
import requests

def url_retrieve(url: str, outfile: Path):
    R = requests.get(url, allow_redirects=True)
    if R.status_code != 200:
        raise ConnectionError('不能下载 {}\n 错误码: {}'.format(url, R.status_code))

    outfile.write_bytes(R.content)


import urllib.request
import urllib.error
import socket

def url_retrieve(
    url: str,
    outfile: Path,
    overwrite: bool = False,
):
    """
    Parameters
    ----------
    url: str
        URL to download from
    outfile: pathlib.Path
        output filepath (including name)
    overwrite: bool
        overwrite if file exists
    """
    outfile = Path(outfile).expanduser().resolve()
    if outfile.is_dir():
        raise ValueError("Please specify full filepath, including filename")
    # need .resolve() in case intermediate relative dir doesn't exist
    if overwrite or not outfile.is_file():
        outfile.parent.mkdir(parents=True, exist_ok=True)
        try:
            urllib.request.urlretrieve(url, str(outfile))
        except (socket.gaierror, urllib.error.URLError) as err:
            raise ConnectionError(
                "could not download {} due to {}".format(url, err)
            )

def testRe(raw_text):
    '''连续表格读取解析'''
    res_tr = r'<tr>(.*?)</tr>'
    msg_tr = re.findall(res_tr, raw_text, re.IGNORECASE) # re.S|re.M)
    print("1.<tr>")
    for tr in msg_tr:
        print(tr)

    print("2.<th>")
    res_th = r'<th>(.*?)</th>'
    msg_th = re.findall(res_th, raw_text, re.I) #re.S|re.M)
    for th in msg_th:
        print(th) # unicode utf-8

    print("3.<td>")
    res_td = r'<td>(.*?)</td>'
    msg_td = re.findall(res_td, raw_text, re.I) #re.S|re.M)
    for td in msg_td:
        print(td)

    print("4.<a href=>")
    res_href = r'<td><a href="(.*?)">' #</a></td
    msg_href = re.findall(res_href, raw_text, re.I) #re.S|re.M)
    for href in msg_href:
        print(href)

if __name__ == '__main__' :
    url = 'https://openslr.magicdatatech.com/resources/60/'
    data = getDatum(url)
    testRe(data)

    #urllist = soupURLs(url)
    
    #for a in urllist:
    #    print(a)


'''
#if req.status_code == 200:
        #1.获取网页源代码
#获取所有<a href></a>链接所有内容
print(u'\n获取完整链接内容:')
urls = re.findall(r"<a.*?href=.*?<\/a>", pagesoup, re.I|re.S|re.M)
for i in urls:
    print(i)
 
#获取<a href></a>中的URL
print(u'\n获取链接中URL:')
res_url = r"(?<=href=\").+?(?=\")|(?<=href=\').+?(?=\')"
link = re.findall(res_url ,  pagesoup, re.I|re.S|re.M)
for url in link:
    print(url)


    #2.正则表达式书写:
    #2.2注意:正则表达式默认匹配的是一行  我们的源代码是多行匹配的要加另一个参数 re.DOTALL
	#2.3正则法一:
		#re.findall() 返回的是lsit集合 一次过滤
    
        re.I(re.IGNORECASE): 忽略大小写（括号内是完整写法）
        re.M(re.MurlreqTILINE): 多行模式，改变'^'和'$'的行为
        re.S(re.DOTALL): 点任意匹配模式，改变'.'的行为

    re_res = re.findall(r'<tr class="province-box">(.*)<div class="wrap-right">', raw_text, re.DOTALL)
    	#re_res[0] 获取下标是的数据    二次过滤
    res=re.findall(r'title="(.*[院心部]）*)"',re_res[0])
    	#检查打印获取到的信息
	print(res)
	
	#2.4正则法二:
		#(优化)不用二次过滤 一次过滤就解决了

        #re_list = re.findall(r'<th><a href="/[^/].*/" target="_blank" title="(.*)">', pagesoup)

    # 写入文件中
    with open("上海医院名单", "w", encoding='utf-8') as read:
        for i in res:
            read.write(i)
            read.write("\n")
    
#else:
#    print("error")

itemlocator = pagesoup.findAll('div', {"class":"product-grid-item xs-100 sm-50 md-33 lg-25 xl-20"})

filename = "new items.csv"
f = open(filename, "w", encoding="utf-8")
headers = "Item Name, Price\n"
f.write(headers)

for items in itemlocator:   
    namecontainer = items.findAll("h4",{"class":"name"})
    names = namecontainer[0].text

    pricecontainer = items.findAll("p",{"class":"price"})
    prices = pricecontainer[0].text.strip()

    print("Item Name: "+ names)
    print("Price: " + prices)   

    f.write(names.replace(","," ") + "," + prices.replace(",", " ") + "\n")
f.write("Total number of items: " + "," + str(len(itemlocator)))
f.close()
'''
'''
anchors = soup.fetch('a')
len(anchors) 164 for a in anchors[:10]:



files = os.listdir(args['url'])
for file in files:
    print(file)
    '''