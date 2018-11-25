from flask import Flask
from flask import render_template,flash,redirect,session,request,jsonify
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import DataRequired
import json
application = Flask(__name__)

application.config['SECRET_KEY'] = "something"

	
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

@application.route("/", methods=['GET','POST'])

def hello():
	
	if session.get('logged',None) == 1 and session.get("level",None) == "user":
		return redirect('https://difres.ru/account')
	elif session.get('logged',None) == 1 and session.get("level",None) == "admin":
		return redirect('https://difres.ru/admin')
	
	logform = LoginForm()
	
	data = {}
	
	if logform.validate_on_submit():
		if session.get('logged',None) == 1:
			return redirect('https://difres.ru/account')
		with open('data/data.json','r') as f:
			data = json.load(f)
		if logform.username.data.lower() in list(data.keys()):
			if data[logform.username.data.lower()]['password'] == logform.password.data.lower():
				session['logged'] = 1
				session['username'] = logform.username.data.lower()
				session['level'] = data[logform.username.data.lower()]['level']
				if session.get("level",None) == "user":
					return redirect('https://difres.ru/account')
				else:
					return redirect('https://difres.ru/admin')
			else:
				flash('Неправильный пароль!')
				return redirect('https://difres.ru')
		else:
			flash('Аккаунта с таким логином нет!')
			return redirect('https://difres.ru')
		return redirect('https://difres.ru')
#
	return render_template('index.html',form=logform)
   
@application.route("/account")
   
def account():
	if session.get('logged',None) != 1:
		return redirect('https://difres.ru')
	if session.get("level",None) != "user":
		return redirect("https://difres.ru/admin")
		
	tasks = {}
	data = {}
	
	with open('data/data.json','r') as f:
		data = json.load(f)
		
	with open('data/task.json','r') as f:
		tasks = json.load(f)
		
	
	return render_template('account.html',username=session.get('username',None),tasks=tasks,data=data)
	
@application.route("/admin")
	
def admin():
	if session.get('logged',None) != 1:
		return redirect('https://difres.ru')
	if session.get("level",None) != "admin":
		return redirect("https://difres.ru/account")
		
	tasks = {}
	data = {}
	userslist = []
	
	with open('data/data.json','r') as f:
		data = json.load(f)
		
	with open('data/task.json','r') as f:
		tasks = json.load(f)
		
	for key in list(data.keys()):
		userslist.extend([key,data[key]['level']])
		
	lenuserslist = len(userslist)
	
		
	return render_template('admin.html',username=session.get('username',None),data=data,userslist=userslist,lenuserslist=lenuserslist,tasks=tasks)
	
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
	
	data = {}
	
	with open('data/data.json','r') as f:
		data = json.load(f)
	
	if adduserformsend.validate_on_submit():
		if not adduserformsend.name.data.lower() in list(data.keys()):
			if adduserformsend.isadmin.data:
				pass
				data.update({adduserformsend.name.data.lower():{'password':adduserformsend.password.data.lower(),'level':'admin'}})
			else:
				pass
				data.update({adduserformsend.name.data.lower():{'password':adduserformsend.password.data.lower(),'level':'user'}})
			with open('data/data.json','w') as f:
				json.dump(data,f)
			return redirect('https://difres.ru/admin')
		else:
			flash('Аккаунт с таким логином уже существует.')
			return redirect('https://difres.ru/admin/adduser')
		
		return redirect('https://difres.ru/admin/adduser')
		
	return render_template('adduser.html',adduserform=adduserformsend)
	
@application.route("/admin/addtask",methods=['GET','POST'])
	
def addtask():
	if session.get('logged',None) != 1:
		return redirect('https://difres.ru')
	if session.get("level",None) != "admin":
		return redirect("https://difres.ru/account")
	
	addtaskform = AddTaskForm()
	
	data = {}
	tasks = {}
	
	with open('data/data.json','r') as f:
		data = json.load(f)
	
	with open('data/task.json','r') as f:
		tasks = json.load(f)
	
	if addtaskform.validate_on_submit():
		if addtaskform.foruser.data.lower() in list(data.keys()):
			tasks.update({addtaskform.name.data:{'user':addtaskform.foruser.data.lower(),'status':'not_ready','info':addtaskform.info.data}})
			with open('data/task.json','w') as f:
				json.dump(tasks,f)
			return redirect('https://difres.ru/admin')
		else:
			flash('Пользователь, которому вы пытаетесь поручить задание, не существует.')
		return redirect('https://difres.ru/admin/addtask')
	
	return render_template('addtask.html',addtaskform=addtaskform)
	
@application.route("/account/done")
def done():
	if session.get('logged',None) != 1:
		return redirect('https://difres.ru')
	if session.get("level",None) != "user":
		return redirect("https://difres.ru/admin")
	args = request.args.to_dict()
	tasks = {}
	with open('data/task.json','r') as f:
		tasks = json.load(f)
	if args['name'] in list(tasks.keys()) and tasks[args['name']]['status'] == "not_ready":
		tasks[args['name']]['status'] = 'check'
		with open('data/task.json','w') as f:
			json.dump(tasks,f)
		return redirect('https://difres.ru/account')
	else:
		redirect('https://difres.ru/account')
	return redirect('https://difres.ru/account')
	
@application.route("/admin/accept")
def admindone():
	if session.get('logged',None) != 1:
		return redirect('https://difres.ru')
	if session.get("level",None) != "admin":
		return redirect("https://difres.ru/account")
	args = request.args.to_dict()
	tasks = {}
	with open('data/task.json','r') as f:
		tasks = json.load(f)
	if args['name'] in list(tasks.keys()) and tasks[args['name']]['status'] == "check":
		tasks[args['name']]['status'] = 'done'
		with open('data/task.json','w') as f:
			json.dump(tasks,f)
		return redirect('https://difres.ru/admin')
	else:
		redirect('https://difres.ru/admin')
	return redirect('https://difres.ru/admin')
	