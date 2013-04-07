# coding=utf-8
from flask import Flask, request, session, g, redirect, url_for, abort, \
     render_template, flash
#import database connection
from xinli import *

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
	return render_template('paper/index.html', entries=entries, pageNumber=pageNumber, page=page, pagetype="paper")

@app.route('/paper')
def paper():
	paper_id = request.args['id']
	c = g.db.cursor()
	c.execute("select * from paper where paper_id=%s", paper_id)
	row = c.fetchone()
	entry = dict(id=row[0], title=row[1], description=row[2], content=row[3])
	return render_template('paper/paper.html', entry=entry, pagetype="paper")

@app.route('/add_paper')
def add_paper():
	return render_template('paper/add_paper.html')

@app.route('/post_paper', methods=['GET', 'POST'])
def post_paper():
	if request.method == 'POST':
		title = request.form['title']
		description = request.form['description']
		content = request.form['content']
		c = g.db.cursor()
		c.execute("insert into paper(title, description, content) values (%s, %s, %s)", (title, description, content))
		g.db.commit()
	return render_template('paper/add_paper.html')


