# coding=utf-8
from postboy2 import PostBoy

if __name__ == '__main__':
    result = PostBoy('www.douban.com','utf-8').get()
    print((result['data']['title']))
