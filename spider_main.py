# coding:utf-8
import nameCrawling, crewByName, output, paperInfoCrew
from selenium import webdriver
profCrawlingUrls = ['https://www.baidu.com/s?wd=Yunhao%20Liu']

if __name__=="__main__":
    # step1 = nameCrawling.NameCrawling()
    # step1.getNameSet()
    # step3 = paperInfoCrew.PaperInfoCrew()
    # professorSet = step3.infoCrew()

    # step2 = crewByName.CrewByName()
    # professorSet = step2.getProfessors()
    step5 = output.Output()
    step5.fileWrite()