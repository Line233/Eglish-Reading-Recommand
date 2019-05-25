from Windows import ArticleWin,ArticlesWin
import tkinter
from tkinter import Tk
if __name__ == "__main__":
    # ctypes.windll.shcore.SetProcessDpiAwareness(1)
    root = Tk()
    artswin = ArticlesWin(root)
    artswin.mainloop()
    pass