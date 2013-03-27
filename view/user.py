# coding=utf-8
from flask import Flask, request, session, g, redirect, url_for, abort, \
     render_template, flash
from xinli import *

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
			return render_template('user/register.html', error=True, message=u'字段不能为空')
		elif len(rows) != 0:
			return render_template('user/register.html', error=True, message=u'用户名已经被注册')
		elif password != confirm:
			return render_template('user/register.html', error=True, message=u'两次输入的密码不一样')
		else:
			c.execute("insert into user(username, password, email) values (%s, %s, %s)", (username, password, email))
			g.db.commit()
			session['login'] = True
			session['username'] = username
			return redirect('/')
	else:
		return render_template('user/register.html')


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
			return render_template('user/login.html', error=True, message=u'字段不能为空')
		elif len(rows) == 0:
			return render_template('user/login.html', error=True, message=u'用户名或者密码不正确')
		else:
			session['login'] = True
			session['username'] = username
			return redirect('/')
	else:
		return render_template('user/login.html')

@app.route('/logout')
def logout():
	del session['login']
	del session['username']
	return redirect('/')
