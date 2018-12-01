from flask import Flask
from flask import render_template,flash,redirect,session,request,jsonify
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import DataRequired
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import json
application = Flask(__name__)

application.config['SECRET_KEY'] = "something"
application.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://login:password@ip/basename'

db = SQLAlchemy(application)

migrate = Migrate(application,db)

class LoginForm(FlaskForm):
	username = StringField('Логин', validators=[DataRequired()])
	password = PasswordField('Пароль', validators=[DataRequired()])
	submit = SubmitField('Войти')
	
class AddUserForm(FlaskForm):
	name = StringField('Логин', validators=[DataRequired()])
	password = PasswordField('Пароль', validators=[DataRequired()])
	isadmin = BooleanField('Права администратора')
	adduser = SubmitField('Добавить')
	
class AddTaskForm(FlaskForm):
	name = StringField('Название', validators=[DataRequired()])
	foruser = StringField('Кому поручить (имя пользователя)', validators=[DataRequired()])
	info = StringField('Подробности', validators=[DataRequired()])
	addtasknow = SubmitField('Добавить')

class data(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	username = db.Column(db.String(64), index=True, unique=True)
	password = db.Column(db.String(64))
	level = db.Column(db.String(5))

	def __init__(self, *args, **kwargs):
		super(data,self).__init__(*args,**kwargs)
		
class task(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	taskname = db.Column(db.String(64), index=True, unique=True)
	foruser = db.Column(db.String(32))
	status = db.Column(db.String(10))
	info = db.Column(db.String(128))
	
	def __init__(self, *args, **kwargs):
		super(task,self).__init__(*args,**kwargs)
		

@application.route("/", methods=['GET','POST'])

def hello():
	
	if session.get('logged',None) == 1 and session.get("level",None) == "user":
		return redirect('https://difres.ru/account')
	elif session.get('logged',None) == 1 and session.get("level",None) == "admin":
		return redirect('https://difres.ru/admin')
	
	logform = LoginForm()
	
	if logform.validate_on_submit():
		if session.get('logged',None) == 1:
			return redirect('https://difres.ru/account')
		user = data.query.filter_by(username=logform.username.data).first()
		if not user is None:
			if logform.password.data == user.password:
				session['username'] = logform.username.data.lower()
				session['logged'] = 1
				session['level'] = user.level
				if user.level == "admin":
					return redirect('https://difres.ru/admin')
				else:
					return redirect('https://difres.ru/account')
			else:
				flash('Неправильный пароль!')
		else:
			flash('Аккаунта с таким логином нет!')
		return redirect('https://difres.ru')
	
	return render_template('index.html',form=logform)
   
@application.route("/account")
   
def account():
	if session.get('logged',None) != 1:
		return redirect('https://difres.ru')
	if session.get("level",None) != "user":
		return redirect("https://difres.ru/admin")
	
	return render_template('account.html',username=session.get('username',None),tasks=task.query.all())
	
@application.route("/admin")
	
def admin():
	if session.get('logged',None) != 1:
		return redirect('https://difres.ru')
	if session.get("level",None) != "admin":
		return redirect("https://difres.ru/account")
		
	return render_template('admin.html',username=session.get('username',None),task=task.query.all(),data=data.query.all())
	
@application.route("/logout")
def logout():
	session['logged'] = 0
	return redirect('https://difres.ru')

@application.route("/admin/adduser", methods=['POST','GET'])
def adduser():
	if session.get('logged',None) != 1:
		return redirect('https://difres.ru')
	if session.get("level",None) != "admin":
		return redirect("https://difres.ru/account")
		
	adduserformsend = AddUserForm()
	
	if adduserformsend.validate_on_submit():
		test = data.query.filter_by(username=adduserformsend.name.data).first()
		if test is None:
			if adduserformsend.isadmin.data:
				newuser = data(username=adduserformsend.name.data,password=adduserformsend.password.data,level='admin')
			else:
				newuser = data(username=adduserformsend.name.data,password=adduserformsend.password.data,level='user')
			db.session.add(newuser)
			db.session.commit()
			return redirect('https://difres.ru/admin')
		else:
			flash('Такой пользователь уже есть!')
		return redirect('https://difres.ru/admin/adduser')


	return render_template('adduser.html',adduserform=adduserformsend)
	
@application.route("/admin/addtask",methods=['GET','POST'])
	
def addtask():
	if session.get('logged',None) != 1:
		return redirect('https://difres.ru')
	if session.get("level",None) != "admin":
		return redirect("https://difres.ru/account")
	
	addtaskform = AddTaskForm()
	
	if addtaskform.validate_on_submit():
		test = task.query.filter_by(taskname=addtaskform.name.data).first()
		if test is None:
			test = data.query.filter_by(username=addtaskform.foruser.data).first()
			if not test is None:
				newtask = task(taskname=addtaskform.name.data,foruser=addtaskform.foruser.data,status='not_ready',info=addtaskform.info.data)
				db.session.add(newtask)
				db.session.commit()
				return redirect('https://difres.ru/admin')
			else:
				flash('Такого пользователя не существует!')
		else:
			flash('Задание с таким названием уже есть!')
		return redirect('https://difres.ru/admin/addtask')
	
	return render_template('addtask.html',addtaskform=addtaskform)
	
@application.route("/account/done")
def done():
	if session.get('logged',None) != 1:
		return redirect('https://difres.ru')
	if session.get("level",None) != "user":
		return redirect("https://difres.ru/admin")
	args = request.args.to_dict()
	
	donetask = task.query.filter_by(taskname=args['name']).first()
	
	if not donetask is None:
		donetask.status = 'check'
		db.session.commit()
	
	return redirect('https://difres.ru/account')
	
@application.route("/admin/accept")
def admindone():
	if session.get('logged',None) != 1:
		return redirect('https://difres.ru')
	if session.get("level",None) != "admin":
		return redirect("https://difres.ru/account")
	args = request.args.to_dict()
	
	accepttask = task.query.filter_by(taskname=args['name']).first()
	
	if not accepttask is None:
		accepttask.status = 'done'
		db.session.commit()
	
	return redirect('https://difres.ru/admin')
	