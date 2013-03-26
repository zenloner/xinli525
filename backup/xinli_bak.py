# coding=utf-8
import MySQLdb
import datetime
import helper
from werkzeug import secure_filename
from flask import Flask, request, session, g, redirect, url_for, abort, \
     render_template, flash

app = Flask(__name__)
app.debug = True
app.config.from_pyfile('config.cfg', silent=True)

from sae.const import (MYSQL_HOST, MYSQL_HOST_S,
    MYSQL_PORT, MYSQL_USER, MYSQL_PASS, MYSQL_DB
)

PER_PAGE = 4
PER_TOPIC = 6

@app.before_request
def before_request():
    g.db = MySQLdb.connect(MYSQL_HOST, MYSQL_USER, MYSQL_PASS,
                           MYSQL_DB, port=int(MYSQL_PORT), charset='utf8')

@app.teardown_request
def teardown_request(exception):
    if hasattr(g, 'db'): g.db.close()




@app.route('/', defaults={'page':1})
@app.route('/<page>')
def index(page):
	try:
		page = int(page)
	except ValueError:
		page = 1
	st = PER_PAGE*(page-1)
	ed = st+PER_PAGE
	c = g.db.cursor()
	c.execute("select * from paper")
	entries = [dict(id=row[0], title=row[1], description=row[2]) for row in c.fetchall()]
	pageNumber = len(entries)/PER_PAGE+1
	if len(entries) < ed:
		ed = len(entries)
	entries = entries[st:ed]
	return render_template('index.html', entries=entries, pageNumber=pageNumber, page=page, pagetype="paper")

@app.route('/paper')
def paper():
	paper_id = request.args['id']
	c = g.db.cursor()
	c.execute("select * from paper where paper_id=%s", paper_id)
	row = c.fetchone()
	entry = dict(id=row[0], title=row[1], description=row[2], content=row[3])
	return render_template('paper.html', entry=entry, pagetype="paper")


@app.route('/pic', defaults={'page':1})
@app.route('/pic/<page>')
def pic(page):
	try:
		page = int(page)
	except ValueError:
		page = 1
	st = PER_PAGE*(page-1)
	ed = st+PER_PAGE
	c = g.db.cursor()
	c.execute("select * from picture")
	entries = [dict(id=row[0], title=row[1], description=row[2]) for row in c.fetchall()]
	pageNumber = len(entries)/PER_PAGE+1
	if len(entries) < ed:
		ed = len(entries)
	entries = entries[st:ed]
	return render_template('pic.html', entries=entries, pageNumber=pageNumber, page=page, pagetype="pic")

@app.route('/picview')
def picview():
	pic_id = request.args['id']
	c = g.db.cursor()
	c.execute("select * from picture where pic_id=%s", pic_id)
	row = c.fetchone()
	entry = dict(id=row[0], title=row[1], description=row[2], content=row[3])
	return render_template('picview.html', entry=entry, pagetype="pic")


@app.route('/register', methods=['GET', 'POST'])
def register():
	#TODO 使用ajax的方式提示错误
	if request.method == 'POST':
		username = request.form['username']
		password = request.form['password']
		confirm = request.form['confirm']
		email = request.form["email"]
		c = g.db.cursor()
		c.execute("select * from user where username=%s", username)
		rows = c.fetchall()
		if username==None or username=="" or password==None or password=="" or email==None or email=="":
			return render_template('register.html', error=True, message=u'字段不能为空')
		elif len(rows) != 0:
			return render_template('register.html', error=True, message=u'用户名已经被注册')
		elif password != confirm:
			return render_template('register.html', error=True, message=u'两次输入的密码不一样')
		else:
			c.execute("insert into user(username, password, email) values (%s, %s, %s)", (username, password, email))
			g.db.commit()
			session['login'] = True
			session['username'] = username
			return redirect('/')
	else:
		return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
	#TODO 使用ajax的方式提示错误
	if request.method == 'POST':
		username = request.form['username']
		password = request.form['password']
		c = g.db.cursor()
		c.execute("select * from user where username=%s and password=%s", (username, password))
		rows = c.fetchall()
		if username==None or username=="" or password==None:
			return render_template('login.html', error=True, message=u'字段不能为空')
		elif len(rows) == 0:
			return render_template('login.html', error=True, message=u'用户名或者密码不正确')
		else:
			session['login'] = True
			session['username'] = username
			return redirect('/')
	else:
		return render_template('login.html')

@app.route('/logout')
def logout():
	del session['login']
	del session['username']
	return redirect('/')

@app.route('/topic', defaults={'page':1})
@app.route('/topic/<page>')
def topic(page):
	try:
		page = int(page)
	except ValueError:
		page = 1
	st = PER_TOPIC*(page-1)
	ed = st+PER_TOPIC
	c = g.db.cursor()
	c.execute("select * from topic order by mtime desc")
	entries = [dict(id=row[0], author=row[1], title=row[2], content=row[3], delta=helper.timegap(row[5])) for row in c.fetchall()]
	pageNumber = len(entries)/PER_TOPIC+1
	for entry in entries:
		c.execute("select * from reply where id=%s order by mtime asc", entry['id'])
		rows = c.fetchall()
		if len(rows)==0:
			entry['reply'] = entry['author']
		else:
			entry['reply'] = rows[0][1]
	if len(entries) < ed:
		ed = len(entries)
	entries = entries[st:ed]
	return render_template('topic.html', entries=entries, pageNumber=pageNumber, page=page, pagetype="topic")

