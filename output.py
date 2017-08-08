#!/usr/bin/env python
# -*- coding: utf-8 -*-
# #导入excel需要xlwt库的支持
from xlwt import Workbook
import professor
import sys

class Output:
    def __init__(self):
        reload(sys)
        sys.setdefaultencoding('utf-8')
        # 指定file以utf-8的格式打开
        self.file = Workbook(encoding = 'utf-8')
        # 指定打开的文件名
        self.sheet = self.file.add_sheet('sheet')
        self.sheet.write(0, 0, '序号')
        self.sheet.write(0, 1, '名字')
        self.sheet.write(0, 2, '学科')
        self.sheet.write(0, 3, '研究领域')
        self.sheet.write(0, 4, '职称')
        self.sheet.write(0, 5, '所在学校、科研机构')
        self.sheet.write(0, 6, '国家称号')
        self.sheet.write(0, 7, '行政职务')
        self.sheet.write(0, 8, '发表论文情况')
        self.sheet.write(0, 9, '匹配度')
        self.professorMap = {}
        f = open('result4.txt', "r")
        lines = f.readlines()
        for line in lines:
            outputPart = line.split('!!!')[0]
            parts = outputPart.split('|')
            l = len(parts)
            name = parts[0].split('/')[0].strip()
            if not self.professorMap.has_key(name):
                profe = professor.Professor(name)
                if len(parts[0].split('/')) > 1:
                    profe.chineseName = parts[0].split('/')[1]
                if len(parts[1].split('/')) > 1:
                    profe.university = parts[1].split('/')[1]
                profe.chiUniversity = parts[1].split('/')[0]
                if l > 2:
                    profe.ieeeNum = parts[2].strip()
                    # profe.studyArea = parts[2].strip()
                    # profe.studyArea = profe.studyArea.replace('None ', '')
                if parts[3] != 'None':
                    profe.citations = parts[3].strip()
                if parts[4] != 'None':
                    profe.h_index = parts[4].strip()
                if parts[5] != 'None':
                    profe.title = parts[5].strip()
                if parts[6] != 'None':
                    profe.adm = parts[6].strip()
                if parts[7] != 'None':
                    profe.nationalHonor = parts[7].strip()
                if parts[8] != 'None':
                    profe.studyArea = parts[8].strip()

                if profe.nationalHonor and profe.nationalHonor != 'None':
                    profe.rank = 80
                elif profe.adm and profe.adm != 'None':
                    profe.rank = 70
                elif (profe.ieeeNum != 'not found' and profe.h_index != 'not found' and int(profe.ieeeNum) > 10 and int(profe.h_index) > 15) or (profe.ieeeNum == 'not found' and profe.h_index == 'not found'):
                    profe.rank = 60
                else:
                    profe.rank = 0
                if profe.rank > 0:
                    self.professorMap[name] = profe
        f.close()

    def fileWrite(self):
        data_list = []
        for profe in self.professorMap:
            data_list.append(self.professorMap[profe])
        data_list.sort(key=lambda obj: obj.rank, reverse=True)
        x = 1
        for professor in data_list:
            row = self.sheet.row(x)
            row.write(0, x)
            if professor.chineseName == 'None':
                row.write(1, professor.englishName)
            else:
                row.write(1, '%s%s%s' % (professor.chineseName, '/', professor.englishName))
            row.write(2, '计算机')
            row.write(3, professor.studyArea)
            row.write(4, professor.title)
            try:
                row.write(5, professor.chiUniversity.encode('utf-8'))
            except Exception, e:
                # print e
                row.write(5, professor.university)
            row.write(6, professor.nationalHonor)
            row.write(7, professor.adm)
            row.write(8, '%s%s%s%s%s%s' % ('引用次数/Citation：', professor.citations, '\n H因子：', professor.h_index, '\n IEEE Trans.篇数：', professor.ieeeNum))
            row.write(9, professor.rank)
            x += 1
        self.file.save('result.xls')
        return
