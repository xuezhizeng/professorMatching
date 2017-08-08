# coding=utf-8
import professor
import threadpool
import Queue
from selenium import webdriver
from selenium.common.exceptions import *
from wait import WebDriverWait
import sys
import time
import re
from bs4 import BeautifulSoup
import professor
chineseTitle = ['教授', '研究员']
englishTitle = ['full professor', 'Professor']
chineseAdms = ['副校长', '校长助理', '院长', '副院长', '院长助理', '系主任', '副主任']
englishAdms = ['vice president', 'principal assistant ', ' Dean ', ' Vice Dean ', 'Dean Assistant', 'department director', 'deputy director']
nationalHonors = ['千人计划',
                '特聘教授',
                '青年千人计划',
                '长江学者特聘教授',
                '青年长江学者',
                '国家杰出青年科学基金',
                '杰青',
                '优秀青年科学基金',
                '万人计划领军人才',
                '万人计划',
                '青年拔尖人才',
                '973首席科学家',
                '教育部新世纪优秀人才',
                '国务院政府特殊津贴']
area = ['信息科学', '计算机工程', '计算机科学', '计算机应用技术', '自动化', '电子', '通信工程']
nationEnglish = ['thousand people plan',
'Distinguished professor',
'youth Millennium Project',
'Professor of Changjiang studies',
'Young scholar of Yangtze river',
'National Science Fund for Distinguished Young people',
'outstanding youth',
'Outstanding young science foundation',
"Million people plan to lead talent",
'million people plan',
'young top-notch talent',
'973 chief scientist',
"Ministry of education, new century talents.",
'Government special subsidy of the State Council']

baiduUrl = 'https://www.baidu.com/s?wd='
baikeUrl = 'https://baike.baidu.com/item/'
global pageUrlQueue
pageUrlQueue = Queue.Queue()

