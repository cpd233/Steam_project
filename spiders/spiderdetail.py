import re
import time
from pymysql import *
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
import csv
import os
import json
from utils.query import queries


class spider(object):
    def __init__(self, spiderurl):
        self.spiderurl = spiderurl

    def startbrowser(self):
        service = Service('./chromedriver.exe')
        options = webdriver.ChromeOptions()
        options.add_experimental_option('debuggerAddress', 'localhost:9222')
        browser = webdriver.Chrome(service=service, options=options)
        browser.get(self.spiderurl)
        return browser

    def main(self, id):
        browser = self.startbrowser()
        print(f'详情页面{self.spiderurl}')
        browser.get(self.spiderurl)
        time.sleep(10)

        # 获取游戏标签
        types = []
        for type in browser.find_elements(by=By.XPATH, value='//div[@class="glance_tags popular_tags"]/a'):
            if type.text:
                types.append(type.text)

        # 获取游戏简介
        try:
            summary = browser.find_element(by=By.XPATH, value='//div[@class="game_description_snippet"]').text
        except:
            summary = "No description"
        # 近期评价
        recentComment = ''
        try:
            if re.search('mixed', browser.find_element(by=By.XPATH,
                                                       value='//*[@id="userReviews"]/div[1]/div[2]/span[1]').get_attribute(
                'class')):
                recentComment = 'mid'
            else:
                recentComment = 'good'
        except:
            recentComment = 'None'

        # 所有评价
        allComments = ''
        try:
            if re.search('mixed', browser.find_element(by=By.XPATH,
                                                       value='//*[@id="userReviews"]/div[2]/div[2]/span[1]').get_attribute(
                'class')):
                allComments = 'mid'
            else:
                allComments = 'good'
        except:
            allComments = 'None'
        # 开发商
        firm = browser.find_elements(by=By.XPATH, value='//div[@class="summary column"]/a')[0].text
        # 发行商
        try:
            publisher = browser.find_elements(by=By.XPATH, value='//div[@class="summary column"]/a')[1].text
        except:
            publisher = 'None'
        # 图片列表
        imglist = [x.get_attribute('src') for x in browser.find_elements(by=By.XPATH,
                                                                         value='//div[@class="highlight_strip_item highlight_strip_screenshot"]/img')]
        # 预览视频
        try:
            video = browser.find_element(by=By.XPATH, value='//video').get_attribute('src')
        except:
            video = ''
        queries('UPDATE games SET types = %s,'
                ' summary = %s,'
                ' recentComment = %s,'
                ' allComments = %s,'
                ' firm = %s,'
                ' publisher = %s,'
                ' imglist = %s,'
                ' video = %s '
                'WHERE id = %s ',
                [json.dumps(types), summary, recentComment, allComments, firm, publisher, json.dumps(imglist), video,
                 id])


if __name__ == '__main__':
    game_list = queries('select * from games', [], 'select')
    for i in game_list[104:]:
        spider0bj = spider(i[-1])
        spider0bj.main(i[0])
