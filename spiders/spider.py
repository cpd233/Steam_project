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


# https://store.steampowered.com/search/?specials=1&page=%s

def init():
    try:
        conn = connect(host='localhost', user='root', password='123456', database='steamdata', port=3306,
                       charset='utf8mb4')

        # create a table
        sql = '''
            CREATE TABLE games (
                    id INT PRIMARY KEY AUTO_INCREMENT,
                    title VARCHAR(255),
                    icon VARCHAR(2555),
                    time VARCHAR(255),
                    compatible VARCHAR(255),
                    evaluate VARCHAR(2555),
                    discount VARCHAR(255),
                    original_price VARCHAR(255),
                    current_price VARCHAR(255),
                    types VARCHAR(2555),
                    summary TEXT,
                    recentComment VARCHAR(255),
                    allComments VARCHAR(255),
                    firm VARCHAR(255),
                    publisher VARCHAR(255),
                    imglist TEXT,
                    video TEXT,
                    detaillink VARCHAR(2555)
                    )
        '''
        cusor = conn.cursor()
        cusor.execute(sql)
        conn.commit()
    except:
        pass
    if not os.path.exists('temp1.csv'):
        # Open the file in write mode to create it and write the header
        with open('temp1.csv', 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['title', 'icon', 'time', 'compatible', 'evaluate', 'discount',
                             'original_price', 'current_price', 'detaillink'])
    print("CSV file created and header written.")


