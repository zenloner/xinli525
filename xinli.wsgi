import sys
ROOT_DIR = '/home/zenloner/www/xinli525'
sys.path.append(ROOT_DIR)
#if you want to run your flask code on apache, you need to alias app to application
from xinli import app as application

#three must be a if statement
if __name__=='__main__':
	#the name should be application, then apache can recognize
	application.run()
