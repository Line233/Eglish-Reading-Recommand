import os
import sqlite3
from enum import Enum
import nltk
from nltk import ne_chunk, pos_tag, word_tokenize
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import TweetTokenizer
from nltk.tree import Tree
import shutil


class DbControl(object):
    dbname = '.\\words.sqlite'

    def __init__(self):
        self.db = sqlite3.connect(self.dbname)
        self.cursor = self.db.cursor()

    # words table opereate
    def words_add(self, word_weight):
        self.cursor.executemany("insert into words values(?,?)", word_weight)
        self.db.commit()
        # PASSED

    def words_clear(self):
        self.cursor.execute("delete from words")
        self.db.commit()
        # PASSED

    def words_gettable(self):
        self.cursor.execute("SELECT * FROM words;")
        words = self.cursor.fetchall()
        return [w for w in words]
        # PASSED

    def words_updateweights(self, weights):
        std_weights = [[w[1], w[0]] for w in weights]
        self.cursor.executemany(
            "update words set weights=? where word=?", std_weights)
        self.db.commit()
        # PASSED
    # words table opereate

    # wordof OP
    def wordof_getarticleid(self, word):
        self.cursor.execute(
            "select articleid from unlearnedin where word=?", [word])
        return set(self.cursor.fetchall())
        # PASSED

    def wordof_getwords(self, articleid):
        self.cursor.execute(
            "SELECT word FROM unlearnedin WHERE articleid=? ", [articleid])
        return self.cursor.fetchall()
        # PASSED
    def wordof_getweights(self, articleid):
        self.cursor.execute(
            "SELECT unlearnedin.word,words.weights  FROM unlearnedin inner join words on words.word=unlearnedin.word WHERE articleid=? ", [articleid])
        return self.cursor.fetchall()
        #PASSED
    def wordof_add(self, words, articleid):
        for w in words:
            self.cursor.execute(
                "INSERT INTO unlearnedin VALUES(?,?)", (w, articleid))
        self.db.commit()
        # PASSED
    # wordof OP

    # ARTICLES OP
    def articles_updateweight(self,articleids):
        self.cursor.executemany("update articles set weight=cast((unlearned*1.0/(learned+unlearned+over)*100) as int) where articleid=?",articleids)
        self.db.commit()
    def articles_newlearn1(self, articleids):
        self.cursor.executemany(
            "update articles set unlearned=unlearned-1,learned=learned+1 where articleid=?", articleids)
        self.db.commit()
        self.articles_updateweight(articleids)

    def articles_newunlearn1(self, articleids):
        self.cursor.executemany(
            "update articles set unlearned=unlearned+1,learned=learned-1 where articleid=?", articleids)
        self.db.commit()
        self.articles_updateweight(articleids)
        # PASS

    def articles_get(self):
        self.cursor.execute("SELECT * FROM articles")
        arts = list(self.cursor.fetchall())
        for index, art in enumerate(arts):
            arts[index] = [x if not x is None else 0 for x in art]
        return arts
        # 0|articleid|INTEGER|0||1
        # 1|title|TEXT|1||0
        # 2|weight|INTEGER|0||0
        # 3|unlearned|INTEGER|0||0
        # 4|learned|INTEGER|0||0
        # 5|over|INTEGER|0||0
        # PASSED

    # ARTICLES OP
    # ARTICLE OP

    def article_get(self, articleid):
        self.cursor.execute(
            "SELECT title,weight,unlearned,learned,over FROM articles WHERE articleid=? LIMIT 1", [articleid])
        return self.cursor.fetchone()
        # PASSED

    def article_getid(self, title):
        self.cursor.execute(
            "SELECT articleid FROM articles WHERE title=? LIMIT 1", [title])
        return self.cursor.fetchone()[0]
        # PASSED

    def article_add(self, title, unlearn, learn, over):
        weight = int(unlearn/(learn+unlearn+over)*100)  # FIXME depart weigh
        self.cursor.execute("INSERT INTO articles(title,weight,learned,unlearned,over) VALUES(?,?,?,?,?)",
                            (title, weight, learn, unlearn, over))
        self.db.commit()
        idd = self.article_getid(title)
        return idd
    # ARTICLE OP

    def add_article_x(self, title, weight, unlearnedword, learned, unlearned, over):
        self.cursor.execute("INSERT INTO articles(title,weight,learned,unlearned,over) VALUES(?,?,?,?,?)",
                            (title, weight, learned, unlearned, over))
        self.db.commit()
        self.cursor.execute(
            "SELECT articleid FROM articles WHERE title='?' LIMIT 1", title)
        arti = self.cursor.fetchone()
        for w in unlearnedword:
            self.cursor.execute(
                "INSERT INTO unlearnedin VALUES(?,?)", (arti, w))
        self.db.commit()

    def add_article(self, title, weight, unlearn, learn, over):
        self.cursor.execute("INSERT INTO articles(title,weight,learned,unlearned,over) VALUES(?,?,?,?,?)",
                            (title, weight, learn, unlearn, over))
        self.db.commit()
        idd = self.article_getid(title)
        return idd

    def add_article_words(self, words, articleid):
        for w in words:
            self.cursor.execute(
                "INSERT INTO unlearnedin VALUES(?,?)", (w, articleid))
        self.db.commit()


