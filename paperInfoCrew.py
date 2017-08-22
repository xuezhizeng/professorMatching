# coding=utf-8
import professor
import threadpool
import Queue
from selenium.common.exceptions import *
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from wait import WebDriverWait
import sys
import time
import re
from bs4 import BeautifulSoup
from selenium.webdriver.common.proxy import Proxy
from selenium.webdriver.common.proxy import ProxyType
global pageUrlQueue
pageUrlQueue = Queue.Queue()
global profeMap
profeMap = {}
googleSchalarUrl = 'http://a.a.88dr.com/'
googleSchalarUrl = 'https://c.ggkai.men/extdomains/scholar.google.com/'
personPage = 'https://c.ggkai.men'
selectedKeys = [
    'cyber physical system',
    'crowd computing',
    'crowdsensing',
    'crowd sensing',
    'mobile application',
    'crowdsourcing',
    'social network',
    'service computing，cloud computing'
]
class PaperInfoCrew:
    def __init__(self):
        self.email = 'sh.wu@siat.ac.cn'
        self.password = '546black'

    # 从DBLP可以统计发表IEEE Trans.篇数
    def DBLPcrew(self, num):
        browser = webdriver.Firefox()  # 初始化Firefox浏览器
        filename = '%d%s' % (num, 'nameIeeeNum.txt')
        ieeeNum = 'not found'
        f = open(filename, 'a')
        while not pageUrlQueue.empty():
            nameDs = pageUrlQueue.get().split('!!!')
            author = nameDs[0].split('|')[0]
            papers = nameDs[1].split('*@*')
            #根据论文找作者
            for paper in papers:
                paper = paper.strip()
                url = '%s%s' % ('http://dblp.uni-trier.de/search?q=', paper)
                try:
                    browser.get(url)  # 调用get方法抓取
                except TimeoutException, e:
                    browser.refresh()
                # # # 等待网页加载完
                if WebDriverWait(browser, 30, 0.5).until(
                        lambda browser: browser.find_element_by_class_name('title')) == 'WrongPage':
                    # print "WrongPaper"
                    continue

                # 解析html
                soup = BeautifulSoup(browser.page_source, 'html.parser', from_encoding='utf-8')

                datas = soup.find_all('div', class_='data')
                detailLink = None
                for d in datas:
                    if paper == d.find('span', class_='title').get_text().strip('.'):
                        links = d.find_all('a')
                        for link in links:
                            if link.find('span') and link.find('span').get_text() == author:
                                detailLink = link['href']
                                break
                    if detailLink:
                        break
                #找到author后进入链接查找ieeeNum
                try:
                    browser.get(detailLink)  # 调用get方法抓取
                except TimeoutException, e:
                    browser.refresh()
                except WebDriverException, e:
                    pass
                if WebDriverWait(browser, 60, 0.5).until(
                        lambda browser: browser.find_element_by_id('max-record-info')) == 'WrongPage':
                    # print 'WrongPage'
                    continue
                #动态检查行不通，所以强行等待
                time.sleep(4)
                soup = BeautifulSoup(browser.page_source, 'html.parser', from_encoding='utf-8')
                ieeeNum = soup.find('div', id='authorpage-refine').find('span', id='max-record-count').get_text()

                # if profeMap.has_key(author):
                #     profeMap[author].ieeeNum = ieeeNum
                # else:
                #     profe = professor.Professor(author)
                #     profe.ieeeNum = ieeeNum
                #     profeMap[author] = profe
                # f.write(author)
                if ieeeNum:
                    break
            print '%s%s%s%s%s' % (nameDs[0], '|', ieeeNum, '!!!', nameDs[1].strip())
            f.write('%s%s%s%s%s%s' % (nameDs[0], '|', ieeeNum, '!!!', nameDs[1], '\n'))
        browser.quit()

    # 从Research gate可以统计citation和H因子
    def rgateCrew(self, num):
        browser = webdriver.Firefox()  # 初始化Firefox浏览器
        filename = '%d%s' % (num, 'nameCi.txt')
        f = open(filename, 'a')
        #登陆
        rgateHome = 'https://www.researchgate.net/home'
        try:
            browser.get(rgateHome)  # 调用get方法抓取
        except TimeoutException, e:
            browser.refresh()
        if browser.find_element_by_id('input-password'):
            try:
                browser.find_element_by_id('input-login').send_keys(self.email)
                print 'Email input success!'
            except:
                print 'Email is wrong!'

            try:
                browser.find_element_by_id('input-password').send_keys(self.password)
                print 'password input success!'
            except:
                print 'password is wrong!'

            try:
                browser.find_element_by_tag_name('button').click()
                print 'click input success!'
            except:
                print 'click is wrong!'

        while not pageUrlQueue.empty():
            nameDs = pageUrlQueue.get().split('!!!')
            name = nameDs[0].split('|')[0]
            university = nameDs[0].split('|')[1]
            ieeeNum = nameDs[0].split('|')[2]
            papers = nameDs[1].split('*@*')
            citations = 'not found'
            h_index = 'not found'
            for paper in papers:
                isThisPaper = False
                paper = paper.strip()
                paperUrl = '%s%s' % ('https://www.researchgate.net/search.Search.html?type=publication&query=', paper)
                try:
                    browser.get(paperUrl)  # 调用get方法抓取
                except TimeoutException, e:
                    browser.refresh()

                # 解析html
                soup = BeautifulSoup(browser.page_source, 'html.parser', from_encoding='utf-8')
                # 通过论文查找有无相应论文
                if not soup.find('div', class_='publications-search'):
                    continue
                lis = soup.find('div', class_='publications-search').find_all('li')
                for li in lis:
                    # 看是否有该论文
                    if li.find('span', class_='publication-title js-publication-title').get_text() == paper:
                        # 打开论文页
                        paperLink = '%s%s' % ('https://www.researchgate.net/',
                                             li.find('a', class_=re.compile(r'js-publication-title-link'))['href'])
                        try:
                            browser.get(paperLink) # 调用get方法抓取
                        except TimeoutException, e:
                            browser.refresh()

                        if WebDriverWait(browser, 30, 0.5).until(
                                lambda browser: browser.find_element_by_class_name('publication-author-position')) == 'WrongPage':
                            # print "WrongPaper"
                            pass
                        # 显示全部author
                        try:
                            if browser.find_element_by_class_name('author-list-action-button'):
                                if browser.find_element_by_class_name('author-list-action-button').text != 'Hide':
                                    browser.find_element_by_class_name('author-list-action-button').click()
                                    time.sleep(2)
                        except NoSuchElementException, e:
                            pass

                        soup = BeautifulSoup(browser.page_source, 'html.parser', from_encoding='utf-8')
                        # 找到所以authors
                        authors = soup.find('div', class_='publication-header-container') \
                            .find_all('li', class_='publication-author-list-item')

                        for author in authors:
                            alink = author.find('a', class_='publication-author-name ga-author-name')
                            if alink is None:
                                continue
                            # 找到作者
                            if alink.find('span').get_text() == name:
                                isThisPaper = True
                                # 若无简介直接跳出
                                if 'profile' not in alink['href']:
                                    # print 'author has not profile'
                                    break

                                # 从anthor的profile中找citation和h-index
                                authorUrl = '%s%s' % ('https://www.researchgate.net/', alink['href'])
                                try:
                                    browser.get(authorUrl)  # 调用get方法抓取
                                except TimeoutException, e:
                                    browser.refresh()
                                if WebDriverWait(browser, 30, 0.5).until(
                                        lambda browser: browser.find_element_by_class_name(
                                            'profile-highlights-stats')) == 'WrongPage':
                                    # print "WrongPaper"
                                    pass
                                soup = BeautifulSoup(browser.page_source, 'html.parser', from_encoding='utf-8')
                                # 找citations
                                citations = soup.find('ul', class_='profile-highlights-stats__items') \
                                    .find('a', href=re.compile(r'citation')) \
                                    .find('div').get_text()

                                try:
                                    if soup.find('div', class_='indent-content institution org'):
                                        university = soup.find('div', class_='indent-content institution org').find(
                                            'a').get_text().strip()
                                except:
                                    pass

                                # 找h-index
                                try:
                                    scoreUrl = '%s%s' % ('https://www.researchgate.net/',
                                                         soup.find('div', class_=re.compile(r'tab-bar-plain'))
                                                         .find('a', class_=re.compile(r'score'))['href'])
                                except Exception, e:
                                    pass
                                try:
                                    browser.get(scoreUrl) # 调用get方法抓取
                                except TimeoutException, e:
                                    browser.refresh()
                                if WebDriverWait(browser, 30, 0.5).until(
                                        lambda browser: browser.find_element_by_class_name(
                                            'rg-score-main')) == 'WrongPage':
                                    # print "WrongPaper"
                                    pass
                                soup = BeautifulSoup(browser.page_source, 'html.parser', from_encoding='utf-8')
                                if soup.find('div', class_='h-index'):
                                    h_index = soup.find('div', class_='h-index').find('div', class_='number').get_text()
                                # if profeMap.has_key(name):
                                #     if university:
                                #         profeMap[name].university = university
                                #     profeMap[name].citations = citations
                                #     profeMap[name].h_index = citations
                                # else:
                                #     profe = professor.Professor(name)
                                #     if university:
                                #         profe.university = university
                                #     profe.h_index = h_index
                                #     profe.citations = citations
                                #     profeMap[name] = profe

                                # f.write(nameDs[0])

                    # 通过论文找到就直接跳出
                    if isThisPaper:
                        break

                # 通过论文找到就直接跳出
                if isThisPaper:
                    break
            f.write('%s%s%s%s%s%s%s%s%s' % (name, '|', university, '|', ieeeNum, '|', citations, '|', h_index))
            print '%s%s%s%s%s%s%s%s%s' % (name, '|', university, '|', ieeeNum, '|', citations, '|', h_index)
        browser.quit()

    def profeWrite(self, filename):
        with open(filename, "w") as f:
            for profe in profeMap:
                f.write('%s%s%s%s%s%s%s%s' % (profeMap[profe].englishName, '|', profeMap[profe].citations, '|', profeMap[profe].h_index, '|', profeMap[profe].ieeeNum, '\n'))

    def googleScholarSearch(self, num):
        # profile = webdriver.FirefoxProfile()
        # profile.set_preference('network.proxy.type', 1)
        # profile.set_preference('network.proxy.http', '127.0.0.1')
        # profile.set_preference('network.proxy.http_port', 17890)  # int
        # profile.update_preferences()
        # browser = webdriver.Firefox(firefox_profile=profile)

        browser = webdriver.Firefox()  # 初始化Firefox浏览器
        filename = '%d%s' % (num, 'nameIeeeNum.txt')
        f = open(filename, 'a')
        while not pageUrlQueue.empty():
            nameDs = pageUrlQueue.get().split('!!!')
            parts = nameDs[0].split('|')
            tempProfe = professor.Professor(parts[0])
            tempProfe.university = parts[1]
            tempProfe.ieeeNum = parts[2]
            tempProfe.citations = parts[3]
            tempProfe.h_index = parts[4]
            tempProfe.studyArea = parts[5]
            papers = nameDs[1].split('*@*')

            authorFind = False
            for paper in papers:
                paper = paper.strip()
                try:
                    browser.get(googleSchalarUrl)  # 调用get方法抓取
                    browser.find_element_by_class_name('gs_in_txt').send_keys(paper)
                    browser.find_element_by_id('gs_hp_tsb').click()
                except TimeoutException, e:
                    browser.get(googleSchalarUrl)
                    browser.find_element_by_class_name('gs_in_txt').send_keys(paper)
                    browser.find_element_by_id('gs_hp_tsb').click()
                except WebDriverException, e:
                    continue

                if WebDriverWait(browser, 30, 0.5).until(
                        lambda browser: browser.find_element_by_class_name('gs_r')) == 'WrongPage':
                    # print "WrongPaper"
                    continue

                # 解析html
                soup = BeautifulSoup(browser.page_source, 'html.parser', from_encoding='utf-8')

                items = soup.find_all('div', class_='gs_a')
                authors = None
                for item in items:
                    authors = item.find_all('a')
                    # authors = item.fing('div', class_='gs_a').find_all('a')
                    break

                if not authors:
                    continue

                for author in authors:
                    url = '%s%s' % (personPage, author['href'])
                    try:
                        browser.get(url)  # 调用get方法抓取
                    except TimeoutException, e:
                        browser.get(url)

                    if WebDriverWait(browser, 30, 0.5).until(
                        lambda browser: browser.find_element_by_class_name('gsc_rsb_std')) == 'WrongPage':
                        # print "WrongPaper"
                        continue

                    if browser.find_element_by_id('gsc_prf_in').text == tempProfe.englishName:
                        authorFind = True
                        # 解析html
                        soup = BeautifulSoup(browser.page_source, 'html.parser', from_encoding='utf-8')

                        details = soup.find_all('div', class_='gsc_prf_il')

                        try:
                            tempProfe.university = details[0].find('a').get_text()
                        except:
                            tempProfe.university = details[0].get_text()
                        tempKeywords = []
                        keywords = details[1].find_all('a')
                        for keyword in keywords:
                            tempKeywords.append(keyword.get_text())

                        tempProfe.studyArea = ','.join(tempKeywords)

                        datas = soup.find_all('td', class_='gsc_rsb_std')
                        tempProfe.citations = datas[0].get_text()
                        tempProfe.h_index = datas[2].get_text()

                if authorFind:
                    break

            #通过论文找不到时，使用名字查找
            if not authorFind:
                try:
                    browser.get(googleSchalarUrl)  # 调用get方法抓取
                    browser.find_element_by_class_name('gs_in_txt').send_keys(tempProfe.englishName)
                    browser.find_element_by_id('gs_hp_tsb').click()
                except TimeoutException, e:
                    browser.get(googleSchalarUrl)
                    browser.find_element_by_class_name('gs_in_txt').send_keys(tempProfe.englishName)
                    browser.find_element_by_id('gs_hp_tsb').click()

                if WebDriverWait(browser, 30, 0.5).until(
                        lambda browser: browser.find_element_by_class_name('gs_r')) == 'WrongPage':
                    # print "WrongPaper"
                    continue

                # 解析html
                soup = BeautifulSoup(browser.page_source, 'html.parser', from_encoding='utf-8')

                items = soup.find_all('div', class_='gs_r')
                authors = None
                url = None
                for item in items:
                    if '个人学术档案' in str(item):
                        url = '%s%s' % (personPage, item.find('a')['href'])
                        break

                authorUrl = None
                if url:
                    try:
                        browser.get(url)  # 调用get方法抓取
                    except TimeoutException, e:
                        browser.get(url)

                    if WebDriverWait(browser, 30, 0.5).until(
                            lambda browser: browser.find_element_by_class_name('gsc_1usr_name')) == 'WrongPage':
                        # print "WrongPaper"
                        continue

                    # 解析html
                    soup = BeautifulSoup(browser.page_source, 'html.parser', from_encoding='utf-8')
                    links = soup.find_all('div', class_='gsc_1usr_text')

                    for author in links:
                        if tempProfe.englishName in str(author.find('a')):
                            select = str.lower(str(author))
                            for i in selectedKeys:
                                if i in select:
                                    authorUrl = '%s%s' % (personPage, author.find('a')['href'])
                                    authorFind = True
                                    break

                        if authorFind:
                            break

                if authorUrl:
                    try:
                        browser.get(authorUrl)  # 调用get方法抓取
                    except TimeoutException, e:
                        browser.get(authorUrl)

                    if WebDriverWait(browser, 30, 0.5).until(
                            lambda browser: browser.find_element_by_class_name('gsc_rsb_std')) == 'WrongPage':
                        # print "WrongPaper"
                        continue

                    soup = BeautifulSoup(browser.page_source, 'html.parser', from_encoding='utf-8')

                    details = soup.find_all('div', class_='gsc_prf_il')

                    try:
                        tempProfe.university = details[0].find('a').get_text()
                    except:
                        tempProfe.university = details[0].get_text()
                    tempKeywords = []
                    keywords = details[1].find_all('a')
                    for keyword in keywords:
                        tempKeywords.append(keyword.get_text())

                    tempProfe.studyArea = ','.join(tempKeywords)

                    datas = soup.find_all('td', class_='gsc_rsb_std')
                    tempProfe.citations = datas[0].get_text()
                    tempProfe.h_index = datas[2].get_text()

                # if not authors:
                #     continue

            print '%s%s%s%s%s%s%s%s%s%s%s%s%s' % (
                tempProfe.englishName, '|',
                tempProfe.university, '|', tempProfe.ieeeNum, '|', tempProfe.citations, '|', tempProfe.h_index, '|',
                tempProfe.studyArea, '!!!', '*@*'.join(papers).strip())

            f.write('%s%s%s%s%s%s%s%s%s%s%s%s%s' % (
                tempProfe.englishName, '|',
                tempProfe.university, '|', tempProfe.ieeeNum, '|', tempProfe.citations, '|', tempProfe.h_index, '|',
                tempProfe.studyArea, '!!!', '*@*'.join(papers)))
        browser.quit()

    def infoCrew(self):
        reload(sys)
        sys.setdefaultencoding('utf-8')
        pool = threadpool.ThreadPool(10)

        names = open("restName4.txt", 'r').readlines()
        num = range(0, 10)

        for name in names:
            pageUrlQueue.put(name)
        requests = threadpool.makeRequests(self.DBLPcrew, num)
        [pool.putRequest(req) for req in requests]
        pool.wait()

        # for name in names:
        #     pageUrlQueue.put(name)
        # requests = threadpool.makeRequests(self.rgateCrew, num)
        # [pool.putRequest(req) for req in requests]
        # pool.wait()

        # for name in names:
        #     pageUrlQueue.put(name)
        # requests = threadpool.makeRequests(self.googleScholarSearch, num)
        # [pool.putRequest(req) for req in requests]
        # pool.wait()

        # self.profeWrite('authorInfo.txt')