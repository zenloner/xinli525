# coding=utf-8
import MySQLdb
from flask import Flask, request, session, g, redirect, url_for, abort, \
     render_template

app = Flask(__name__)
app.debug = True
app.config.from_pyfile('config.cfg', silent=True)

from config import *




@app.before_request
def before_request():
    g.db = MySQLdb.connect(MYSQL_HOST, MYSQL_USER, MYSQL_PASS,
                           MYSQL_DB, port=int(MYSQL_PORT), charset='utf8')

@app.teardown_request
def teardown_request(exception):
    if hasattr(g, 'db'): g.db.close()

from view import *
