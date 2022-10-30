import innodb_status_tool
import innodb_status_display
import argparse
import sys
#coll_instance = innodb_status_tool.innodb_status_collector(file='/tmp/innodb_status.txt')
#print(coll_instance.get_innodb_status_str())
#print(coll_instance.is_ok())

def _argparse():
	parser = argparse.ArgumentParser(add_help=False, description='mysql innodb status analyze. only for version 5.7 and 8.0')
	parser.add_argument('--help', '-H',  action='store_true', dest='helps', default=False, help='查看帮助')
	parser.add_argument('--version', '-v', '-V', action='store_true', dest="VERSION", default=False,  help='VERSION')
	parser.add_argument('--host', '-h',  action='store', dest='HOST', help='MYSQL服务器地址')
	parser.add_argument('--port', '-P' ,  action='store', dest='PORT',type=int, help='MYSQL服务器端口')
	parser.add_argument('--user', '-u' ,  action='store', dest='USER',  help='MYSQL用户')
	parser.add_argument('--password', '-p' ,  action='store', dest='PASSWORD',   help='MYSQL用户的密码')
	parser.add_argument('--socket', '-S' ,  action='store', dest='SOCKET',   help='mysql unix socket')
	parser.add_argument('--file', '-f' , required=False, type=argparse.FileType('r'),default=sys.stdin, dest='FILE',  help='要解析的innodb_status.txt文件')
	parser.add_argument('--type', '-t' ,  dest='TYPE', choices=['simple', 'html', 'csv'],default='simple', help='输出类型, 支持simple和html和csv')
	parser.add_argument('--suggestion', '-s',  action='store_true', dest='SUGGESTION', default=False, help='显示建议')


	if parser.parse_args().helps:
		parser.print_help()
		sys.exit(0)

	elif parser.parse_args().VERSION:
		print("VERSION: v0.1")
		sys.exit(0)

	else:
		return parser.parse_args()


if __name__ == '__main__':
	parser = _argparse()
	#print(parser.FILE.read())
	#print(parser.TYPE)

	if (parser.HOST is not None) or (parser.PORT is not None) or (parser.USER is not None) or (parser.PASSWORD is not None):
		coll_instance = innodb_status_tool.innodb_status_collector(host=parser.HOST,port=parser.PORT,password=parser.PASSWORD,user=parser.USER) 
		if coll_instance.is_ok():
			innodb_status_str = coll_instance.get_innodb_status_str()
		else:
			sys.exit(1)

	else:
		innodb_status_str = parser.FILE.read()




	
	format_str = innodb_status_tool.innodb_status_format(innodb_status_str)
	format_str.set_all()
		#print(format_str.get_innodb_status_dict())
	innodb_status_dict = format_str.get_innodb_status_dict()

	if parser.SUGGESTION:
		suggestion_instance = innodb_status_tool.innodb_status_suggestion(innodb_status_dict)
		suggestion_instance.suggestion_all()
		suggestion = suggestion_instance.get_suggestion()
	else:
		suggestion = None
	
	
	display = innodb_status_display.display(innodb_status_dict=innodb_status_dict,suggestion=suggestion)
	#print('死锁:',innodb_status_dict['dead_lock'])
	#print('事务:',innodb_status_dict['transactions']['sumary'])
	#print('事务:',innodb_status_dict['transactions']['trx_list'])
	#for x in innodb_status_dict['transactions']['trx_list']:
	#	if x['sql'] != '':
	#		print(x['sql'])
	if parser.TYPE == 'simple':
		display.simple()
	elif parser.TYPE == 'html':
		display.html()
	elif parser.TYPE == 'csv':
		display.json()
	else:
		print("未知类型:",parser.SUGGESTION)
	