def save_to_csv(rowdata):
    with open('temp1.csv', 'a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(rowdata)
        print("存储")


def save_to_sql():
    with open('temp1.csv', 'r', newline='', encoding='utf-8') as r_f:
        reader = csv.reader(r_f)
        for i in reader:
            if i[0] == 'title':
                continue
            queries('''
                insert into games(title, icon, time, compatible, evaluate, discount, original_price, current_price,
                             detaillink)
                values (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            ''', [i[0], i[1], i[2], i[3], i[4], i[5], i[6], i[7], i[8]])


# def spider(spiderTarget, startpage):
#     print('页面' + spiderTarget % startpage)
#     browser = startbrowser()
#     browser.get(spiderTarget % startpage)
#     time.sleep(10)
#
#     scroll_position = 0
#     scroll_amount = 200
#     max_scroll_amount = 2000
#     while scroll_position < max_scroll_amount:
#         scroll_script = f"window.scrollBy(0,{scroll_amount})"
#         browser.execute_script(scroll_script)
#         scroll_position += scroll_amount
#         time.sleep(2)
#
#     game_list = browser.find_elements(by=By.XPATH,
#                                       value="//a[@class='search_result_row ds_collapse_flag  app_impression_tracked']")
#
#     for game in game_list:
#         try:
#             title = game.find_element(by=By.XPATH,
#                                       value="./div[@class='responsive_search_name_combined']/div[1]/span[@class='title']").text
#             icon = game.find_element(by=By.XPATH,
#                                      value="./div[@class='col search_capsule']/img").get_attribute("src")
#             compatiblelist = game.find_elements(by=By.XPATH,
#                                                 value="./div[@class='responsive_search_name_combined']/div[1]/div/span")
#             compatible = []
#             for i in compatiblelist:
#                 if re.search('win', i.get_attribute("class")):
#                     compatible.append(re.search('win', i.get_attribute("class")).group())
#                 elif re.search('mac', i.get_attribute("class")):
#                     compatible.append(re.search('mac', i.get_attribute("class")).group())
#                 elif re.search('linux', i.get_attribute("class")):
#                     compatible.append(re.search('linux', i.get_attribute("class")).group())
#             # try:
#             #     times = game.find_element(by=By.XPATH,
#             #                               value="./div[@class='responsive_search_name_combined']/div[2]").text
#             # except:
#             #     times = "Unknown"
#
#             # 尝试获取发布时间
#             times_element = game.find_elements(By.XPATH, "./div[@class='responsive_search_name_combined']/div[2]")
#             times = times_element[0].text if times_element else "Unknown"
#
#             # evaluate = ''
#             # if re.search('mixed', game.find_element(by=By.XPATH,
#             #                                         value="./div[@class='responsive_search_name_combined']/div[3]/span").get_attribute(
#             #     'class')):
#             #     evaluate = 'mid'
#             # else:
#             #     evaluate = 'good'
#             # try:
#             #     discount = 100 - int(
#             #         re.search(r'\d+',
#             #                   game.find_element(by=By.XPATH, value=".//div[@class='discount_pct']").text).group()
#             #     )
#             # except:
#             #     discount = 0
#             #
#             # try:
#             #     original_price = re.search(r'\d+(\.\d+)?', game.find_element(by=By.XPATH,
#             #                                                              value=".//div[@class='discount_original_price']").text).group()
#             # except:
#             #     original_price = 'Null'
#             #
#             # try:
#             #     current_price = re.search(r'\d+(\.\d+)?', game.find_element(by=By.XPATH,
#             #                                                             value=".//div[@class='discount_final_price']").text).group()
#             # except:
#             #     current_price = 'Null'
#             # 评价信息
#             evaluate_element = game.find_elements(By.XPATH,
#                                                   "./div[@class='responsive_search_name_combined']/div[3]/span")
#             evaluate = "mid" if (evaluate_element and "mixed" in evaluate_element[0].get_attribute('class')) else "good"
#
#             # 尝试获取打折信息
#             discount_element = game.find_elements(By.XPATH, ".//div[@class='discount_pct']")
#             discount = 100 - int(re.search(r'\d+', discount_element[0].text).group()) if discount_element else 0
#
#             # 尝试获取原价
#             original_price_element = game.find_elements(By.XPATH, ".//div[@class='discount_original_price']")
#             original_price = re.search(r'\d+(\.\d+)?',
#                                        original_price_element[0].text).group() if original_price_element else "Null"
#
#             # 尝试获取现价
#             current_price_element = game.find_elements(By.XPATH, ".//div[@class='discount_final_price']")
#             current_price = re.search(r'\d+(\.\d+)?',
#                                       current_price_element[0].text).group() if current_price_element else "Null"
#
#             detaillink = game.get_attribute("href")
#             print(detaillink)
#             save_to_csv([title, icon, times, json.dumps(compatible), evaluate, discount, original_price, current_price,
#                          detaillink])
#         except Exception as e:
#             print(f'Failed:{e}')
def spider(spiderTarget, startpage):
    print('页面' + spiderTarget % startpage)
    browser = startbrowser()
    browser.get(spiderTarget % startpage)
    time.sleep(15)

    scroll_position = 0
    scroll_amount = 200
    max_scroll_amount = 2000
    while scroll_position < max_scroll_amount:
        scroll_script = f"window.scrollBy(0,{scroll_amount})"
        browser.execute_script(scroll_script)
        scroll_position += scroll_amount
        time.sleep(2)

    game_list = browser.find_elements(By.XPATH, "//a[@class='search_result_row ds_collapse_flag  app_impression_tracked']")

    for game in game_list:
        try:
            title = game.find_element(By.XPATH, "./div[@class='responsive_search_name_combined']/div[1]/span[@class='title']").text
            icon = game.find_element(By.XPATH, "./div[@class='col search_capsule']/img").get_attribute("src")

            # 兼容性信息
            compatiblelist = game.find_elements(By.XPATH, "./div[@class='responsive_search_name_combined']/div[1]/div/span")
            compatible = []
            for i in compatiblelist:
                class_attr = i.get_attribute("class")
                if "win" in class_attr:
                    compatible.append("win")
                elif "mac" in class_attr:
                    compatible.append("mac")
                elif "linux" in class_attr:
                    compatible.append("linux")

            # 发布时间
            times_element = game.find_elements(By.XPATH, "./div[@class='responsive_search_name_combined']/div[2]")
            times = times_element[0].text if times_element else "Unknown"

            # 评价信息
            evaluate_element = game.find_elements(By.XPATH, "./div[@class='responsive_search_name_combined']/div[3]/span")
            evaluate = "mid" if (evaluate_element and "mixed" in evaluate_element[0].get_attribute('class')) else "good"

            # 折扣信息
            discount_element = game.find_elements(By.XPATH, ".//div[@class='discount_pct']")
            discount = 100 - int(re.search(r'\d+', discount_element[0].text).group()) if discount_element else 0

            # 原价信息
            original_price_element = game.find_elements(By.XPATH, ".//div[@class='discount_original_price']")
            original_price = re.search(r'\d+(\.\d+)?', original_price_element[0].text).group() if original_price_element else "Null"

            # 现价信息
            current_price_element = game.find_elements(By.XPATH, ".//div[@class='discount_final_price']")
            current_price = re.search(r'\d+(\.\d+)?', current_price_element[0].text).group() if current_price_element else "Null"

            # 详情页链接
            detaillink = game.get_attribute("href")

            print(detaillink)
            save_to_csv([title, icon, times, json.dumps(compatible), evaluate, discount, original_price, current_price, detaillink])

        except Exception as e:
            print(f'Failed:{e}')


def startbrowser():
    service = Service('./chromedriver.exe')
    options = webdriver.ChromeOptions()
    options.add_experimental_option('debuggerAddress', 'localhost:9222')
    browser = webdriver.Chrome(service=service, options=options)
    return browser


def main(spiderTarget):
    # init()
    for i in range(1, 10):
        spider(spiderTarget, i)
    save_to_sql()


if __name__ == '__main__':
    # startbrowser()
    # init()
    spiderTarget = 'https://store.steampowered.com/search/?specials=1&page=%s'
    main(spiderTarget)
