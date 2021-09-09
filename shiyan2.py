# -*- coding: utf-8 -*-
"""
Created on Wed Jun  9 19:36:26 2021

@author: lixiang
"""
import numpy as np
import pandas as pd
from datetime import datetime
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans #导入kmeans算法
import matplotlib.pyplot as plt

data = pd.read_csv("D:/QQ文件/python/实验2代码/任务程序/data/air_data.csv",
    encoding="gb18030") #读取原始数据
print('原始数据:',data)
##探索性数据分析
explore = data.describe(percentiles=[], include = 'all').T#对数据的基本描述
explore['null'] = len(data) - explore['count']#手动计算空值数

explore = explore[['null', 'max', 'min']]
explore.columns = [u'空值数',u'最大值',u'最小值']#表头重命名

explore.to_excel('D:/QQ文件/python/实验2代码/任务程序/tmp/explore.xls')#导出结果
print('探索性数据:',explore)
##数据预处理

##数据清洗
data = data[data['SUM_YR_1'].notnull()&data['SUM_YR_2'].notnull()] # 票价非空值才保留
#只保留票价非零的,或者平均折扣率与总飞行公里数同时为0的记录

index1 = data['SUM_YR_1'] != 0
index2 = data['SUM_YR_2'] != 0
index3 = (data['SEG_KM_SUM']> 0) & \
    (data['avg_discount'] != 0)  
data = data[(index1 | index2) & index3]

##属性规约,分别是观测结束时间,入会时间,距离最近一次飞行的时间,飞行次数,飞行距离,平均折扣
data_select = data[['LOAD_TIME', 'FFP_DATE', 'LAST_TO_END', 'FLIGHT_COUNT', 'SEG_KM_SUM', 'avg_discount']]
print('数据清洗后的数据：',data_select)

##提取LRFMC五个指标
## 构建L特征
L = pd.to_datetime(data_select["LOAD_TIME"]) - \
pd.to_datetime(data_select["FFP_DATE"])

L = L.astype("str").str.split().str[0]

L = L.astype("int")/30
## 合并特征
data_features = pd.concat([L,
    data_select.iloc[:,2:]],axis = 1)
#print(data_features)

data_select = data_features.rename(columns = {0:'L','LAST_TO_END': 'R','FLIGHT_COUNT':'F','SEG_KM_SUM':'M','avg_discount':'C'})
#print(data_select)
data_selected=data_select[['L','R','F','M','C']]
print('提取LRFMC特征后的数据:',data_selected)
#data_selected.to_excel('D:/QQ文件/python/实验2代码/任务程序/data/zscoredata.xls')

##标准化
data = StandardScaler().fit_transform(data_select)
print('标准化后的数据:',data)
np.savez('D:/QQ文件/python/实验2代码/任务程序/tmp/airline_scale.npz',data)

##模型构建

##客户聚类
airline_scale = np.load('D:/QQ文件/python/实验2代码/任务程序/tmp/airline_scale.npz')['arr_0']
k = 5                       #需要进行的聚类类别数
#构建模型
kmeans_model = KMeans(n_clusters = k,n_jobs=4,random_state=123)
fit_kmeans = kmeans_model.fit(airline_scale)   #模型训练

print(kmeans_model.cluster_centers_) #查看聚类中心

print(kmeans_model.labels_) #查看样本的类别标签
#简单打印结果
s = pd.Series(['客户群1','客户群2','客户群3','客户群4','客户群5'], index=[0,1,2,3,4]) #创建一个序列s
#print(s)
r1 = pd.Series(kmeans_model.labels_).value_counts() #统计各个类别的数目
#print(r1)
r2 = pd.DataFrame(kmeans_model.cluster_centers_) #找出聚类中心
#print(r2)
r = pd.concat([s,r1,r2], axis = 1) #横向连接（0是纵向），得到聚类中心对应的类别下的数目
r.columns =[u'聚类名称'] + [u'聚类个数'] + [u'ZL'] + [u'ZR']+ [u'ZF']+ [u'ZM']+ [u'ZC']
print('聚合后的数据:\n',r)

##客户价值分析
def plot_radar(data):
    '''
    the first column of the data is the cluster name;
    the second column is the number of each cluster;
    the last are those to describe the center of each cluster.
    '''
    n = len(data[0])
    kinds = ['客户群1','客户群2','客户群3','客户群4','客户群5']
    colors = ['black','r','lawngreen','dodgerblue','aqua']
    lines = ['-','--',':','-.','--']
    labels = ['ZL(入会时间)','ZR(最近一次飞行)','ZF(飞行次数)','ZM(飞行里程)','ZC(平均折扣系数)','ZL(入会时间)']
    centers = pd.DataFrame(data)
    centers = pd.concat([centers.iloc[:,:],centers.iloc[:,0]],axis = 1)
    centers = np.array(centers)

    angles = np.linspace(0,2 * np.pi,n,endpoint = False)
    angles = np.concatenate((angles,[angles[0]]))

    fig = plt.figure()
    ax = fig.add_subplot(111,polar = True)  #设置坐标为极坐标

    # 画若干个五边形
    floor = np.floor(centers.min())      #大于最小值的最大整数
    ceil = np.ceil(centers.max())        #小于最大值得最小整数
    for i in np.arange(floor,ceil + 0.5,0.5):
        ax.plot(angles,[i] * (n + 1),'--',lw = 0.5,color = 'black')

    # 画不同客户群的分割线
    for i in range(n):
        ax.plot([angles[i],angles[i]],[floor,ceil],'--',lw = 0.5,color = 'black')

    # 画不同的客户群所占的大小
    for i in range(len(kinds)):
        ax.plot(angles,centers[i],lines[i],lw = 2,label = kinds[i],color = colors[i],marker='o')

    ax.set_thetagrids(angles * 180 / np.pi,labels)  #设置显示的角度，将弧度转化为角度
    plt.legend(bbox_to_anchor = (0.8,0.8),fontsize = 11)  #设置图例的位置

    ax.set_theta_zero_location('N')
    ax.spines['polar'].set_visible(False)  # 不显示极坐标最外圈的圆
    ax.grid(False)  #不显示默认的分割线
    ax.set_yticks([])   #不显示坐标间隔
    # 设置字体为楷体
    plt.rcParams['font.sans-serif'] = ['SimHei']
    plt.rcParams['axes.unicode_minus'] = False
    plt.savefig('雷达图.jpg')

data = r[['ZL','ZR','ZF','ZM','ZC']]
data = np.array(data)
data = data.tolist()
print('用来画雷达图的数据:',data)
plot_radar(data)