# coding=utf-8
from flask import Flask, request, session, g, redirect, url_for, abort, \
     render_template, flash
from xinli import *


@app.route('/cure')
def cure():
	return render_template('cure/cure.html', pagetype="cure")
