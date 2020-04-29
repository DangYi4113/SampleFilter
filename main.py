print('\n程序准备中，请稍候。。。。。。')

import sys

import pandas as pd
import time

print('\n开始识别所设定的参数，请稍候。。。。。。')
from get_paras import get_paras

data_filename,data_sheetname,data_extraline_num,\
model_reg, method_reg,\
xlist0,y_name,t_above_list,t_below_list,p_alpha_list, \
alpha,const_bool,lr,rr,iteration,N,d = get_paras()

print('\n开始读取数据文件：')

writer_info = '更多问题，可联系作者，邮箱 dangyi4113@foxmail.com'

try:
    data = pd.read_excel(data_filename, sheet_name = data_sheetname, header = data_extraline_num)
except:
    print('\n数据文件读取异常')
    print('可能原因是：数据文件没有和本程序放在同一文件夹下，或者，参数表中所写的文件名或sheet名不准确')
    input(writer_info)
    sys.exit(0)
else:
    print('数据文件已读取\n')
    #print('数据文件包含以下变量：\n%s' %','.join(list(data.columns)))
    try:
        X = data[xlist0]
        #缺一步，未验证是否包含缺失值，以及对缺失值的处理（可以提前把有缺失值的样本输出到一个文件中）
    except:
        print('\n以下自变量名称与数据表文件不完全一致，需要核对\n\t%s'%','.join(xlist0))
        input(writer_info)
        sys.exit(0)
    else:
        print('数据文件中找到了以下自变量：\n%s' %','.join(xlist0))
    try:
        y = data[y_name]
    except:
        print('\n因变量名称 %s 与数据表文件不完全一致，需要核对' % y_name)
        input(writer_info)
        sys.exit(0)
    else:
        print('\n数据文件中找到了因变量：\n%s' % y_name)

time.sleep(3)

print('\n开始尝试：')

import warnings
warnings.filterwarnings('ignore')

from choice_sample import choice_step3
import statsmodels.api as sm

model_dict = {'线性回归':sm.OLS,'Logit':sm.Logit,'Probit':sm.Probit}
MyReg = model_dict[model_reg]
if const_bool:
    X = sm.add_constant(X)  
index1 = choice_step3(X,y,model_reg,method_reg,p_alpha_list,t_above_list,t_below_list,alpha,lr,rr,iteration,N)

time.sleep(3)

print('\n原始数据的回归结果如下：\n')
reg0 = MyReg(y,X)
result_reg0 = reg0.fit(method=method_reg, disp=False)
resultsheets_reg0 = result_reg0.summary2()
print(resultsheets_reg0)
time.sleep(2)
if index1:
    print('\n在最终的子样本中，回归结果如下：\n')
    reg1 = MyReg(y.loc[index1],X.loc[index1])
    result_reg1 = reg1.fit(method=method_reg, disp=False)
    resultsheets_reg1 = result_reg1.summary2()
    print(resultsheets_reg1)
    str_len_list = [len(s) for s in xlist0]
    str_len_max = max(2*max(str_len_list),15)
    float_str0 = '%'+'.'+'%d'%d+'f'
    output_filename = '%soutput.xlsx' % time.strftime('%Y%m%d%H%M%S',time.localtime(time.time()))
    
    writer = pd.ExcelWriter(output_filename)
    #输出1：原始数据
    data.to_excel(writer,'原始数据',index=False)
    #输出2：原始数据回归结果
    row = 0
    t = 0
    for df in resultsheets_reg0.tables:
        flag = False
        if t==1:
            flag = True
        df.to_excel(writer,'原始数据回归结果',startrow=row,float_format=float_str0,index=flag, header=flag)
        row = row+len(df)+2
        t = t+1
    writer.sheets['原始数据回归结果'].column_dimensions['A'].width = str_len_max+2
    #单位width对应excel中列宽8像素
    #输出3：处理后的子样本
    data.loc[index1].to_excel(writer,'处理后的子样本',index=False)
    #输出4：处理后子样本回归结果
    row = 0
    t = 0
    for df in resultsheets_reg1.tables:
        flag = False
        if t==1:
            flag = True
        df.to_excel(writer,'处理后子样本回归结果',startrow=row,float_format=float_str0,index=flag, header=flag)
        row = row+len(df)+2
        t = t+1
    writer.sheets['处理后子样本回归结果'].column_dimensions['A'].width = str_len_max+2
    index2 = data.index.drop(index1)
    #输出5：需要重新收集的子样本
    data.loc[index2].to_excel(writer,'需要重新收集的子样本',index=False)
    writer.save()
    writer.close()
    print('\n处理结果输出在同一文件夹下的 %s 文件里' % output_filename)
    print('当前的处理结果中，原始数据%d个样本留下了%d个。\n\n程序已完成，按Enter键结束。'%(len(data),len(index1)))
    input()
else:
    print('\n程序未能成功得到所需结果。\n\n程序中断，按Enter键结束程序。')
    input(writer_info)
    
