
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
ver：1.0
auther：White0PS

日志：
9/21：
完成的功能：
1、多线程以句为单位查重；
2、基本函数（-v命令参数）的写成。
3、字体颜色标识

9/22（14：30-16：38）：
尝试的功能：
1、多进程任务
2、文章清洗
认识到的问题：
1、并不是所有的任务都使用多进程或者是多线程去完成。当任务数量较少的时候，使用单进程单线程完全够用，时间差异并不大。由此，我们明确，当且仅当进行爬虫任务，暴力破解、盲注攻击、协议毒害攻击、条件竞争的时候，才会使用多线程或多进程
2、文本清洗的必要性

接下来的方向：
剔除文件中不需要的部分（多进程和多线程部分），留下核心部分，然后编写测试模块，进行测试，然后上交。
'''

class diff_find:

    def __init__(self,thread_num,cmd_mode):
        self.thread_num = thread_num
        self.mode = cmd_mode
        self.queue_ob = queue.Queue()
        self.cpu_num = multiprocessing.cpu_count()

    def __check_file(self,f1,f2):
        ext1 = f1[f1.rfind('.'):]    #不能使用index方法，该方法会查找子串第一次出现的地方。使用rfind方法。
        ext2 = f2[f2.rfind('.'):]
        #print(ext1,ext2)
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
                print(self.__f1)
                print(self.__f2)
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
        t1 = time.time()
        if(self.__check_file(first_file,second_file)):
            line_list1 = self.__f1.split("。")
            line_list2 = self.__f2.split("。")   #对文章进行分句之后的结果，列表元素是一个个句子
            task_num = max(len(line_list1),len(line_list2))  #给各个线程分配任务
            if self.mode =='-v':
                task_range = math.ceil(task_num/self.thread_num) #math.ceil()向上取整，拿到每个线程需要处理的句子个数。
                for i in range(self.thread_num):

                    thread = threading.Thread(target=self.complex_analysis,args=(line_list1[i*task_range:(i+1)*task_range],line_list2[i*task_range:(i+1)*task_range]))
                    thread.start()
                    thread.join()
            elif self.mode =='-p': #使用多进程再次进行尝试，此时多进程方式是：给每个子进程分配一定的拆分句子数量，就如同多线程一样，同时使用pool进行进程调度
                task_range = math.ceil(task_num/self.cpu_num)
                for i in range(self.cpu_num):#不使用pool的原因：无法通过变量来分配任务区间
                    process_ob = multiprocessing.Process(target=self.complex_analysis,args=(line_list1[i*task_range:(i+1)*task_range],line_list2[i*task_range:(i+1)*task_range]))
                    process_ob.run()
            elif self.mode == '-m':
                rate = self.__analysis(self.__f1,self.__f2)
                print("查重率为：%.2f" %rate)
                return

            line_num = 0
            queue_size = self.queue_ob.qsize()
            for i in range(queue_size):
                line_num += self.queue_ob.get()
            mark = line_num/queue_size
            t2 = time.time()
            if mark>0.15:
                print('\033[1;31;40m')
                print('*'*30)
                print('查重率为：%.2f' %mark)
                print('查重所用时间：%.2f' %(t2-t1))
                print('*' * 30)
            else:
                print('\033[1;32;42m')
                print('*'*30)
                print('查重率为：%.2f' %mark)
                print('查重所用时间为：%.2f' %(t2-t1))
                print('*' * 30)
            return

        else:
            return 0

    def complex_analysis(self,line_list1,line_list2):#传入的line_list是一个分片之后的列表，列表元素为字符串（一句一句话）
        if len(line_list1) ==len(line_list2):#当分配的任务相同的时候（即比较的两个列表中句子）
            list_length = len(line_list1)
            for i in range(list_length):
                same_words = 0
                word_list1 = jieba.lcut(line_list1[i])#分词
                word_list2 = jieba.lcut(line_list2[i])
                word_dict = {} #词频字典，词语每出现一次则词语对应的键值+1
                word_list1 = [i.strip() for i in word_list1] #对分词后的列表，去除其中的换行。
                word_list2 = [i.strip() for i in word_list2]
                word_list1 = [ i for i in word_list1 if i not in ('','，','、','-','“','”','：')]  #去除特殊符号
                word_list2 = [i for i in word_list2 if i not in ('','，','、','-','“','”','：')]
                word_num = len(word_list1)
                if word_num ==0:   #可能是句子中仅有特殊符号，当特殊符号去掉之后列表就变成空了
                    continue
                print('\033[32m[*]比较的两个句子：')
                print('\033[34m')
                print(line_list1[i])
                print('\033[33m')
                print(line_list2[i])
                print('\033[0m')
                for word in word_list1:
                    word_dict[word] = word_dict.get(word,0)+1
                print("\033[0m|"+"="*len(line_list1)+"|")
                print("\033[0m重复的词语有：",end='')
                for word in word_list2:
                    try:
                        if (word_dict[word]):  #如果能够在由第一句所生成的词频字典中找到第二个句子中的词，那显然就是重复了。
                            print(word,end=',')
                            same_words +=1
                    except:
                        pass
                print("\n重复的词数："+str(same_words))
                rate = same_words/word_num
                print("两个句子的重复率：%.2f" %rate)
                print("|" + "=" * len(line_list1) + "|")
                print("\n")
                self.queue_ob.put(rate)   #由于是往队列中写数据，而不是操作数据，因此不需要使用lock（）方法。

    def __analysis(self,text1,text2):#该函数应当返回：查重率。
        word_ls1 =jieba.lcut(text1)
        word_ls2 = jieba.lcut(text2)
        word_ls1 = [i for i in word_ls1 if i not in ('', '，', '、', '-', '“', '”', '：','。')]  # 去除特殊符号
        word_ls2 = [i for i in word_ls2 if i not in ('', '，', '、', '-', '“', '”', '：','。')]
        dict = {}
        same_words = 0
        for w in word_ls1:
            dict[w] = dict.get(w,0)+1
        print(dict)
        for w in word_ls2:
            try:
                if (dict[w]):
                    same_words+=1
            except:
                pass
        rate = same_words/len(word_ls1)
        return rate









if __name__ =='__main__':
    file_ob = diff_find(5,'-m')
    file_ob.f_open(r'C:\Users\wu\Desktop\method\test\orig.txt',r'C:\Users\wu\Desktop\method\test\orig_0.8_del.txt')