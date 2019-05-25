from BasicOP import DiskOP
from WordArticle import ArticleImporter
import os
import traceback
def read_txt_lines(filename):
    file = open(filename, 'r', encoding='utf-8')
    lines = file.readlines()
    file.close()
    return lines
def wirte(filename,str2):
    f=open(filename,'w',encoding='utf-8')
    f.write(str2)
    f.close()
path='C:\\Users\\Jacky\\Downloads\\2014年12月VOA常速英语听力音频打包下载\\2014年12月VOA常速英语听力音频打包下载\\New folder\\y\\'
if __name__ == "__main__":
    # import os
    # files=os.listdir(path)
    # for file in files:
    #     if file[-4:]=='.lrc':
    #         try:
    #             lines=DiskOP.read_txt_lines(path+file,encodingx='gbk')
    #             olines=''
    #             for line in lines[4:]:
    #                 olines+=line[10:]
                
    #             wirte(path+'y\\'+file[:-4]+'.txt',olines)
    #         except Exception as e:
    #             print(traceback.format_exc())
    #             pass
    # path='C:\\Users\\Jacky\\Downloads\\2014年12月VOA常速英语听力音频打包下载\\2014年12月VOA常速英语听力音频打包下载\\New folder'
    import os
    files=os.listdir(path)
    at=ArticleImporter()
    for file in files:
        try:
            at.integrate(path+file)
        except Exception as e:
            print(traceback.format_exc())


        
# DiskOP.read_txt_lines()