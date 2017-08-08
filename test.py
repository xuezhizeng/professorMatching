# coding:utf-8
import time
from selenium.common.exceptions import TimeoutException
from bs4 import BeautifulSoup
from selenium import webdriver
from wait import WebDriverWait
import math
import threadpool
import Queue
import re
import os

import sys

temp = {}
tempSet = set()
# global pageUrlQueue
# pageUrlQueue = Queue.Queue()
#
#
# def getIeeeName(num):
#     browser = webdriver.Firefox()  # 初始化Firefox浏览器
#     filename = '%d%s' % (num, 'ieeeTemp.txt')
#     f = open(filename, 'a')
#     while not pageUrlQueue.empty():
#         author = pageUrlQueue.get()
#         keywordSet = set()
#         papers = author.split('!!!')[1].split('*@*')
#         for paper in papers:
#             url = '%s%s' % ('http://ieeexplore.ieee.org/search/searchresult.jsp?queryText=', paper)
#             browser.get(url)  # 调用get方法抓取
#             # # # 等待网页加载完
#             WebDriverWait(browser, 120, 0.5).until(
#                 lambda browser: browser.find_element_by_class_name('c-Pagination-nodes'))
#             # 解析html
#             soup = BeautifulSoup(browser.page_source, 'html.parser', from_encoding='utf-8')
#             links = soup.find_all('a', href=re.compile(r"document"))
#             tempSet = set()
#             for link in links:
#                 if len(link['href']) == 18:
#                     docUrl = '%s%s%s' % ('http://ieeexplore.ieee.org', link['href'], 'authors?ctx=authors')
#                     try:
#                         browser.get(docUrl)  # 调用get方法抓取
#                     except TimeoutException, e:
#                         browser.refresh()
#                     # # # 等待网页加载完
#                     WebDriverWait(browser, 120, 0.5).until(
#                         lambda browser: browser.find_element_by_class_name('document-ft-section-header'))
#                     time.sleep(1)
#                     # 解析html
#                     soup = BeautifulSoup(browser.page_source, 'html.parser', from_encoding='utf-8')
#                     lists = soup.find_all('li', class_="doc-all-keywords-list-item ng-scope")
#                     for list in lists:
#                         if list.find('strong').get_text() == 'Author Keywords ':
#                             keylinks = list.find_all('a')
#                             for keylink in keylinks:
#                                 keywordSet.add(keylink.get_text())
#
#                     if keywordSet is None:
#                         for list in lists:
#                             if list.find('strong').get_text() == 'IEEE Keywords':
#                                 keylinks = list.find_all('a')
#                                 for keylink in keylinks:
#                                     keywordSet.add(keylink.get_text())
#                     break
#
#         keywords = []
#         for keyword in keywordSet:
#             keywords.append(keyword)
#         print '%s%s%s%s%s' % (author.split('!!!')[0], '|',  ','.join(keywords), '!!!', author.split('!!!')[1].strip())
#         f.write('%s%s%s%s%s' % (author.split('!!!')[0], '|',  ','.join(keywords), '!!!', author.split('!!!')[1]))
#     browser.quit()
#
#
# reload(sys)
# sys.setdefaultencoding('utf-8')
# # sys.setdefaultencoding('gbk')
# pool = threadpool.ThreadPool(10)
# num = range(0, 10)
# pageUrls = open("allIeeeNum.txt").readlines()
# for page in pageUrls:
#     pageUrlQueue.put(page)
# requests = threadpool.makeRequests(getIeeeName, num)
# [pool.putRequest(req) for req in requests]
# pool.wait()

# tempSet = set()
# num = range(0,10)
# for i in num:
#     filename = '%d%s' % (i, 'ieeeTemp.txt')
#     f = open(filename, 'r')
#     lines = f.readlines()
#     for line in lines:
#         tempSet.add(line)
#     f.close()
#
# f = open('newIeeeNum.txt', 'w')
# for i in tempSet:
#     f.write(i)
# f.close()

# f = open('newIeeeNum.txt', 'r')
# lines = f.readlines()
# for line in lines:
#     temp[line.split('|')[0]] = line
#     # print line.strip()
# f.close()
#
# f = open('allInfo.txt', 'r')
# lines = f.readlines()
# for line in lines:
#     if temp.has_key(line.split('|')[0]):
#         temp[line.split('|')[0]] = '%s%s%s' % (line.strip(), '|', temp[line.split('|')[0]].split('|')[3])
# f.close()
#
# f = open('trueInfo.txt', 'w')
# for i in temp:
#     f.write(temp[i])
# f.close()

# num = range(0, 8)
# for i in num:
#     filename = '%s%s' % (i, 'details.txt')
#     f = open(filename, 'r')
#     lines = f.readlines()
#     for line in lines:
#         tempSet.add(line)
#     f.close()
#
# f = open('result4.txt', 'w')
# for i in tempSet:
#     f.write(i)
# f.close()

