import os
import shutil
from enum import Enum

import nltk
from nltk import ne_chunk, pos_tag, word_tokenize
from nltk.corpus import wordnet as wn
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import TweetTokenizer
from nltk.tree import Tree

from BasicOP import DbControl, nltkhelper, DiskOP


class WordStatue(Enum):
    learned = 0
    unlearned = 1
    over = 2
    # def __init__(self):
    #     self.over=2
    #     pass
    # TESTED


class WordTable(object):
    words = []
    dbcontroler = DbControl()
    # TESTED

    def __init__(self):
        self.words = dict(self.dbcontroler.words_gettable())

    def get_statue(self, word):
        if not word in self.words:
            return WordStatue.over
        else:
            i = self.words[word]
            if i > 1:
                return WordStatue.learned
            elif i > -1:
                return WordStatue.unlearned
            else:
                return WordStatue.over


class Article():
    dbcontroler = DbControl()
    formattedfilepath = ".\\formatted article\\"

    def __init__(self):
        self.index = 0

        self.text = ''
        self.tokens = list()
        self.title = ''
        self.words = dict()
        self.unlearnednum = 0
        self.learnednum = 0
        self.over = 0
        self.weight = 0
        self.checkwords = set()
        self.tokendict = dict()
        # PASSED

    def __gettokens__(self, articleid):
        tokens = DiskOP.article_read(articleid)
        return tokens

    def __gettext__(self, tokens):
        text = ''
        for item in tokens:
            if item[0] == "\\n":
                text += "\n"
            else:
                text += item[0]+' '
        return text

    def read_usingid(self, articleid):
        self.tokens = self.__gettokens__(articleid)
        self.tokendict = dict(self.tokens)
        self.text = self.__gettext__(self.tokens)
        art = self.dbcontroler.article_get(articleid)
        self.title = art[0]
        self.weight = art[1]
        self.unlearnednum = art[2]
        self.learnednum = art[3]
        self.over = art[4]
        self.words = dict(self.dbcontroler.wordof_getweights(articleid))
        pass

    def checkword(self, word):
        if word in self.tokendict:
            self.checkwords.add(self.tokendict[word])

    def __devide_word__(self, update, unlearn_to_learn, learn_to_unlearn):
        for word in self.words:
            if not self.words[word] == -1:
                if not word in self.checkwords:
                    update[word] = self.words[word]+1
                    if update[word] == 2:
                        unlearn_to_learn.add(word)
                else:
                    update[word] = 0
                    if self.words[word] > 1:
                        learn_to_unlearn.add(word)

    def finishread(self):
        update = dict()
        unlearn_to_learn = set()
        learn_to_unlearn = set()
        self.__devide_word__(update, unlearn_to_learn, learn_to_unlearn)

        self.dbcontroler.words_updateweights([[x, update[x]] for x in update])
        for w in unlearn_to_learn:
            ids = self.dbcontroler.wordof_getarticleid(w)
            self.dbcontroler.articles_newlearn1(ids)
        for w in learn_to_unlearn:
            ids = self.dbcontroler.wordof_getarticleid(w)
            self.dbcontroler.articles_newunlearn1(ids)
        pass


class ArticleImporter():
    wordtool = WordTable()
    dbcontroler = DbControl()
    formattedfilepath = ".\\formatted article\\"

    def __init__(self):
        pass

    def __tagtext__(self, sents):
        tokens = list()
        for sent in sents:
            tokens += self.__tagsent__(sent)
            tokens += [('\\n', '')]
        return tokens

    def __tagsent__(self, sent):
        tokens = nltkhelper.tokenize(sent)
        tags = nltkhelper.pos_tag(tokens)
        xtokens = list()
        for word in tags:
            # no name
            origin = ''
            p = nltkhelper.get_pos(word[1])
            if not p == ' ':
                try:
                    origin = (nltkhelper.lemmatize(
                        word[0], p))
                    if not origin in self.wordtool.words:
                        origin = ''
                except:
                    origin = ''
                    pass
            xtokens.append((word[0], origin))
        return xtokens

    def __calculateByStatue__(self, tokens, words):
        learn = 0
        unlearn = 0
        over = 0
        for token in tokens:
            if not token[1] == '':
                words.add(token[1])
        for word in words:
            if not word == '':
                statue = self.wordtool.get_statue(word)
                if statue == WordStatue.learned:
                    learn += 1
                elif statue == WordStatue.unlearned:
                    unlearn += 1
                else:
                    over += 1
        return (learn, unlearn, over)

    def integrate(self, filename):
        title = os.path.split(filename)[1][:-4]
        sents = DiskOP.read_txt_lines(filename)
        tokens = self.__tagtext__(sents)
        words = set()
        num = self.__calculateByStatue__(tokens, words)

        idd = self.dbcontroler.article_add(title, num[1], num[0], num[2])
        # idd=1
        self.dbcontroler.wordof_add(words, idd)
        DiskOP.article_write(idd, tokens)
        return idd


class Articles(object):
    articles = []
    dbcontroler = DbControl()

    def __init__(self):
        self.articles = self.dbcontroler.articles_get()
        self.articles=sorted(self.articles,key=lambda article: article[2],reverse=True)
    def fresh(self):
        self.articles = self.dbcontroler.articles_get()
        self.articles=sorted(self.articles,key=lambda article: article[2],reverse=True)


    @staticmethod
    def get_total(unlearned, learned, over):
        return unlearned+learned+over


def test_import():
    ai = ArticleImporter()
    file = './origin data get/raw article/test112.txt'
    idd = ai.integrate(file)
    print(idd)


def test_article():
    ar = Article()
    ar.read_usingid(1)
    ar.checkword('year')
    ar.checkword('engineer')
    ar.finishread()


if __name__ == "__main__":
    # testArticle()
    # test_article()
    # test_import()
    arts=Articles()
    print(arts.articles)
    pass
