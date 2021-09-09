# coding=utf-8
# 代码文件：chapter19/ch19.7.3-1.py

import wx
import wx.grid
import shiyan1 as sy

item = sy.visit_data_fromSqlserver()
data = []
for i in item:
    temp = []
    temp.append(i['Date'])
    temp.append(str(i['Open']))
    temp.append(str(i['High']))
    temp.append(str(i['Low']))
    temp.append(str(i['Close']))
    temp.append(i['Volume'])
    data.append(temp)

column_names = ['日期', '开盘价', '最高价', '最低价', '收盘价', '成交量']


# 自定义窗口类MyFrame
class MyFrame(wx.Frame):
    def __init__(self):
        super().__init__(parent=None, title='表格', size=(500, 900))
        self.Centre()  # 设置窗口居中
        self.grid = self.CreateGrid(self)
        self.Bind(wx.grid.EVT_GRID_LABEL_LEFT_CLICK, self.OnLabelLeftClick)

    def OnLabelLeftClick(self, event):
        print("RowIdx：{0}".format(event.GetRow()))
        print("ColIdx：{0}".format(event.GetCol()))
        print(data[event.GetRow()])
        event.Skip()

    def CreateGrid(self, parent):
        grid = wx.grid.Grid(parent)
        grid.CreateGrid(len(data), len(data[0]))

        for row in range(len(data)):
            for col in range(len(data[row])):
                grid.SetColLabelValue(col, column_names[col])
                grid.SetCellValue(row, col, data[row][col])
        # 设置行和列自定调整
        grid.AutoSize()

        return grid


class App(wx.App):

    def OnInit(self):
        # 创建窗口对象
        frame = MyFrame()
        frame.Show()
        return True
def main():
    app = App()
    app.MainLoop() 


if __name__ == '__main__':
     # 进入主事件循环
     main()
