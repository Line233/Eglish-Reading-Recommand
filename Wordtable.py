import nltk
import BasicOP
from BasicOP import DbControl
from nltk.corpus import words
from nltk.corpus import wordnet
from BasicOP import DiskOP
import math


def getallwordtable():
    set1 = set(w.lower() for w in words.words() if w.isalpha())
    set2 = set(w.lower() for w in wordnet.words() if w.isalpha())
    return set1.union(set2)


def getnltklist():
    print('1')
    nltklist = list()
    nltklist += list(nltk.corpus.brown.words())
    print('1')
    nltklist += list(nltk.corpus.reuters.words())
    nltklist += list(nltk.corpus.gutenberg.words())
    print('1')
    nltklist += list(nltk.corpus.webtext.words())
    return [x.lower() for x in nltklist if x.isalpha()]


def getFreq(nltklist):
    fdist = nltk.FreqDist(nltklist)
    return dict(fdist)


def calculate_weight_1(words):
    try:
        calculate_weight_1.fdist
    except:
        nltklist = list()
        nltklist += list(nltk.corpus.brown.words())
        nltklist += list(nltk.corpus.reuters.words())
        nltklist += list(nltk.corpus.gutenberg.words())
        nltklist += list(nltk.corpus.webtext.words())
        calculate_weight_1.fdist = nltk.FreqDist(
            [w.lower() for w in nltklist if w.isalpha()])
    word_weight = dict()
    for word in words:
        freq = math.log(calculate_weight_1.fdist[word]+1)
        word_weight[word] = int(freq+0.5)
    return word_weight

def calculate_weight_2(words,freq):
    word_weight = dict()
    for word in words:
        f=0
        if word in freq:
            f=freq[word]
        weight = math.log(f+1)
        word_weight[word] = int(weight+0.5)
    return word_weight

def changeweight(word_weight, inwords):
    diccopy = dict()
    for word in word_weight:
        if word in inwords:
            if word_weight[word] > 6:
                diccopy[word] = 2
            elif word_weight[word] > 2:
                diccopy[word] = 1
            else:
                diccopy[word] = 0
        else:
            if not word_weight[word] == 0:
                diccopy[word] = -1
    return diccopy


def fileter(words, fileterwords):
    set2 = set()
    for word in words:
        if not word in fileterwords:
            set2.add(word)
    return set2


def dic_to_list(dic):
    l = list()
    for key in dic:
        l.append([key, dic[key]])
    return l


allwordfile = ['./origin data get/Vocabulary/allword.txt',
               './origin data get/Vocabulary/allword_without_names.txt']
inwordfiles = ['./origin data get/Vocabulary/raw vocabulary/gaokao.txt',
               './origin data get/Vocabulary/raw vocabulary/cet6.txt', './origin data get/Vocabulary/raw vocabulary/kaoyan.txt']
inwordfile = ['./origin data get/Vocabulary/inwords.txt']
namefile = './origin data get/Vocabulary/names.txt'
weightfile = './origin data get/Vocabulary/weight1.txt'
weightfile2 = './origin data get/Vocabulary/weight2.txt'
weightfileupdate = './origin data get/Vocabulary/weightup.txt'
nltklistfile = './origin data get/Vocabulary/nltklist.txt'
FreqWeightFile = "./origin data get/Vocabulary/Freq.txt"


def preceder_GetNltkList():
    nltklist = getnltklist()
    print(len(nltklist))
    DiskOP.write_wordtable(nltklistfile, nltklist)


def preceder_GetFreq():
    words = DiskOP.read_wordtables([nltklistfile])
    weight = getFreq(words)
    DiskOP.write_weighttable(FreqWeightFile, weight)


def preceder1():
    words = getallwordtable()
    DiskOP.write_wordtable(allwordfile[0], words)


def preceder2():
    names = DiskOP.read_wordtables([namefile])
    words = DiskOP.read_wordtables([allwordfile[0]])
    words = fileter(words, names)
    DiskOP.write_wordtable(allwordfile[1], words)


def preceder3():
    words = DiskOP.read_wordtables([allwordfile[1]])
    weight = calculate_weight_1(words)
    DiskOP.write_weighttable(weightfile, weight)


def preceder4():
    # get inwords
    words = DiskOP.read_wordtables(inwordfiles)
    DiskOP.write_wordtable(inwordfile[0], words)


def preceder5():
    # change weight to system
    # weightfile to weightfile2
    weight = DiskOP.read_weighttable(weightfile)
    inwords = DiskOP.read_wordtables(inwordfile)
    weight = changeweight(weight, inwords)
    DiskOP.write_weighttable(weightfile2, weight)


def preceder6():
    # write to sqlite
    db = DbControl()
    db.words_clear()
    weight = DiskOP.read_weighttable(weightfile2)
    lit = dic_to_list(weight)
    db.words_add(lit)


def preceder7():
    # add normal word filtered by names
    inwords = DiskOP.read_wordtables(inwordfile)
    words = DiskOP.read_wordtables([allwordfile[1]])
    updatewords = fileter(inwords, words)
    freq=DiskOP.read_weighttable(FreqWeightFile)
    weight = calculate_weight_2(updatewords,freq)
    weight = changeweight(weight, inwords)
    DiskOP.write_weighttable(weightfileupdate, weight)

def preceder8():
    weight=DiskOP.read_weighttable(weightfileupdate)
    db = DbControl()
    lit=dic_to_list(weight)
    db.words_add(lit)


def test():
    preceder8()
    # preceder6()

if __name__ == "__main__":
    test()
    # print('ttt')
