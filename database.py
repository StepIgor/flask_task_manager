from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate


application = Flask(__name__)
application.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://:@/'
db = SQLAlchemy(application)
migrate = Migrate(application,db)

class data(db.Model):	#данные пользователей
	id = db.Column(db.Integer, primary_key=True)
	username = db.Column(db.String(64), index=True, unique=True)
	password = db.Column(db.String(64))
	level = db.Column(db.String(5))

	def __init__(self, *args, **kwargs):
		super(data,self).__init__(*args,**kwargs)
		
class task(db.Model):	#база заданий
	id = db.Column(db.Integer, primary_key=True)
	taskname = db.Column(db.String(64), index=True, unique=True)
	foruser = db.Column(db.String(32))
	status = db.Column(db.String(10))
	info = db.Column(db.String(128))
	
	def __init__(self, *args, **kwargs):
		super(task,self).__init__(*args,**kwargs)	