@app.route('/reply/<id>')
def reply(id):
	c = g.db.cursor()
	c.execute("select * from topic where id=%s", id)
	row = c.fetchone()
	delta = helper.timegap(row[4])
	entry = dict(id=id, author=row[1], title=row[2], content=row[3], delta=delta)
	c.execute("select * from reply where tid=%s order by mtime asc", id)
	replies = [dict(author=row[1], content=row[2], delta=helper.timegap(row[3])) for row in c.fetchall()]
	number = len(replies)
	return render_template('reply.html', number=number, entry=entry, replies=replies, pagetype="topic")

@app.route('/post_reply/<id>', methods=['GET', 'POST'])
def post_reply(id):
	if request.method == 'POST':
		content = request.form['reply']
		author = session['username']
		mtime = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
		tid = id
		c = g.db.cursor()
		c.execute("insert into reply(author, content, mtime, tid) values (%s, %s, %s, %s)", (author, content, mtime, tid))
		c.execute("update topic set mtime=%s where id=%s", (mtime, id))
		g.db.commit()
	return redirect('/reply/'+id)

@app.route('/admin')
def admin():
	return render_template('admin.html')

@app.route('/post_paper', methods=['GET', 'POST'])
def post_paper():
	if request.method == 'POST':
		title = request.form['title']
		description = request.form['description']
		content = request.form['content']
		c = g.db.cursor()
		c.execute("insert into paper(title, description, content) values (%s, %s, %s)", (title, description, content))
		g.db.commit()
	return render_template('admin.html')


@app.route('/add_pic')
def add_pic():
	return render_template('add_pic.html')

@app.route('/post_pic', methods=['GET', 'POST'])
def post_pic():
	if request.method == 'POST':
		title = request.form['title']
		description = request.form['description']
		content = request.form['content']
		c = g.db.cursor()
		c.execute("insert into picture(title, description, content) values (%s, %s, %s)", (title, description, content))
		g.db.commit()
	return render_template('add_pic.html')

@app.route('/add_topic')
def add_topic():
	if not ('login' in session):
		return render_template('login.html', error=True, message=u'登录之后才能发表话题')
	return render_template('add_topic.html', pagetype="topic")

@app.route('/post_topic', methods=['GET', 'POST'])
def post_topic():
	if request.method == 'POST':
		title = request.form['title']
		content = request.form['content']
		author = session['username']
		ctime = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
		mtime = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
		c = g.db.cursor()
		c.execute("insert into topic(title, content, author, ctime, mtime) values (%s, %s, %s, %s, %s)", (title, content, author, ctime, mtime))
		g.db.commit()
	return redirect('/topic')

@app.route('/add_test')
def add_test():
	return render_template('add_test.html', pagetype="test")

@app.route('/post_test', methods=['GET', 'POST'])
def post_test():
	if request.method == 'POST':
		title = request.form['title']
		description = request.form['description']
		file = request.files['file']
		mtime = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
		file.save('static/test/'+mtime)		
		c = g.db.cursor()
		c.execute("insert into test(title, description, filename, mtime) values (%s, %s, %s, %s)", (title, description, mtime, mtime))
		g.db.commit()
	return redirect('/add_test')

@app.route('/test', defaults={'page':1})
@app.route('/test/<page>')
def test(page):
	try:
		page = int(page)
	except ValueError:
		page = 1
	st = PER_PAGE*(page-1)
	ed = st+PER_PAGE
	c = g.db.cursor()
	c.execute("select * from test")
	entries = [dict(id=row[0], title=row[1], description=row[4]) for row in c.fetchall()]
	pageNumber = len(entries)/PER_PAGE+1
	if len(entries) < ed:
		ed = len(entries)
	entries = entries[st:ed]
	return render_template('test.html', entries=entries, pageNumber=pageNumber, page=page, pagetype="test")

@app.route('/testview')
def testview():
	test_id = request.args['id']
	c = g.db.cursor()
	c.execute("select * from test where id=%s", test_id)
	row = c.fetchone()
	filename = row[2]
	entry = helper.fileread(filename)
	return render_template('testview.html', entry=entry, id=test_id, pagetype="test")

@app.route('/post_test', methods=['GET', 'POST'])
def post_test():
	if request.method == 'POST':
		test_id = request.form['id']
		c = g.db.cursor()
		c.execute("select * from test where id=%s", test_id)
		row = c.fetchone()
		filename = row[2]
		entry = helper.fileread(filename)
		score = 0
		symptoms = []
		questions = entry['questions']
		for j in range(len(questions)):
			question = questions[j]
			value = request.form.get(question, None)
			options = entry['options']
			opt_scores = entry['opt_scores']
			for i in range(len(options)):
				if options[i] == value:
					score = score+opt_scores[i]
				if i==(len(options)-1):
					symptoms.append(entry['symptoms'][j])
		results = entry['result']	
		result = ''
		for key in results:
			if key.isdigit():
				if score < int(key):
					result = results[key]
					break
			else:
				result = results[key]
				break
		return render_template('testresult.html',title=entry['title'],id=test_id, result=result, symptoms=symptoms, pagetype="test")
