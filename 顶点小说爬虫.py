# -*- coding: utf-8 -*-
"""
Created on Thu May 27 22:24:31 2021

@author: lixiang
"""

import requests
import re

def getHtMLText(url):
    try:
        r = requests.get(url, timeout = 30)
        r.raise_for_status()
        r.encoding = r.apparent_encoding
        return r.text
    except:
        return "发生异常"

def compare_catalogue(html):
    pattern = re.compile('<td class="L"><a href="(.*?)">(.*?)</a></td>.*?',re.S)  
    item = re.findall(pattern, html)
    return item 

def compare_text(html):
    pattern = re.compile('<dd id="contents">&nbsp;&nbsp;&nbsp;&nbsp;(.*?)</dd>|<dd id="contents">',re.S)  
    item = re.findall(pattern, html)
    return item
 
#print(type(compare_text(getHtMLText('https://www.e1w.net/read/5403/5100808.html'))[1]))

def main():
    url1 = 'https://www.e1w.net/read/5403/index.html'
    list = compare_catalogue(getHtMLText(url1))
#    print(list)
#    text = getHtMLText('https://www.e1w.net/read/5403/'+list[0][0])
#    t = compare_text(text)
#    patterns = re.compile('(.*?)<br />\r\n<br />\r\n&nbsp;&nbsp;&nbsp;&nbsp;')
#    items = re.findall(patterns,t[0])
#    print(items)
    for i in list:
        url = 'https://www.e1w.net/read/5403/'+i[0]
        mid_data = compare_text(getHtMLText(url))
        patterns = re.compile('(.*?)<br />\r\n<br />\r\n&nbsp;&nbsp;&nbsp;&nbsp;')
        data = re.findall(patterns,mid_data[0])          
        with open ('D://QQ文件//python//电子书//反叛的大魔王//'+i[1].split(' ')[0]+' .txt','w',encoding = 'utf-8') as f:            
            for j in range(len(data)):
                f.write('  '+data[j]+'\n')
        f.close()
    print('导入成功')
        
if __name__ == '__main__':
    main()