class nltkhelper:
    lemmatizer = WordNetLemmatizer()
    tokenizer = TweetTokenizer()
    # TESTED
    @staticmethod
    def tokenize(sent):
        return nltkhelper.tokenizer.tokenize(sent)

    @staticmethod
    def pos_tag(sent):
        return nltk.pos_tag(sent, tagset='universal')

    @staticmethod
    def peek_tag(sent):
        return ne_chunk(nltk.pos_tag(sent))

    @staticmethod
    def lemmatize(word, p):
        return nltkhelper.lemmatizer.lemmatize(word.lower(), p).lower()

    @staticmethod
    def get_pos(tag):
        if tag in ['NOUN', 'VERB', 'ADJ', 'ADV']:
            if tag == 'ADV':
                return 'r'
            else:
                return tag[0].lower()
        else:
            return ' '


class DiskOP():
    @staticmethod
    def list_read(filename):
        lis = list()
        f = open(filename, 'r', encoding='utf-8')
        for line in f:
            lis.append(line[:-1].lower())
        f.close()

    @staticmethod
    def list_write(filename, lis):
        f = open(filename, "w", encoding="utf-8")
        for item in lis:
            f.write("{}\n".format(item))
        f.close()

    @staticmethod
    def tuplelist_write(filename, tuples):
        f = open(filename, "w", encoding="utf-8")
        for item in tuples:
            f.write("{}\t{}\n".format(item[0], item[1]))
        f.close()

    @staticmethod
    def tuplelist_read(filename):
        lis = list()
        f = open(filename, "r", encoding="utf-8")
        for line in f:
            items = line[:-1].split("\t")
            lis.append((items[0], items[1]))
        f.close()
        return lis

    @staticmethod
    def read_wordtables(filenames):
        set1 = list()
        for name in filenames:
            f = open(name, 'r')
            for line in f:
                set1.append(line[:-1].lower())
            f.close()
        return set1

    @staticmethod
    def write_wordtable(filename, words):
        f = open(filename, "w", encoding="utf-8")
        for word in words:
            f.write("{}\n".format(word))
        f.close()

    @staticmethod
    def read_weighttable(filename):
        fs = open(filename, 'r', encoding='utf-8')
        dic = dict()
        for line in fs:
            words = line.split("\t")
            dic[words[0]] = int(words[1][:-1])
        return dic

    @staticmethod
    def write_weighttable(filename, dic):
        f = open(filename, "w", encoding='utf-8')
        for word in dic:
            f.write("{}\t{}\n".format(word, dic[word]))
        f.close()

    @staticmethod
    def read_txt_lines(filename):
        file = open(filename, 'r', encoding='utf-8')
        lines = file.readlines()
        file.close()
        return lines

    @staticmethod
    def article_path(idd):
        formattedfilepath = ".\\formatted article\\"
        return "{}{}.txt".format(formattedfilepath, idd)

    @staticmethod
    def moveToFolder(self, filepath, idd):
        shutil.copy(filepath, article_path(idd))

    @staticmethod
    def article_read(idd):
        return DiskOP.tuplelist_read(DiskOP.article_path(idd))
        # fs = open(DiskOP.article_path(idd), 'r', encoding='utf-8')
        # lis = list()
        # for line in fs:
        #     words = line.split("\t")
        #     lis.append((words[0], words[1][:-1]))
        # return lis

    @staticmethod
    def article_write(idd, tokens):
        f = open(DiskOP.article_path(idd), "w", encoding='utf-8')
        for word in tokens:
            f.write("{}\t{}\n".format(word[0], word[1]))
        f.close()


def testdbcontroler():
    db = DbControl()
    # idd = db.add_article("test2", 2/(2+3+5)*100, 2, 3, 5)[0]
    # print(idd)
    # db.wordof_add(['comfort', 'tissue', ], idd)
    # words = db.words_gettable()
    # art = db.article_get(28)
    # print(art)
    # words = db.wordof_getwords(31)
    # print(words)
    # print(len(words))
    arts = db.wordof_getweights(1)
    print(arts)


def testnltkhelper():
    tokens = nltkhelper.tokenize('i am a good boy.\nyou too\n')
    tokens = nltkhelper.peek_tag(tokens)

    print(tokens)
    # tokens_tags = nltkhelper.peek_tag(tokens)
    # print(tokens_tags)
    # word = nltkhelper.lemmatize('plays', 'v')
    # print(word)


def test_update_weight():
    db = DbControl()
    li = db.wordof_getwords(6)
    print(li)


if __name__ == "__main__":
    testdbcontroler()
    # testnltkhelper()
    # testnltkhelper()
    # DiskOP.write_wordtable('./aa.txt',['hh'])
