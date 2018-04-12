# -*- coding:utf-8 -*-
import os
import re
import urllib
import json
import socket
import urllib.request
import urllib.parse
import urllib.error
import os
import os.path as osp
# 设置超时
import time

timeout = 1
socket.setdefaulttimeout(timeout)

classNames = ['狗','手机','猫','杯子','花','书桌','人',\
'电视机','电脑','钱包','笔记本','眼镜','鼠标','汽车','自行车',\
'火车','椅子','餐桌','沙发','鸟']

# 人 => 人街拍

trainRoot = './train/'
testRoot = './test/'

if not os.path.exists(trainRoot):
    os.mkdir(trainRoot)

if not os.path.exists(testRoot):
    os.mkdir(testRoot)

class Crawler:
    # 睡眠时长
    __time_sleep = 0.1
    __amount = 0
    __start_amount = 0
    __counter = 0
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:23.0) Gecko/20100101 Firefox/23.0'}

    # 获取图片url内容等
    # t 下载图片时间间隔
    def __init__(self, t=0.1):
        self.time_sleep = t

    # 获取后缀名
    def get_suffix(self, name):
        m = re.search(r'\.[^\.]*$', name)
        if m.group(0) and len(m.group(0)) <= 5:
            return m.group(0)
        else:
            return '.jpeg'

    # 获取referrer，用于生成referrer
    def get_referrer(self, url):
        par = urllib.parse.urlparse(url)
        if par.scheme:
            return par.scheme + '://' + par.netloc
        else:
            return par.netloc

        # 保存图片
    def save_image(self, rsp_data, word, trainOrtest='train'):
        if trainOrtest=='train':
            root = trainRoot
        else:
            root = testRoot
        if not os.path.exists(root + word):
            os.mkdir(root + word)
        # 判断名字是否重复，获取图片长度
        self.__counter = len(os.listdir(root + word)) + 1
        for image_info in rsp_data['imgs']:

            try:
                time.sleep(self.time_sleep)
                suffix = self.get_suffix(image_info['objURL'])
                # 指定UA和referrer，减少403
                refer = self.get_referrer(image_info['objURL'])
                opener = urllib.request.build_opener()
                opener.addheaders = [
                    ('User-agent', 'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:55.0) Gecko/20100101 Firefox/55.0'),
                    ('Referer', refer)
                ]
                urllib.request.install_opener(opener)
                # 保存图片
                urllib.request.urlretrieve(image_info['objURL'], root + word + '/' + str(self.__counter) + str(suffix))
            except urllib.error.HTTPError as urllib_err:
                print(urllib_err)
                continue
            except Exception as err:
                time.sleep(1)
                print(err)
                print("产生未知错误，放弃保存")
                continue
            else:
                print(word+" 图+1,已有" + str(self.__counter) + "张 "+word+" 图")
                self.__counter += 1
        return

    # 开始获取
    def get_images(self, word='美女', trainOrtest='train'):
        search = urllib.parse.quote(word)
        # pn int 图片数
        pn = self.__start_amount
        while pn < self.__amount:

            url = 'http://image.baidu.com/search/avatarjson?tn=resultjsonavatarnew&ie=utf-8&word=' + search + '&cg=girl&pn=' + str(
                pn) + '&rn=60&itg=0&z=0&fr=&width=&height=&lm=-1&ic=0&s=0&st=-1&gsm=1e0000001e'
            # 设置header防ban
            try:
                time.sleep(self.time_sleep)
                req = urllib.request.Request(url=url, headers=self.headers)
                page = urllib.request.urlopen(req)
                rsp = page.read().decode('unicode_escape')
            except UnicodeDecodeError as e:
                print(e)
                print('-----UnicodeDecodeErrorurl:', url)
            except urllib.error.URLError as e:
                print(e)
                print("-----urlErrorurl:", url)
            except socket.timeout as e:
                print(e)
                print("-----socket timout:", url)
            else:
                # 解析json
                rsp_data = json.loads(rsp)
                self.save_image(rsp_data, word, trainOrtest=trainOrtest)
                # 读取下一页
                print("下载下一页")
                pn += 60
            finally:
                page.close()
        print("下载任务结束")
        return

    def start(self, word, spider_page_num=1, start_page=1, trainOrtest='train'):
        """
        爬虫入口
        :param word: 抓取的关键词
        :param spider_page_num: 需要抓取数据页数 总抓取图片数量为 页数x60
        :param start_page:起始页数
        :return:
        """
        self.__start_amount = (start_page - 1) * 60
        self.__amount = spider_page_num * 60 + self.__start_amount
        self.get_images(word, trainOrtest=trainOrtest)


if __name__ == '__main__':
    crawler = Crawler(0.05)  # 抓取延迟为 0.05
    # get train img
    for clsname in classNames:
        print("train set of "+clsname+" is geted...")
        crawler.start(clsname, 10, 1,trainOrtest='train')
    # get test img
    for clsname in classNames:
        print("test set of "+clsname+" is geted...")
        crawler.start(clsname, 10, 1,trainOrtest='test')