#!/usr/bin/python
# -*- coding: utf-8 -*-
import os
import os.path
import sys
import JavaMapClass

javaMapInsList = []
start = "----------"
keyDiffNum = {}
keyNum = {}  # key:类名, value:数量列表

keyNumSame = []
keyNumIncrease = []
keyNumOther = []

diffIncrease = {}  #key:涨幅, value:类名


# 判断递增的幅度
def analyseIncreaseDis(numList):
    dis = 0
    length = len(numList)
    for ii in range(0, length - 1):
        d = numList[ii + 1] - numList[ii]
        if dis < d:
            dis = d
    return dis


# 判断是否全相等0，递增1，其他2
def analyseRe(numList):
    length = len(numList)
    isAllSame = True
    for ii in range(1, length):
        if numList[0] == numList[ii]:
            continue
        isAllSame = False
        break
    if isAllSame:
        return 0
    isIncrease = True
    for ii in range(0, length - 1):
        if numList[ii] <= numList[ii + 1]:
            continue
        isIncrease = False
        break
    if isIncrease:
        return 1
    return 2


def analyse(d):
    # TODO：这里先对文件进行排序
    for tmp in os.listdir(d):
        f = os.path.join(d, tmp)
        javaMapInsList.append(JavaMapClass.JavaMapClass(f, start))
    pass
    if 0 < len(javaMapInsList):
        allkey = javaMapInsList[0].getkeys()
        for key in allkey:
            for ii in range(0, len(javaMapInsList)):
                ins = javaMapInsList[ii]
                if key not in keyNum:
                    keyNum[key] = []
                keyNum[key].append(ins.getValue(key))
            pass
    # 进行详细的分析
    # 数量没有变化的，增加的，减少的
    for key in keyNum:
        length = len(keyNum[key])
        if 1 < length:
            re = analyseRe(keyNum[key])
            if 0 == re:
                keyNumSame.append(key)
            elif 1 == re:
                keyNumIncrease.append(key)
                dis = analyseIncreaseDis(keyNum[key])
                if dis not in diffIncrease:
                    diffIncrease[dis] = []
                diffIncrease[dis].append(key)
            else:
                keyNumOther.append(key)
                pass
    print("num of same num key:%s" % (len(keyNumSame)))
    print("num of increase num key:%s" % (len(keyNumIncrease)))
    print("num of other key:%s" % (len(keyNumOther)))

    diffKey = diffIncrease.keys()
    print("increase over 10 has %d" % (len(diffKey)))
    diffKey.sort(reverse = True)
    for key in diffKey:
        if 10 < key:
            print("keys %d:%s" % (key, ",  ".join(diffIncrease[key])))


if __name__ == '__main__':
    os.chdir(sys.path[0])
    analyse("F:\\yqwl\\analyseDir\\work")
    # print(analyseIncreaseDis(range(0, 4)))
