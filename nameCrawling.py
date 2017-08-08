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

global pageUrlQueue
pageUrlQueue = Queue.Queue()
global pageUrlRQueue
pageUrlRQueue = Queue.Queue()
global docUrlQueue
docUrlQueue = Queue.Queue()
global nameQueue
nameQueue = Queue.Queue()

keywords = ['cyber physical system',
            'crowd computing',
            'crowd sensing',
            'mobile application',
            'crowd sourcing',
            'social network',
            'service computing',
            'cloud computing']
startYear = 2007
endYear = 2017
rangeYear = '%s%d%s%d%s' % ('&ranges=', startYear, '_', endYear, '_Year')

class NameCrawling():
    # 获取该主题搜索出来的页数
    def getIeeePages(self, keyword):
        browser = webdriver.Firefox()  # 初始化Firefox浏览器
        browser.get(pageUrlQueue.get())  # 调用get方法抓取
        # # # 等待网页加载完
        WebDriverWait(browser, 120, 0.5).until(lambda browser: browser.find_element_by_class_name('c-Pagination-nodes'))
        # 解析html
        soup = BeautifulSoup(browser.page_source, 'html.parser', from_encoding='utf-8')

        links = soup.find('div', class_="Dashboard-section").find('span')
        totalRecords = links.get_text().split('of')[1]

        print totalRecords
        pages = int(math.ceil(float(totalRecords.replace(',', '').strip()) / 25))
        # 实在太多了取前100页,也就是2500个
        pages = min(pages, 100)
        for i in range(1, pages):
            url = '%s%s%s%s%d%s%s' % (
                'http://ieeexplore.ieee.org/search/searchresult.jsp?', 'queryText=', keyword, '&pageNumber=', i,
                rangeYear, '\n')
            pageUrlRQueue.put(url)

        browser.quit()

    #将IeeePages保持到ieeePages.txt中
    def pageWrite(selg, filename):
        with open(filename, "w") as f:
            while not pageUrlRQueue.empty():
                f.write(pageUrlRQueue.get())

    #收集每一页的文档链接
    def getIeeeDocuments(self, url):
        browser = webdriver.Firefox()  # 初始化Firefox浏览器
        while not pageUrlQueue.empty():
            browser.get(pageUrlQueue.get())  # 调用get方法抓取
            # # # 等待网页加载完
            if WebDriverWait(browser, 60, 0.5).until(
                lambda browser: browser.find_element_by_class_name('c-Pagination-nodes')) == 'WrongPage':
                continue
            # 向下滑动获取完整页面
            for i in range(1, 5):
                browser.execute_script("window.scrollBy(0,3000)")
                time.sleep(1)

            # 解析html
            soup = BeautifulSoup(browser.page_source, 'html.parser', from_encoding='utf-8')

            links = soup.find_all('a', href=re.compile(r"document"))
            tempSet = set()
            for link in links:
                if len(link['href']) == 18:
                    tempSet.add(link['href'])
            for temp in tempSet:
                docUrl = '%s%s%s' % ('http://ieeexplore.ieee.org', temp, 'authors?ctx=authors')
                docUrlQueue.put(docUrl)
        browser.quit()

    #将搜索到的document保持到ieeeDocs.txt中
    def docWrite(selg, filename):
        with open(filename, "w") as f:
            tempSet = set()
            while not docUrlQueue.empty():
                tempSet.add(docUrlQueue.get())
            for t in tempSet:
                f.write('%s%s' % (t, '\n'))

    # 通过document页面将中国学者都找出来
    def getIeeeName(self, num):
        browser = webdriver.Firefox()  # 初始化Firefox浏览器
        filename = '%d%s' % (num, 'ieeeTemp.txt')
        f = open(filename, 'a')
        while not pageUrlQueue.empty():
            url = pageUrlQueue.get()
            try:
                browser.get(url)  # 调用get方法抓取
            except TimeoutException, e:
                browser.refresh()
            # # # 等待网页加载完
            WebDriverWait(browser, 120, 0.5).until(lambda browser: browser.find_element_by_class_name('document-ft-section-header'))
            time.sleep(1)
            # 解析html
            soup = BeautifulSoup(browser.page_source, 'html.parser', from_encoding='utf-8')
            docName = soup.find('h1', class_="document-title").find('span').get_text()

            #爬领域关键字
            lists = soup.find_all('li', class_="doc-all-keywords-list-item ng-scope")
            for list in lists:
                if list.find('strong').get_text() == 'Author Keywords ':
                    keylinks = list.find_all('a')
                    for keylink in keylinks:
                        keywordSet.add(keylink.get_text())
            break
            keywords = []
            for keyword in keywordSet:
                keywords.append(keyword)

            authors = soup.find('section', class_="document-all-authors ng-scope").find_all('div', class_='pure-u-18-24')
            for author in authors:
                area = author.find('div', class_='ng-binding').get_text()
                if 'China' in area:
                    name = author.find('span', class_='ng-binding').get_text().strip()
                    areas = re.split("[,.:()]", area)
                    university = 'None'
                    for a in areas:
                        if 'university' in a or 'University' in a:
                            university = a.strip()
                            break
                    try:
                        f.write(url)
                        f.write('%s%s%s%s%s%s%s' % (name, '|', university, ','.join(keywords), '!!!', docName, '\n'))
                    except UnicodeDecodeError, e :
                        print name
                        print university
                        print docName
        browser.quit()

    # 将中国学者保持到ieeeName.txt中
    def nameWrite(self, filename):
        with open(filename, "w") as f:
            tempDic = {}
            while not nameQueue.empty():
                l = nameQueue.get().split('!!!')
                if not tempDic.has_key(l[0]):
                    tempDic[l[0]] = l[1]
                else:
                    tempDic[l[0]] += '%s%s' % ('*@*', l[1])
            for dic in tempDic:
                f.write('%s%s%s%s' % (dic, '!!!', tempDic[dic], '\n'))

    def getAllNames(self, filename):
        files = os.listdir('./names/')
        tempDic = {}
        for file in files:
            if '.txt' in file:
                nameAll = open('%s%s' % ("names/", file)).readlines()
                for nameA in nameAll:
                    names = nameA.split('!!!')
                    if not tempDic.has_key(names[0]):
                        tempDic[names[0]] = names[1]
                    else:
                        tempDic[names[0]] += '%s%s' % (',', names[1])
        with open(filename, "w") as f:
            for dic in tempDic:
                f.write('%s%s%s' % (dic, '!!!', tempDic[dic]))

    def getACMPages(self, keyword):
        browser = webdriver.Firefox()  # 初始化Firefox浏览器
        browser.get(pageUrlQueue.get())  # 调用get方法抓取
        # # # 等待网页加载完
        WebDriverWait(browser, 120, 0.5).until(lambda browser: browser.find_element_by_id('searchtots'))
        # 解析html
        soup = BeautifulSoup(browser.page_source, 'html.parser', from_encoding='utf-8')

        totalRecords = soup.find('div', id="searchtots").find('strong').get_text()
        totalRecords = int(totalRecords.replace(',', ''))

        # 实在太多了取前100页,也就是2000个
        pages = min(totalRecords, 100 * 20)
        for i in range(0, pages, 20):
            url = '%s%s%s%d%s' % ('http://dl.acm.org/results.cfm?query=', keyword, '&srt=_score&start=', i, '\n')
            pageUrlRQueue.put(url)

        browser.quit()

    def getACMAuthors(self, url):
        browser = webdriver.Firefox()  # 初始化Firefox浏览器
        tempSet = set()
        while not pageUrlQueue.empty():
            try:
                browser.get(pageUrlQueue.get())  # 调用get方法抓取
            except TimeoutException, e:
                browser.refresh()
            # # # 等待网页加载完
            if WebDriverWait(browser, 60, 0.5).until(
                lambda browser: browser.find_element_by_class_name('authors')) == 'WrongPage':
                continue

            # 解析html
            soup = BeautifulSoup(browser.page_source, 'html.parser', from_encoding='utf-8')

            authors = soup.find_all('div', class_='authors')
            for author in authors:
                links = author.find_all('a')
                for link in links:
                    tempSet.add(link['href'].split('&')[0])

        for temp in tempSet:
            docUrl = '%s%s' % ('http://dl.acm.org/', temp)
            docUrlQueue.put(docUrl)
        browser.quit()

    def getACMName(self, url):
        browser = webdriver.Firefox()  # 初始化Firefox浏览器
        filename = url + 'acmTemp.txt'
        f = open(filename, 'a')
        while not pageUrlQueue.empty():
            try:
                browser.get(pageUrlQueue.get())  # 调用get方法抓取
            except TimeoutException, e:
                browser.refresh()
            # # # 等待网页加载完
            if WebDriverWait(browser, 120, 0.5).until(
                lambda browser: browser.find_element_by_class_name('title')) == 'WrongPage':
                print "WrongPage"
            # 解析html
            soup = BeautifulSoup(browser.page_source, 'html.parser', from_encoding='utf-8')

            authorName = soup.find('span', class_="small-text").find('strong').get_text()

            universitySet = soup.find_all('td', class_="small-text")[1].find_all('a')
            universityT = None
            # for u in universitySet:
            #     if u.get_text() in universityEnglish:
            #         universityT = u.get_text()

            if not universityT:
                continue

            titles = soup.find_all('div', class_="title")
            docs = []
            for title in titles:
                titlelink = title.find('a').get_text()
                docs.append(titlelink)
            docS = '*@*'.join(docs)
            authorName = ' '.join(authorName.split())
            # nameQueue.put('%s%s%s%s%s' % (authorName, '|', universityT, '!!!', docS))

            f.write('%s%s%s%s%s' % (authorName, '|', universityT, '!!!', docS))

        browser.quit()

    def acmWrite(selg, filename):
        with open(filename, "w") as f:
            tempSet = {}
            while not nameQueue.empty():
                nameq = nameQueue.get().split('!!!')
                if not tempSet.has_key(nameq[0]):
                    tempSet[nameq[0]] = nameq[1]
            for t in tempSet:
                f.write('%s%s%s%s' % (t, '!!!', tempSet[t], '\n'))

    def getElsDocs(self, keyword):
        browser = webdriver.Firefox()  # 初始化Firefox浏览器
        browser.get(pageUrlQueue.get())  # 调用get方法抓取
        # # # 等待网页加载完
        WebDriverWait(browser, 120, 0.5).until(lambda browser: browser.find_element_by_class_name('search-result-meta'))
        # 解析html
        soup = BeautifulSoup(browser.page_source, 'html.parser', from_encoding='utf-8')

        items = soup.find_all('div', class_=re.compile(r'search-result-body'))

        for item in items:
            if item.find('span', class_='category').get_text() == 'Journals':
                pageUrlRQueue.put(item.find('a')['href'])

        # 实在太多了取前100页,也就是2000个
        culPage = int(soup.find('div', id='pagination-wrapper').find('li', class_='selected').find('span').get_text())
        if culPage < 200:
            browser.find_element_by_class_name('btn-right-arrow btn-tertiary').click()

        browser.quit()

    def getElsName(self, url):
        browser = webdriver.Firefox()  # 初始化Firefox浏览器
        while not pageUrlQueue.empty():
            url = pageUrlQueue.get()
            try:
                browser.get(url)  # 调用get方法抓取
            except TimeoutException, e:
                browser.refresh()
            if 'books' in url:
                if WebDriverWait(browser, 120, 0.5).until(
                        lambda browser: browser.find_element_by_class_name('contributor-content')) == 'WrongPage':
                    print "WrongPage"
                    continue

                # 解析html
                soup = BeautifulSoup(browser.page_source, 'html.parser', from_encoding='utf-8')

                authors = soup.find_all('div', class_='contributor-content')

                book = soup.find('header', class_='book-intro-header').find('h1').get_text()

                for author in authors:
                    if 'China' not in author.find('div'):
                        continue
                    authorName = author.find('h3').get_text()
                    nameQueue.put('%s%s%s' % (authorName, '!!!', book))

            elif 'call-for-papers' in url:
                if WebDriverWait(browser, 120, 0.5).until(
                        lambda browser: browser.find_element_by_class_name('title')) == 'WrongPage':
                    print "WrongPage"
                    continue

                # 解析html
                soup = BeautifulSoup(browser.page_source, 'html.parser', from_encoding='utf-8')

                book = soup.find('div', class_='publication-title').find('h1').get_text()

                authors = soup.find('div', class_='article-content').find_all('p')
                for p in authors:
                    if p.find('br') and 'China' in p.find('br'):
                        authorName = p.find('strong').get_text()
                        university = p.find('br').get_text()
                        nameQueue.put('%s%s%s%s%s' % (authorName, '|', university, '!!!', book))
        browser.quit()

    def getNameSet(self):
        reload(sys)
        sys.setdefaultencoding('utf-8')
        # sys.setdefaultencoding('gbk')
        pool = threadpool.ThreadPool(10)

        # #在IEEE上根据关键字得到搜索页
        # for keyword in keywords:
        #     url = '%s%s%s%s' % ('http://ieeexplore.ieee.org/search/searchresult.jsp?', 'queryText=', keyword, rangeYear)
        #     pageUrlQueue.put(url)
        # requests = threadpool.makeRequests(self.getIeeePages, keywords)
        # [pool.putRequest(req) for req in requests]
        # pool.wait()
        # self.pageWrite('searchPages/ieeePages.txt')

        # # 在ACM上根据关键字得到搜索页
        # for keyword in keywords:
        #     url = '%s%s' % ('http://dl.acm.org/results.cfm?query=', keyword)
        #     pageUrlQueue.put(url)
        # requests = threadpool.makeRequests(self.getACMPages, keywords)
        # [pool.putRequest(req) for req in requests]
        # pool.wait()
        # self.pageWrite('searchPages/acmPages.txt')

        # #根据Ieee的搜索页得到全部document的Url
        # pageUrls = open("searchPages/ieeePages.txt").readlines()
        # for page in pageUrls:
        #     pageUrlQueue.put(page)
        # requests = threadpool.makeRequests(self.getIeeeDocuments, pageUrls[0:10])
        # [pool.putRequest(req) for req in requests]
        # pool.wait()
        # self.docWrite('docUrls/ieeeDocs.txt')

        # #根据acm的搜索页得到全部document的Url
        # pageUrls = open("searchPages/acmPages.txt").readlines()
        # for page in pageUrls:
        #     pageUrlQueue.put(page)
        # requests = threadpool.makeRequests(self.getACMAuthors, pageUrls[0:10])
        # [pool.putRequest(req) for req in requests]
        # pool.wait()
        # self.docWrite('docUrls/acmDocs.txt')

        # #根据acm的搜索页得到全部author的name
        # pageUrls = open("docUrls/acmDocs.txt").readlines()
        # for page in pageUrls:
        #     pageUrlQueue.put(page)
        # requests = threadpool.makeRequests(self.getACMName, pageUrls[0:10])
        # [pool.putRequest(req) for req in requests]
        # pool.wait()
        # self.acmWrite('names/acmNames.txt')


        # # 在ACM上根据关键字得到搜索页
        # for keyword in keywords:
        #     url = '%s%s%s' % ('https://www.elsevier.com/search-results?query=', keyword, '&labels=all')
        #     pageUrlQueue.put(url)
        # numbers = range(0, 10)
        # requests = threadpool.makeRequests(self.getElsDocs, numbers)
        # [pool.putRequest(req) for req in requests]
        # pool.wait()
        # self.pageWrite('searchPages/elsevierPages.txt')

        #根据Ieee的搜索页得到全部document的Url
        num = range(0, 10)
        pageUrls = open("docUrls/ieeeDocs.txt").readlines()
        for page in pageUrls:
            pageUrlQueue.put(page)
        requests = threadpool.makeRequests(self.getIeeeName, num)
        [pool.putRequest(req) for req in requests]
        pool.wait()
        # self.nameWrite('names/ieeeName.txt')

        # self.getAllNames('allNames.txt')