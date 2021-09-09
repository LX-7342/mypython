# -*- coding: utf-8 -*-
"""
Created on Sun May 23 17:17:44 2021

@author: lixiang
"""
import requests
import re
import pymssql
import csv
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import mplfinance.original_flavor
import pandas
import wx
import wx表格展示 as wxb


plt.rcParams['font.family'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False

#得到html
def get_HtML_Text(url):
    try:
        r = requests.get(url, timeout = 30)
        r.raise_for_status()
        r.encoding = r.apparent_encoding
        return r.text
    except:
        return "发生异常"
#匹配到具体数据 
def parse_HTML_Text(html):
    pattern = re.compile('<tr class=.*?><td>(\d+-\d+-\d+)'  #日期
                         +'</td>.*?>(\d+\.\d+)'             #开盘价
                         +'</td>.*?>(\d+\.\d+)'             #最高价
                         +'</td>.*?>(\d+\.\d+)'             #最低价
                         +'</td>.*?>(\d+\.\d+)'             #收盘价
                         +'</td>.*?>(.?\d+\.\d+)'           #涨跌额
                         +'</td>.*?>(.?\d+\.\d+)'           #涨跌幅
                         +'</td>.*?>(\d+,\d+|\d+,\d+,\d+)'  #成交量
                         +'</td>.*?>(\d+,\d+|\d+,\d+,\d+)'  #成交金额
                         +'</td>.*?>(\d+\.\d+)'             #振幅
                         +'</td>.*?>(\d+\.\d+)</td></tr>')  #换手率
    item = re.findall(pattern, html)
    return item          
#将数据存入sqlserver
def insert_data_toSqlserver(item):
     db = pymssql.connect(host='LAPTOP-0TOJ7FM5', user='sa', password='lx101611.', database='myPython')
     if db:
         print("连接成功!")
     try:
         with db.cursor() as cursor:
             sql = 'insert into historicalquote(HDate,HOpen,HHigh,HLow,HClose,Hrf,Hud,HVolume,Hta,Ham,Htr) values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)'
             cursor.executemany(sql,item)
             db.commit()
     finally:
        db.close()
        print('插入成功')
#从sqlserver中访问数据     
def visit_data_fromSqlserver():
    db = pymssql.connect(host='LAPTOP-0TOJ7FM5', user='sa', password='lx101611.', database='myPython')
    if db:
         print("连接成功!")
    data = []
    try:
        with db.cursor() as cursor:
            sql = 'select HDate,HOpen,HHigh,Hlow,HClose,HVolume from historicalquote'
            cursor.execute(sql)
            result_set = cursor.fetchall()
            
            for row in result_set:
                fields = {}
                fields['Date'] = row[0]
                fields['Open'] = float(row[1])
                fields['High'] = float(row[2])
                fields['Low']  = float(row[3])
                fields['Close'] = float(row[4])
                fields['Volume']= row[5]
                data.append(fields)
    finally:
        db.close()
        print('查询成功')
    return data
#画K线图
def show_k():
    data = visit_data_fromSqlserver()

    # 列名
    colsname = ['Date', 'Open', 'High', 'Low', 'Close', 'Volume']
    # 临时数据文件名
    datafile = 'temp.csv'
    # 写如数据到临时数据文件
    with open(datafile, 'w', newline='', encoding='utf-8') as wf:
        writer = csv.writer(wf)
        writer.writerow(colsname)
        for quotes in data:
            row = [quotes['Date'], quotes['Open'], quotes['High'],
                   quotes['Low'], quotes['Close'], quotes['Volume']]
            writer.writerow(row)

    # 调用绘图函数
    pot_candlestick_ohlc(datafile) 
def pot_candlestick_ohlc(datafile):
    """绘制K线图"""

    # 从CSV文件中读入数据DataFrame数据结构中
    quotes = pandas.read_csv(datafile,
                             index_col=0,
                             parse_dates=True,
                             infer_datetime_format=True)

    # 绘制一个子图，并设置子图大小
    fig, ax = plt.subplots(figsize=(10, 5))
    # 调整子图参数SubplotParams
    fig.subplots_adjust(bottom=0.2)

    mplfinance.original_flavor.candlestick_ohlc(ax, zip(mdates.date2num(quotes.index.to_pydatetime()),
                                         quotes['Open'], quotes['High'],
                                         quotes['Low'], quotes['Close']),
                                 width=1, colorup='r', colordown='g')

    ax.xaxis_date()
    ax.autoscale_view()
    plt.setp(plt.gca().get_xticklabels(), rotation=45, horizontalalignment='right')

    plt.show()
    
class MyFrame(wx.Frame):
    def __init__(self):
        super().__init__(parent=None, title='GUI', size=(300, 200))
        self.Centre()  # 设置窗口居中
        panel = wx.Panel(parent=self)
        b1 = wx.Button(parent=panel, id=10, label='展示表格', pos=(50, 45))
        b2 = wx.Button(parent=panel, id=11, label='展示K线图', pos=(150, 45))
        b2 = wx.Button(parent=panel, id=12, label='关闭窗口', pos=(100, 90))
        # self.Bind(wx.EVT_BUTTON, self.on_click, b1)
        # self.Bind(wx.EVT_BUTTON, self.on_click, id=11)
        self.Bind(wx.EVT_BUTTON, self.on_click, id=10, id2=20)

    def on_click(self, event):
        event_id = event.GetId()
        if event_id == 10:
            wxb.main()
        elif event_id == 11:
            show_k()
        else:
            wx.Exit()
            
            


class App(wx.App):

    def OnInit(self):
        # 创建窗口对象
        frame = MyFrame()
        frame.Show()
        return True

def main():    
    #url = "http://quotes.money.163.com/trade/lsjysj_600050.html"
    url = "http://quotes.money.163.com/trade/lsjysj_600795.html#01b07"
    html = get_HtML_Text(url)
    item = parse_HTML_Text(html)
    #print(item)
    #insert_data_toSqlserver(item)
    #data = visit_data_fromSqlserver()
    app = App()
    app.MainLoop()
    


if __name__ == '__main__':
    main()    