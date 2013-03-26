# coding=utf-8
import datetime, time
import codecs

def timegap(time1):
	#intime = time.strptime(intimestr, "%Y-%m-%d %H:%M:%S")
	# 参数中带*指把列表分解成多个参数
	#函数定义中使用*表示传递任意多的参数
	#函数定义中使用**表示传递任意多键值对
	#time1 = datetime.datetime(*intime[:6])
	time2 = datetime.datetime.now()
	delta = time2-time1
	retstr = u''
	if delta.days>0:
		retstr=u'%d天前' % delta.days
	elif delta.seconds>=3600:
		retstr=u'%d小时前' % (delta.seconds/3600)
	elif delta.seconds>=60:
		retstr=u'%d分钟前' % (delta.seconds/60)
	else:
		retstr=u'%d秒前' % (delta.seconds)
	return retstr

def fileread(filename):
	file = codecs.open('static/test/'+filename, 'r', 'utf8')
	flag = ''
	line = file.readline()
	title = ''
	questions = []
	options = []
	opt_scores = []
	calculate = []
	result = {}
	symptoms = []
	while line:
		line = line[:-1]
		if line.startswith('title:'):
			flag='title'
		elif line.startswith('questions:'):
			flag='questions'
		elif line.startswith('options:'):
			flag = 'options'
		elif line.startswith('calculate:'):
			flag = 'calculate'
		elif line.startswith('result:'):
			flag = 'result'
		else:
			if flag=='title':
				title = line
			elif flag=='questions':
				splitlist = line.split('(')
				questions.append(splitlist[0])
				symptoms.append(splitlist[1][:-1])
			elif flag=='options':
				if line.isdigit():
					opt_scores.append(int(line))
				else:
					options.append(line)
			elif flag=='calculate':
				pos = line.index('=')
				calculate.append(line[(pos+1):])
			elif flag=='result':
				splitlist = line.split(' ')
				result[splitlist[0]] = splitlist[1]
			else:
				pass
		line = file.readline()
	return dict(title=title, questions=questions, opt_scores=opt_scores, options=options, calculate=calculate, result=result, symptoms=symptoms)

if __name__ == "__main__":
	contentmap = fileread('20130223222650')
	for key in contentmap:
		print key, contentmap[key]

