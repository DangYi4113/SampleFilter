import pandas as pd
import sys

writer_info = '更多问题，可联系作者，邮箱 2592612552@qq.com'

def get_paras(filename='参数表.xlsx'):
    part1 = pd.read_excel(filename,sheet_name='必须填充的')
    part2 = pd.read_excel(filename,sheet_name='样本比较过程中的参数（可不修改）')

    try:
        data_filename = part1['数据表文件名'].iloc[0]
        data_sheetname = part1['数据表sheet名'].iloc[0]
        data_extraline_num = int(part1['数据表开头额外行数（默认为0）'].iloc[0])
    except:
        print('数据表文件名或sheet名 未能正确识别，请核对 参数表.xlsx 文件中的sheet——必须填充的')
        input(writer_info)
        sys.exit(0)
    
    try:
        model_reg = part1['回归模型'].iloc[0]
        method_reg = part1['回归方法'].iloc[0]
    except:
        print('回归模型或回归方法未能正确识别，请核对 参数表.xlsx 文件中的sheet——必须填充的')
        input(writer_info)
        sys.exit(0)
    else:
        if model_reg == '线性回归':
            if not method_reg in ['pinv','qr']:
                method_reg = 'pinv'
        elif model_reg in ['Logit','Probit']:
            if not method_reg in ['newton','nm','bfgs','lbfgs','powell','cg','ncg','basinhopping','minimize']:
                method_reg = 'newton'
    
    try:
        xlist0 = list(part1['自变量'].dropna().drop_duplicates().astype('str'))
    except:
        print('自变量未能正确识别，请核对 参数表.xlsx 文件中的sheet——必须填充的')
        input(writer_info)
        sys.exit(0)
    
    try:
        y_name = part1['因变量'].iloc[0]
    except:
        print('因变量未能正确识别，请核对 参数表.xlsx 文件中的sheet——必须填充的')
        input(writer_info)
        sys.exit(0)
    
    try:
        t_above = list(part1['需要系数为正的自变量'].dropna().drop_duplicates().astype('str'))
        t_below = list(part1['需要系数为负的自变量'].dropna().drop_duplicates().astype('str'))
        p_alpha = list(part1['需要P值足够小的自变量'].dropna().drop_duplicates().astype('str'))
        p_alpha_list = []
        t_above_list = []
        t_below_list = []
        for i in t_above:
            t_above_list.append(xlist0.index(i)+1)
        for i in t_below:
            t_below_list.append(xlist0.index(i)+1)
        for i in p_alpha:
            p_alpha_list.append(xlist0.index(i)+1)
    except:
        print('需要调整的变量 未能正确识别，请核对 参数表.xlsx 文件中的sheet——必须填充的')
        input(writer_info)
        sys.exit(0)
        

    try:
        alpha = part2.iloc[0]['alpha']
        const_dict = {'是':True,'否':False}
        const_bool = const_dict[part2.iloc[0]['是否包含常数项']]
        lr = part2.iloc[0]['初始样本的样本量占总样本比例的下限']
        rr = part2.iloc[0]['初始样本的样本量占总样本比例的上限']
        iteration = int(part2.iloc[0]['每次寻找初始样本时，最大重复次数'])
        N = int(part2.iloc[0]['重复整个过程的批次数'])
        d = int(part2.iloc[0]['输出结果的小数位数'])
    except:
        print('迭代过程中的参数 未能正确识别，请核对 参数表.xlsx 文件中的sheet——默认参数')
        input(writer_info)
        sys.exit(0)
    
    print('''以下参数已经成功识别：
    
    数据表文件：%s；
    Sheet名：%s；
    从这个Sheet的第%d行开始读取数据；
    回归模型：%s；
    回归方法: %s；    
    自变量：%s；
    因变量：%s；
    需要系数为正的自变量：%s；
    需要系数为负的自变量：%s；
    需要P值足够小的自变量：%s；
    
    alpha：%.03f；
    是否包含常数项：%s
    初始样本的样本量占总样本比例的下限：%.03f；
    初始样本的样本量占总样本比例的上限：%.03f；
    每次寻找初始样本时，最大重复次数：%d；
    重复整个过程的批次数：%d；
    结果文件中，回归模型保留的小数位数：%d。''' % (data_filename, data_sheetname, data_extraline_num+1,\
                        model_reg, method_reg, ','.join(xlist0), y_name, \
                        ','.join(t_above), ','.join(t_below), ','.join(p_alpha), \
                        alpha, const_bool, lr, rr, iteration, N, d))
    
    return data_filename,data_sheetname,data_extraline_num,\
            model_reg, method_reg,\
            xlist0,y_name,t_above_list,t_below_list,p_alpha_list, \
            alpha,const_bool,lr,rr,iteration,N,d