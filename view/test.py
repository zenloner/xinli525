# coding=utf-8
from flask import Flask, request, session, g, redirect, url_for, abort, \
     render_template, flash
import helper
import datetime
from xinli import *

@app.route('/add_test')
def add_test():
	return render_template('test/add_test.html', pagetype="test")

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
	return render_template('test/test.html', entries=entries, pageNumber=pageNumber, page=page, pagetype="test")

@app.route('/testview')
def testview():
	test_id = request.args['id']
	c = g.db.cursor()
	c.execute("select * from test where id=%s", test_id)
	row = c.fetchone()
	filename = row[2]
	entry = helper.fileread(filename)
	return render_template('test/testview.html', entry=entry, id=test_id, pagetype="test")

@app.route('/test_test', methods=['GET', 'POST'])
def test_test():
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
		return render_template('test/testresult.html',title=entry['title'],id=test_id, result=result, symptoms=symptoms, pagetype="test")
