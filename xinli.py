# coding=utf-8
import MySQLdb
from flask import Flask, request, session, g, redirect, url_for, abort, \
     render_template

app = Flask(__name__)
app.debug = True
app.config.from_pyfile('config.cfg', silent=True)

# config
MYSQL_HOST = 'localhost'
MYSQL_USER = 'root'
MYSQL_PASS = '123456'
MYSQL_DB = 'app_xinli525'
MYSQL_PORT = '3306'
PER_PAGE = 4
PER_TOPIC = 6



@app.before_request
def before_request():
    g.db = MySQLdb.connect(MYSQL_HOST, MYSQL_USER, MYSQL_PASS,
                           MYSQL_DB, port=int(MYSQL_PORT), charset='utf8')

@app.teardown_request
def teardown_request(exception):
    if hasattr(g, 'db'): g.db.close()

from view import *
