# coding=utf-8
from flask import Flask, request, session, g, redirect, url_for, abort, \
     render_template, flash
from xinli import *

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
	return render_template('pic/pic.html', entries=entries, pageNumber=pageNumber, page=page, pagetype="pic")

@app.route('/picview')
def picview():
	pic_id = request.args['id']
	c = g.db.cursor()
	c.execute("select * from picture where pic_id=%s", pic_id)
	row = c.fetchone()
	entry = dict(id=row[0], title=row[1], description=row[2], content=row[3])
	return render_template('pic/picview.html', entry=entry, pagetype="pic")

@app.route('/add_pic')
def add_pic():
	return render_template('pic/add_pic.html')

@app.route('/post_pic', methods=['GET', 'POST'])
def post_pic():
	if request.method == 'POST':
		title = request.form['title']
		description = request.form['description']
		content = request.form['content']
		c = g.db.cursor()
		c.execute("insert into picture(title, description, content) values (%s, %s, %s)", (title, description, content))
		g.db.commit()
	return render_template('pic/add_pic.html')