class CrewByName:
    def getChiUniversity(self, browser, tempProfe):
        university = tempProfe.university
        if university != 'None':
            checkFind = False
            #看百度百科能否找到
            try:
                browser.get('%s%s' % (baikeUrl, university))  # 调用get方法抓取
                if browser.find_element_by_class_name('main-content'):
                    checkFind = True
                else:
                    pass
            except TimeoutException, e:
                browser.get('%s%s' % (baikeUrl, university))
                if browser.find_element_by_class_name('main-content'):
                    checkFind = True
                else:
                    pass
            except WebDriverException, e:
                pass

            if not checkFind:
                url = '%s%s' % (baiduUrl, university)
                try:
                    browser.get(url)  # 调用get方法抓取
                except TimeoutException, e:
                    browser.get(url)
                except WebDriverException, e:
                    pass
                # 解析html
                soup = BeautifulSoup(browser.page_source, 'html.parser', from_encoding='utf-8')
                baike = None
                details1 = soup.find_all('div', class_="result-op c-container xpath-log")
                for d in details1:
                    if '百度百科' in d.find('h3').find('a').get_text():
                        baike = d.find('h3').find('a')['href']
                        checkFind = True
                        break

                if baike:
                    try:
                        browser.get(baike)  # 调用get方法抓取
                    except TimeoutException, e:
                        browser.refresh()
                    except WebDriverException, e:
                        pass

                if not baike:
                    for d in details1:
                        if '百度翻译' in d.find('h3').find('a').get_text():
                            try:
                                chiUniversity = browser.find_element_by_class_name('op_sp_fanyi_line_two').text
                                tempProfe.chiUniversity = chiUniversity
                            except Exception, e:
                                chiUniversity = browser.find_element_by_class_name('op_dict_text2').text
                                tempProfe.chiUniversity = chiUniversity
                            break

            #百科找到直接找出标题
            if checkFind:
                try:
                    if browser.find_element_by_class_name('main-content'):
                        chiUniversity = browser.find_element_by_tag_name('h1').text
                        tempProfe.chiUniversity = chiUniversity

                except Exception, e:
                    browser.refresh()

    def getPagefromBaidu(self, browser, tempProfe):
        name = tempProfe.englishName
        if tempProfe.chiUniversity != 'None':
            university = tempProfe.chiUniversity
        else:
            university = tempProfe.university
        url = '%s%s%s%s' % (baiduUrl, name, ' ', university)

        if university == 'None':
            url = '%s%s' % (url, ' 计算机')

        # url = 'https://www.baidu.com/s?wd=' + university
        try:
            browser.get(url)  # 调用get方法抓取
        except TimeoutException, e:
            browser.get(url)  # 调用get方法抓取

        if WebDriverWait(browser, 30, 0.5).until(
                lambda browser: browser.find_element_by_class_name('n')) == 'WrongPage':
            # print "WrongPaper"
            return

        # 解析html
        soup = BeautifulSoup(browser.page_source, 'html.parser', from_encoding='utf-8')
        details1 = soup.find_all('a', class_="c-showurl")
        # details2 = None
        # try:
        #     browser.find_element_by_class_name('n').click()
        #     soup = BeautifulSoup(browser.page_source, 'html.parser', from_encoding='utf-8')
        #     details2 = soup.find_all('a', class_="c-showurl")
        # except Exception, e:
        #     browser.refresh()
        # if details2:
        #     details1.extend(details2)
        return self.findDetailPage(browser, details1, name)

    def findDetailPage(self, browser, details, name):
        tempnum = 0
        detailUrl = None
        baike = None
        for page in details:
            baikePage = page.find_all('div', class_="result-op c-container xpath-log")
            for d in baikePage:
                if '百度百科' in d.find('h3').find('a').get_text():
                    baike = d.find('h3').find('a')['href']
                    break

            if 'edu.cn' in page.get_text() or 'ac.cn' in page.get_text():
                try:
                    browser.get(page['href'])  # 调用get方法抓取
                except TimeoutException, e:
                    browser.refresh()
                except WebDriverException, e:
                    pass
                tempSoup = BeautifulSoup(browser.page_source, 'html.parser', from_encoding='utf-8')

                num = (str(tempSoup).count(name) +
                       str(tempSoup).count(str.lower(name)) +
                       str(tempSoup).count(str.lower(name).replace(' ', '')) +
                       str(tempSoup).count(str.upper(name)) +
                       str(tempSoup).count(str.upper(name).replace(' ', '')))
                for a in area:
                    num += str(tempSoup).count(a) * 0.1
                if num > tempnum:
                    tempnum = num
                    detailUrl = page['href']
        return detailUrl, baike

    def getDetails(self, browser, detailUrl, profe):
        try:
            browser.get(detailUrl)  # 调用get方法抓取
        except TimeoutException, e:
            browser.refresh()
        except WebDriverException, e:
            pass
        soup = BeautifulSoup(browser.page_source, 'html.parser', from_encoding='utf-8')
        content = soup.find_all('p')

        for p in content:
            text = p.get_text()

            # 获取中文名
            if '姓名' in text:
                names = re.split("[,.:()：。、，（）  |]".decode("utf8"), text)
                for n in names:
                    if '姓名' in n:
                        if names.index(n) + 1 < len(names):
                            profe.chineseName = names[names.index(n) + 1].strip()
                        else:
                            profe.chineseName = content[content.index(p) + 1].get_text()
                            # print names[names.index(n) + 1].strip()

            # 获取 教授/研究员/full professor/Professor，不是的直接过滤
            for titleProfessor in chineseTitle:
                titles = re.split("[,.:()：。、，（） |]".decode("utf8"), text)
                for t in titles:
                    if titleProfessor in t and '副教授' not in t and profe.title == None:
                        profe.title = titleProfessor

            for titleProfessor in englishTitle:
                if profe.title is None and titleProfessor in text and 'associate professor' not in text and 'adjunct professor' not in text:
                    titles = re.split("[.:()。、，（） |]".decode("utf8"), text)
                    for t in titles:
                        if profe.title is None:
                            profe.title = titleProfessor
            # for titleProfessor in chineseTitle:
            #     if titleProfessor in text and title == None:
            #         if '大学' in text:
            #             titles = re.split("[,.:()：。、，（）]".decode("utf8"), text)
            #             for t in titles:
            #                 if titleProfessor in t and '副教授' not in t and title == None:
            #                     title = titleProfessor
            #                     unis = re.split("[  ]".decode("utf8"), t)
            #                     for u in unis:
            #                         if '大学' in u.encode('utf-8'):
            #                             university = '%s%s' % (t[0:t.find('大学')], '大学')

            # for titleProfessor in englishTitle:
            #     if title == None and titleProfessor in text:
            #         if 'University' in text:
            #             titles = re.split("[.:()。、，（）]".decode("utf8"), text)
            #             for t in titles:
            #                 if title == None and 'University' in t:
            #                     title = titleProfessor
            #                     unis = re.split("[,]", t)
            #                     for u in unis:
            #                         if 'University' in u:
            #                             university = u.strip()

        if profe.title is None:
            return

        for p in content:
            text = p.get_text()
            # # 获取学校/科研机构
            # if not university:
            #     if '大学' in text.encode('utf-8') or 'University' in text:
            #         titles = re.split("[,.:()：。、，（）]".decode("utf8"), text)
            #         for t in titles:
            #             if '大学' in t.encode('utf-8'):
            #                 university = '%s%s' % (t.encode('utf-8')[0:t.encode('utf-8').find('大学')], '大学')
            #                 break
            #             if 'University' in t:
            #                 university = t
            #                 break

            # 获取行政职务
            if not profe.adm:
                for chineseAdm in chineseAdms:
                    if chineseAdm in text.encode('utf-8'):
                        adms = re.split("[,.:()：。、，（）  |]".decode("utf8"), text)
                        for a in adms:
                            if chineseAdm in a.encode('utf-8'):
                                profe.adm = '%s%s' % (t.encode('utf-8')[0:t.encode('utf-8').find(chineseAdm)], chineseAdm)

                for englishAdm in englishAdms:
                    if englishAdm in text:
                        adms = re.split("[,.:()：。、，（）  |]".decode("utf8"), text)
                        for a in adms:
                            if englishAdm in a:
                                if 'and' in a:
                                    details = a.split('and')
                                    for d in details:
                                        if englishAdm in d:
                                            profe.adm = d
                                else:
                                    profe.adm = a

            #获取国家称号
            for nationalHonor in nationalHonors:
                if nationalHonor in text.encode('utf-8'):
                    profe.nationalHonorSet.add(nationalHonor)

            for nationalHonor in nationEnglish:
                if nationalHonor in text.encode('utf-8'):
                    profe.nationalHonorSet.add(nationalHonor)

    def getProfe(self, num):
        browser = webdriver.Firefox()  # 初始化Firefox浏览器
        filename = '%d%s' % (num, 'details.txt')
        f = open(filename, 'a')
        while not pageUrlQueue.empty():
            line = pageUrlQueue.get()
            parts = line.split('!!!')
            tempProfe = professor.Professor(parts[0].split('|')[0])
            # tempProfe.university = parts[0].split('|')[1]
            tempProfe.chiUniversity = parts[0].split('|')[1].split('/')[0]
            tempProfe.university = parts[0].split('|')[1].split('/')[1]
            tempProfe.ieeeNum = parts[0].split('|')[2]
            tempProfe.citations = parts[0].split('|')[3]
            tempProfe.h_index = parts[0].split('|')[4]
            tempProfe.studyArea = parts[0].split('|')[5]
            tempProfe.papers = parts[1]

            #学校名转换为机构名
            # self.getChiUniversity(browser, tempProfe)
            # print '%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s' % (
            # tempProfe.englishName, '|', tempProfe.chiUniversity, '/',
            # tempProfe.university, '|', tempProfe.ieeeNum, '|', tempProfe.citations, '|', tempProfe.h_index, '|',
            # tempProfe.studyArea, '!!!', tempProfe.papers.strip())
            #
            # f.write('%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s' % (
            # tempProfe.englishName, '|', tempProfe.chiUniversity, '/',
            # tempProfe.university, '|', tempProfe.ieeeNum, '|', tempProfe.citations, '|', tempProfe.h_index, '|',
            # tempProfe.studyArea, '!!!', tempProfe.papers))

            # 通过百度，edu.cn, ac.cn查找详细信息
            try:
                detailUrl, baike = self.getPagefromBaidu(browser, tempProfe)
            except:
                continue
            tempProfe.detailPage = detailUrl
            # if baike:
            #     self.baikeCheck(browser, baike, tempProfe)
            if detailUrl:
                self.getDetails(browser, detailUrl, tempProfe)

            if tempProfe.title:
                for i in tempProfe.nationalHonorSet:
                    tempProfe.nationalHonor = '%s%s%s' % (tempProfe.nationalHonor, ' ', i)

                print '%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s' % (
                    tempProfe.englishName, '/', tempProfe.chineseName, '|', tempProfe.chiUniversity, '/',
                tempProfe.university, '|', tempProfe.ieeeNum, '|', tempProfe.citations, '|', tempProfe.h_index, '|',
                    tempProfe.title, '|', tempProfe.adm, '|', tempProfe.nationalHonor, '|',
                tempProfe.studyArea, '!!!', tempProfe.papers.strip())

                f.write('%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s' % (
                    tempProfe.englishName, '/', tempProfe.chineseName, '|', tempProfe.chiUniversity, '/',
                tempProfe.university, '|', tempProfe.ieeeNum, '|', tempProfe.citations, '|', tempProfe.h_index, '|',
                    tempProfe.title, '|', tempProfe.adm, '|', tempProfe.nationalHonor, '|',
                tempProfe.studyArea, '!!!', tempProfe.papers))

        browser.close()

    def baikeCheck(self, browser, baike, profe):
        try:
            browser.get(baike)  # 调用get方法抓取
        except TimeoutException, e:
            browser.refresh()

        tempSoup = BeautifulSoup(browser.page_source, 'html.parser', from_encoding='utf-8')
        main_content = tempSoup.find('div', class_='main-content')
        if profe.chiUniversity in str(main_content) and profe.englishName in str(main_content):
            try:
                profe.chineseName = browser.find_element_by_tag_name('h1').text
                soup = BeautifulSoup(browser.page_source, 'html.parser', from_encoding='utf-8')
                content = soup.find_all('p')

                for p in content:
                    text = str(main_content)

                    # 获取 教授/研究员/full professor/Professor，不是的直接过滤
                    for titleProfessor in chineseTitle:
                        titles = re.split("[,.:()：。、，（）<>]".decode("utf8"), text)
                        for t in titles:
                            if titleProfessor in t and '副教授' not in t and profe.title is None:
                                profe.title = titleProfessor

                if profe.title is None:
                    return

                for p in content:
                    text = p.get_text()
                    # 获取行政职务
                    if not profe.adm:
                        for chineseAdm in chineseAdms:
                            if chineseAdm in text.encode('utf-8'):
                                adms = re.split("[,.:()：。、，（）]".decode("utf8"), text)
                                for a in adms:
                                    if chineseAdm in a.encode('utf-8'):
                                        profe.adm = '%s%s' % (
                                        t.encode('utf-8')[0:t.encode('utf-8').find(chineseAdm)], chineseAdm)

                    # 获取国家称号
                    for nationalHonor in nationalHonors:
                        if nationalHonor in text.encode('utf-8'):
                            profe.nationalHonorSet.add(nationalHonor)
            except Exception, e:
                browser.refresh()

    def getProfessors(self):
        reload(sys)
        sys.setdefaultencoding('utf-8')

        pool = threadpool.ThreadPool(10)
        # names = open("trueInfo.txt", 'r').readlines()
        names = open("allChiuni.txt", 'r').readlines()

        num = range(0, 8)
        for name in names:
            pageUrlQueue.put(name)
        requests = threadpool.makeRequests(self.getProfe, num)
        [pool.putRequest(req) for req in requests]
        pool.wait()
