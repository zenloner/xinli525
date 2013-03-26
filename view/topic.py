# coding=utf-8
from flask import Flask, request, session, g, redirect, url_for, abort, \
     render_template, flash
import helper
import datetime
from xinli import *

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
	return render_template('topic/topic.html', entries=entries, pageNumber=pageNumber, page=page, pagetype="topic")


@app.route('/add_topic')
def add_topic():
	if not ('login' in session):
		return render_template('user/login.html', error=True, message=u'登录之后才能发表话题')
	return render_template('topic/add_topic.html', pagetype="topic")

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
	return render_template('topic/reply.html', number=number, entry=entry, replies=replies, pagetype="topic")

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

