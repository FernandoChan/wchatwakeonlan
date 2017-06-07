#!/usr/bin/python
# -*- coding: utf-8 -*-
import itchat
import paramiko
import os
import time
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

hostname = ''
username = ''
port =  
key_file = '/home/fangwenjun/.ssh/id_rsa'
filename = '/home/fangwenjun/.ssh/known_hosts'

@itchat.msg_register(itchat.content.TEXT)
def text_reply(msg):
	if msg['ToUserName'] != 'filehelper': return
	if msg['Text'] ==  u'开机':
		ssh_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) 
		itchat.send(ssh_time+u'开始连接远程主机', toUserName='filehelper')
		paramiko.util.log_to_file('ssh_key-login.log')
		privatekey = os.path.expanduser(key_file) 
		try:
		    key = paramiko.RSAKey.from_private_key_file(privatekey)
		except paramiko.PasswordRequiredException:
		    key = paramiko.RSAKey.from_private_key_file(privatekey,key_file_pwd)
		 
		ssh = paramiko.SSHClient()
		ssh.load_system_host_keys(filename=filename)
		ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
		ssh.connect(hostname=hostname,username=username,pkey=key,port=port)
		#执行唤醒命令
		stdin,stdout,stderr=ssh.exec_command('wakeonlan -i 192.168.1.0 14:dd:a9:ea:0b:96')
		print stdout.read()
		wakeonlan_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) 
		itchat.send(wakeonlan_time+u'执行唤醒，等待设备开机联网', toUserName='filehelper')
		#由于开机需要一些时间去启动网络，所以这里等等15s
		time.sleep(15)
		#执行 ping 命令，-c 1 表示只 ping 一下，然后过滤有没有64，如果有则获取64并转换为 int 类型传给sshConStatus
		stdin,stdout,stderr=ssh.exec_command('ping 192.168.1.182 -c 1 | grep 64 | cut -b 1,2')
		sshConStatus = stdout.read()
		#进行判断，如果为64，则说明 ping 成功，设备已经联网，可以进行远程连接了，否则发送失败消息
		if sshConStatus !=' ':
			connect_ok_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) 
			itchat.send(connect_ok_time+u'设备唤醒成功，您可以远程连接了', toUserName='filehelper')
		else:
			connect_err_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
			itchat.send(connect_err_time+u'设备唤醒失败，请检查设备是否连接电源', toUserName='filehelper')
		ssh.close()
		os.system('touch /www/shutdown')
		print '执行开机消息成功'

	if	msg['Text'] ==  u'关机':
		rmfile = os.system('rm -rf /www/shutdown')
		if rmfile == 0:
			print '执行关机消息成功'
		shutdown_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) 
		itchat.send(shutdown_time+u'正在关机....', toUserName='filehelper')
		paramiko.util.log_to_file('ssh_key-login.log')
		privatekey = os.path.expanduser(key_file) 
		try:
		    key = paramiko.RSAKey.from_private_key_file(privatekey)
		except paramiko.PasswordRequiredException:
		    key = paramiko.RSAKey.from_private_key_file(privatekey,key_file_pwd)
		 
		ssh = paramiko.SSHClient()
		ssh.load_system_host_keys(filename=filename)
		ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
		ssh.connect(hostname=hostname,username=username,pkey=key,port=port)
		itchat.send(shutdown_time+u'正在确认设备是否完成关机操作，大约需要等待60s.', toUserName='filehelper')
		time.sleep(10)
		stdin,stdout,stderr=ssh.exec_command('ping 192.168.1.182 -c 1 | grep 64 | cut -b 1,2')
		sshConStatus = stdout.read()
		if int(sshConStatus) != 64:
			shutdown_success_err_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
			itchat.send(shutdown_success_err_time+u'关机成功', toUserName='filehelper')
		else:
			shutdown_err_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) 
			itchat.send(shutdown_err_time+u'关机失败，请连接桌面检查客户端程序是否正常执行', toUserName='filehelper')

			
		ssh.close()
itchat.auto_login(hotReload=True,enableCmdQR=2)
itchat.run()