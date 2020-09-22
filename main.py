
import queue
import threading
import jieba
import time
import re
import math
import multiprocessing

'''
项目概述：
实现文章查重功能，给出两篇文章相似的百分比（精确到小数点后两位）
同时为了性能优先，使用多进程编程
支持读入的文本格式：.txt文件。

项目开始日期：2020/9/20
ver：1.3
auther：White0PS

'''

class diff_find:

    def __check_file(self,f1,f2):
        ext1 = f1[f1.rfind('.'):]    #不能使用index方法，该方法会查找子串第一次出现的地方。使用rfind方法。
        ext2 = f2[f2.rfind('.'):]

        if ext1 in ['.txt'] and ext2 in ['.txt']:
            try:
                file1_content= open(f1,encoding='utf-8').read()
                file2_content = open(f2,encoding='utf-8').read()   #在此处进行文本预处理。将文本中包含的符号、非汉字进行去除。
                self.__f1 =  re.findall('[\u3002\uff1b\uff0c\uff1a\u201c\u201d\uff08\uff09\u3001\uff1f\u300a\u300b\u4e00-\u9fa5]',file1_content)
                self.__f2 = re.findall(
                    '[\u3002\uff1b\uff0c\uff1a\u201c\u201d\uff08\uff09\u3001\uff1f\u300a\u300b\u4e00-\u9fa5]',
                    file2_content)
                self.__f1 = ''.join(self.__f1)
                self.__f2 = ''.join(self.__f2)
                return 1


            except:#文件无法打开，文件上传失败。
                print('[-]文件有误！')
                print('[-]exiting!')
                return 0

        else:
            print("[-]文件输入不通过！")
            print("[-]Exiting!")
            return 0


    def f_open(self,first_file,second_file):
        if(self.__check_file(first_file,second_file)):

            take_time,rate = self.__analysis(self.__f1,self.__f2)
            if rate>0.15:
                print('\033[31m',end='')
                print("[*]重复率为：%.2f" %(rate*100)+'%')
                print('\033[33m',end='')
                print('[*]所用时间：%.2f' %take_time+'s')
            else:
                print('\033[32m',end='')
                print("[*]重复率为：%.2f" % (rate * 100) + '%')
                print('\033[33m', end='')
                print('[*]所用时间：%.2f' % take_time + 's')

            return



    def __analysis(self,text1,text2):#该函数应当返回：查重率。
        return_list = []
        t1 = time.time()
        word_ls1 =jieba.lcut(text1)
        word_ls2 = jieba.lcut(text2)
        word_ls1 = [i for i in word_ls1 if i not in ('', '，', '、', '-', '“', '”', '：','。')]  # 去除特殊符号
        word_ls2 = [i for i in word_ls2 if i not in ('', '，', '、', '-', '“', '”', '：','。')]
        dict = {}
        same_words = 0
        for w in word_ls1:
            dict[w] = dict.get(w,0)+1
        #print(dict)
        for w in word_ls2:
            try:
                if (dict[w]):
                    same_words+=1
            except:
                pass
        t2 = time.time()
        take_time = t2-t1
        return_list.append(take_time)
        rate = same_words/len(word_ls1)
        return_list.append(rate)
        return return_list



if __name__ =='__main__':
    file_ob = diff_find()
    file_ob.f_open(r'C:\Users\wu\Desktop\method\test\orig.txt',r'C:\Users\wu\Desktop\method\test\orig_0.8_del.txt')