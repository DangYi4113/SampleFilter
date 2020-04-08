import numpy as np 
import pandas as pd
import random
import statsmodels.api as sm
#下面这两行是为了不显示warnings
import warnings
warnings.filterwarnings('ignore')

model_dict = {'线性回归':sm.OLS,'Logit':sm.Logit,'Probit':sm.Probit}
B_dict = {'线性回归':'t','Logit':'z','Probit':'z'}

global issuccess
issuccess = False
global issuccess_all
issuccess_all = False

def sig_t(X,y,model_reg,method_reg,p_alpha_list,t_above_list,t_below_list,alpha=0.05):
    #这个函数是每次都需要改的
    MyReg = model_dict[model_reg]
    regt = MyReg(y,X)
    result = regt.fit(method=method_reg, disp=False).summary2().tables[1]
    #if regt.isfit==False:
        #return False
        #尚不明确，采用了statsmodels之后，怎么判断回归是否成功
        
    for t in p_alpha_list:
        if result.iloc[t]['P>|%s|'%B_dict[model_reg]]>=alpha:
            return False
    for t in t_above_list:
        if result.iloc[t][B_dict[model_reg]]<=0:
            return False
    for t in t_below_list:
        if result.iloc[t][B_dict[model_reg]]>=0:
            return False
    return True

#1. choice_step1，这个函数用来在整个样本中找到较小的一个子样本
#2. choice_step2，在choice_step1结果的基础上，找到尽可能大的一个子样本
#3. choice_step3，重复进行choice_step1和choice_step2，找到尽可能大的子样本

#运行choice_step2前必须运行choice_step1。
#运行choice_step3前不一定先运行choice_step1和choice_step2，因为choice_step3里会从头开始计算

def choice_step1(X,y,model_reg,method_reg,p_alpha_list,t_above_list,t_below_list,alpha=0.05,iteration=10000,lr=0.2,rr=0.6):
    l = len(X)
    l1 = int(l*lr)
    l2 = int(l*rr)
    s = random.randint(l1, l2)
    index1 = random.sample(list(X.index),s)
    XN = X.loc[index1]
    yN = y.loc[index1]
    t=1
    global issuccess
    issuccess = False
    while (not issuccess) and t<=iteration:
        t+=1
        if t%(iteration//10)==0:
            print("\t进行了%d次尝试" %t)
        s = random.randint(l1, l2)
        index1 = random.sample(list(X.index),s)
        XN = X.loc[index1]
        yN = y.loc[index1]
        if sig_t(XN,yN,model_reg,method_reg,p_alpha_list,t_above_list,t_below_list,alpha):
            flag = True
            #print('当前批次共%d个样本，该样本符合要求。共进行了%d次迭代'%(len(index1),t))
            print('共进行了%d次迭代，找到了一个可行的样本'%t)
            issuccess=True
            global issuccess_all
            issuccess_all=True
        if t>iteration and issuccess==False:
            print('当前批次迭代次数超过上限。共进行了%d次迭代。\n这批样本尝试未成功，不可用'%iteration)
            break
    return index1

def choice_step2(X,y,index1,model_reg,method_reg,p_alpha_list,t_above_list,t_below_list,alpha=0.05,whether_print=False):
    index2 = X.index.drop(index1)
    #print('初始子样本包含%d个样本' % len(index1))
    for j in index2:
        indexj = index1.copy()
        indexj.append(j)
        XN = X.loc[indexj]
        yN = y.loc[indexj]
        if sig_t(XN,yN,model_reg,method_reg,p_alpha_list,t_above_list,t_below_list,alpha):
            index1 = indexj
            if whether_print:
                print('\t加入了序号为%d的样本' % j)
    print('原始数据中，样本量为%d'%len(y))
    print('这批样本中，最终保留下来的样本量为%d'%len(index1))
    return index1

def choice_step3(X,y,model_reg,method_reg,p_alpha_list,t_above_list,t_below_list,alpha=0.05,lr=0.2,rr=0.6,iteration=10000,N=5):
    #iteration是每次寻找初始样本时，最大重复次数
    #lr是初始样本的样本量占总样本比例的下限
    #rr是初始样本的样本量占总样本比例的上限
    #N是重复整个过程的次数
    index_final = []
    index_len = 0
    j = 0
    for k in range(N):
        print('\n开始寻找第%d批子样本：'%(k+1))
        global issuccess
        issuccess = False
        index1 = choice_step1(X,y,model_reg,method_reg,p_alpha_list,t_above_list,t_below_list,alpha,iteration,lr,rr)
        if issuccess:
            index2 = choice_step2(X,y,index1,model_reg,method_reg,p_alpha_list,t_above_list,t_below_list,alpha)
            if len(index2)>index_len:
                if k>0:
                    print('第%d批子样本比之前的样本量大\n' % (k+1))
                j = k+1
                index_final = index2
                index_len = len(index2)
            else:
                if k>0:
                    print('第%d批子样本并不比之前的样本量大\n' % (k+1))
        else:
            print('第%d批的%d次尝试均不成功，结果不可用'%(k+1,iteration))
    global issuccess_all
    if issuccess_all:
        print('第%d批子样本的样本量最大，共%d个样本' % (j,index_len))
        return index_final
    else:
        print('%d批尝试均不成功，可以增加迭代次数再试，或者修改模型' %N)
        return None