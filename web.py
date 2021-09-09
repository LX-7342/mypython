# -*- coding: utf-8 -*-
"""
Created on Mon May 31 22:43:58 2021

@author: lixiang
"""

# Import socket module
from socket import * 
import sys 

serverSocket = socket(AF_INET, SOCK_STREAM)

serverPort = 9998

serverSocket.bind(("", serverPort))

serverSocket.listen(1)

# 服务器持续启动运行，并侦听传入的连接
while True:
	print('The server is ready to receive')

# 一直进行监听，如果客户端进行连接，相应并建立来自客户端的新连接
	connectionSocket, addr = serverSocket.accept()

	try:
		# 接受客户端的请求信息
		message = connectionSocket.recv(1024).decode()
		# 从消息（请求报文）中提取所请求对象的路径（URL）
		filename = message.split()[1]
		# 由URL的一般形式，需要从第二个字符读取路径。
		f = open(filename[1:])
		# 将请求文件的全部内容存储在临时缓冲区中
		outputdata = f.read()
		# 将HTTP响应标头行发送到连接套接字
		connectionSocket.send("HTTP/1.1 200 OK\r\n\r\n".encode()) 
 
		# 将请求文件的内容发送到连接套接字
		for i in range(0, len(outputdata)):  
			connectionSocket.send(outputdata[i].encode())
		connectionSocket.send("\r\n".encode()) 
    
		connectionSocket.close()

	except IOError:
			# 发送未找到文件的HTTP响应消息
			connectionSocket.send("HTTP/1.1 404 Not Found\r\n\r\n".encode())
			connectionSocket.send("<html><head></head><body><h1>404 Not Found</h1></body></html>\r\n".encode())
			connectionSocket.close()

serverSocket.close()  
sys.exit()#发送相应数据后终止程序

