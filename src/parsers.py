import argparse
from user_agents import parse
from random import choice

def parser():
    # Construct an argument parser
    all_args = argparse.ArgumentParser(description='下载大文件，支持断点续传，仅供参考！')

    # Add arguments to the parser
    all_args.add_argument("-U", "--url", required=True,
    help="web网址")
    all_args.add_argument("-F", "--downfile", required=False,
    help="文件名(可选项)")
    #all_args.add_argument("-S", "--savefile", required=False,
    #help="保存的本地文件名(可选)，缺省为原文件名")
    args = vars(all_args.parse_args())  # to Dict
    return args

def parser_one():
    # Construct an argument parser
    all_args = argparse.ArgumentParser(description='下载大文件，支持断点续传，仅供参考！')

    # Add arguments to the parser
    #all_args.add_argument("-U", "--url", required=True, help="web网址")
    all_args.add_argument("-F", "--downfile", required=True, help="Web文件名")
    #all_args.add_argument("-S", "--savefile", required=False,
    #help="保存的本地文件名(可选)，缺省为原文件名")
    args = vars(all_args.parse_args())  # to Dict
    return args

def getUA():
    user_agents = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:91.0) Gecko/20100101 Firefox/91.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:78.0) Gecko/20100101 Firefox/78.0",
    "Mozilla/5.0 (X11; Linux x86_64; Win64; x64; rv:95.0) Gecko/20100101 Firefox/95.0"
    ]
    return {'User-Agent': str(parse(choice(user_agents)))}

def spend(secs):
    '''given: seconds from time.time()-start
    return: xx 小时 xx 分 xx 秒！'''

    seconds = round(secs)
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    seconds = (seconds % 3600) % 60
    return "{0}小时 {1}分 {2}秒".format(hours,minutes,seconds)
