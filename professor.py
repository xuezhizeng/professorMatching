# coding:utf-8
class Professor:
    def __init__(self, name):
        #名字 学科 研究领域 职称 所在学校、科研机构 国家称号 行政职务 发表论文情况 匹配度
        self.englishName = name
        self.chineseName = None
        self.subject = '计算机'
        self.studyAreaSet = set()
        self.studyArea = None
        self.title = None
        self.university = None
        self.chiUniversity = None
        self.nationalHonor = ''
        self.nationalHonorSet = set()
        self.adm = None
        self.papers = None
        self.rank = 0

        self.citations = None
        self.h_index = None
        self.ieeeNum = None
        self.detailPage = None

        self.paperInfo = set()