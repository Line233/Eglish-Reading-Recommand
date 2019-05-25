import tkinter
from tkinter import (BOTH, BOTTOM, CENTER, LEFT, RIGHT, VERTICAL, Menu,
                     Scrollbar, Text, Tk, Toplevel, W, X, Y, filedialog, ttk, messagebox)

from WordArticle import Articles, Article
import os

class ArticleWin():

    def __init__(self, root, articleid, parent):
        self.checkword = False
        self.article = Article()
        self.article.read_usingid(articleid)
        self.parent = parent
        # ui
        self.root = root
        self.root.geometry("500x300")
        self.root.protocol("WM_DELETE_WINDOW", self._on_closing_h)
        self._addmenu()
        self._addText()
        self.open = False

    def _freshArticle(self, idd):
        self.text.config(state=tkinter.NORMAL)
        self.article.read_usingid(idd)
        self.text.delete('1.0')
        self.text.insert('1.0', self.article.text)
        self.text.config(state=tkinter.DISABLED)

    def _addmenu(self):
        self.menu = Menu(self.root)
        self.menu.add_command(label='size↑', command=self._increase_font)
        self.menu.add_command(label='size↓', command=self._decrease_font)
        self.menu.add_separator()
        self.menu.add_command(label='finish', command=self._finish_h)
        self.menu.add_separator()
        self.menu.add_command(
            label='give up', command=self._give_up_h)
        # pack
        self.root.config(menu=self.menu)

    def _get_font(self, textfont='Calibri', textsize=20, textstyle='normal'):
        self.textsize = textsize
        return "{} {} {}".format(textfont, textsize, textstyle)

    def _addText(self):
        #
        self.text = Text(self.root)
        self.text.insert('1.0', self.article.text)
        self.text.config(font=self._get_font(), state=tkinter.DISABLED,wrap=tkinter.WORD)
        # bind
        self.text.bind("<Double-Button-1>", self._doubleclick_h)
        self.text.bind("<<Selection>>", self._seletchange_h)
        # scrolbar
        scrollbar = Scrollbar(self.root, orient=VERTICAL)
        scrollbar.config(command=self.text.yview)
        self.text.config(yscrollcommand=scrollbar.set)
        # pack
        scrollbar.pack(side=RIGHT, fill=Y)
        self.text.pack(fill=BOTH, expand=1)

    def mainloop(self):
        self.root.mainloop()
        self.open == True

    def _increase_font(self):
        self.textsize += 2
        self.text.config(font=self._get_font(textsize=self.textsize))

    def _decrease_font(self):
        self.textsize -= 2
        self.text.config(font=self._get_font(textsize=self.textsize))

    def _destroy(self):
        self.root.destroy()
        self.open = False

    def _save(self):
        self.article.finishread()
        self.parent.children_close()

    def _finish_h(self):
        self._save()
        self._destroy()  # FIXME: add finish

    def _askForSave(self):
        b = messagebox.askyesno('exit', 'save study change?')
        if b == True:
            self._save()
        return b

    def _on_closing_h(self):
        b = self._askForSave()
        self._destroy()

    def reloadx(self, articleid):
        if self.open == True:
            b = self._askForSave()
        self._freshArticle(articleid)
        # FIXME fix

    def _give_up_h(self):
        self._destroy()
        pass

    def _doubleclick_h(self, Event):
        self.checkword = True

    def _seletchange_h(self, evet):
        if self.checkword == True:
            try:
                str = self.text.selection_get()
                if str.isalpha():
                    self.article.checkword(str)
                    os.system("echo '%s' | clip" % str)
            except:
                pass
            self.checkword = False


class ArticlesWin():
    heads = ('id', 'title', 'total', 'unlearned', 'leaned', 'over', 'weight')
    headweight = ('20', '300', '50', '50', '50', '50', '50')
    articles = Articles()

    def __init__(self, root):
        self.root = root
        root.geometry("700x300")
        # self.top=Toplevel()
        # menu
        self.menu = Menu(self.root)
        root.config(menu=self.menu)
        self.menu.add_command(label='import', command=self.importcommand)
        # tree
        self.fulltree()

    def _freshTree(self):
        # tree-insert
        self.tree.delete(*self.tree.get_children())
        self.articles.fresh()
        for art in self.articles.articles:
            total = art[3]+art[4]+art[5]
            self.tree.insert('', 'end', values=(
                art[0], art[1], total, art[3], art[4], art[5], art[2]))
        # tree-double click

    def fulltree(self):
        # tree
        self.tree = ttk.Treeview(
            self.root, columns=self.heads, selectmode='browse')
        self.tree['show'] = 'headings'
        for head, weight in zip(self.heads, self.headweight):
            self.tree.heading(head, text=head)
            self.tree.column(head, width=weight, stretch=0, anchor=CENTER)
        self.tree.column('#0', width=0)
        self.tree.column('title', width='300', stretch=1, anchor=W)
        self.tree.bind('<Double-Button-1>', self.open_article)
        # scrolbar
        scrollbar = Scrollbar(self.root, orient=VERTICAL)
        scrollbar.config(command=self.tree.yview)
        self.tree.config(yscrollcommand=scrollbar.set)
        # pack
        scrollbar.pack(side=RIGHT, fill=Y)
        self.tree.pack(fill=BOTH, pady=0, expand=1)
        self._freshTree()

    def importcommand(self):
        print('import function has not been constructed')
        pass

    def open_article(self, event):
        sel = self.tree.selection()[0]
        idd = self.tree.item(sel)['values'][0]
        # print('open_article:', idd)  # FIXME open article window
        try:
            if self.articlewin.open == True:
                self.articlewin.reloadx()
            else:
                self.top = Toplevel()
                self.articlewin = ArticleWin(self.top, idd, self)
                self.articlewin.mainloop()
        except:
            self.top = Toplevel()
            self.articlewin = ArticleWin(self.top, idd, self)
            self.articlewin.mainloop()
        pass

    def mainloop(self):
        self.root.mainloop()

    def children_close(self):
        self._freshTree()


def testarticleswin():
    # root=Tk()
    root = Tk()
    artswin = ArticlesWin(root)
    artswin.mainloop()
    pass


def testarticlewin():
    root = Tk()
    artwin = ArticleWin(root, 1)
    artwin.mainloop()


if __name__ == "__main__":
    testarticleswin()
