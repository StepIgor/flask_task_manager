from flask import Flask
from flask import render_template,flash,redirect,session,request,jsonify
from loginform import *
from database import *

#пути

@application.route("/", methods=['GET','POST'])

def hello():	#страница входа на сайт
	
	if session.get('logged',None) == 1 and session.get("level",None) == "user":	#чекаем наличие входа
		return redirect('https://***.ru/account')
	elif session.get('logged',None) == 1 and session.get("level",None) == "admin":
		return redirect('https://***.ru/admin')
	
	logform = LoginForm()
	
	if logform.validate_on_submit():	#обрабатываем полученные логин и пароль
		if session.get('logged',None) == 1:
			return redirect('https://***.ru/account')
		user = data.query.filter_by(username=logform.username.data).first()
		if not user is None:
			if logform.password.data == user.password:
				session['username'] = logform.username.data.lower()
				session['logged'] = 1	#по этому параметру потом проверяем наличие входа в акк
				session['level'] = user.level
				if user.level == "admin":
					return redirect('https://***.ru/admin')
				else:
					return redirect('https://***.ru/account')
			else:
				flash('Неправильный пароль!')
		else:
			flash('Аккаунта с таким логином нет!')
		return redirect('https://***.ru')
	
	return render_template('index.html',form=logform,title='Войти')
   
@application.route("/account")
   
def account():	#страница обычного пользователя
	if session.get('logged',None) != 1:
		return redirect('https://***.ru')
	if session.get("level",None) != "user":
		return redirect("https://***.ru/admin")
	
	return render_template('account.html',username=session.get('username',None),tasks=task.query.all(),title='Главная страница')
	
@application.route("/admin")	#страница админа
	
def admin():
	if session.get('logged',None) != 1:
		return redirect('https://***.ru')
	if session.get("level",None) != "admin":
		return redirect("https://***.ru/account")
		
	return render_template('admin.html',username=session.get('username',None),task=task.query.all(),data=data.query.all(),title='Главная страница')
	
@application.route("/logout") #если нажата кнопка выхода
def logout():
	session['logged'] = 0
	return redirect('https://***.ru')

@application.route("/admin/adduser", methods=['POST','GET'])	#страница добавления пользователя - только для админа
def adduser():
	if session.get('logged',None) != 1:
		return redirect('https://***.ru')
	if session.get("level",None) != "admin":
		return redirect("https://***.ru/account")
		
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
			return redirect('https://***.ru/admin')
		else:
			flash('Такой пользователь уже есть!')
		return redirect('https://***.ru/admin/adduser')


	return render_template('adduser.html',adduserform=adduserformsend,title='Добавить пользователя')
	
@application.route("/admin/addtask",methods=['GET','POST'])	#страница добавления задания - только для админа
	
def addtask():
	if session.get('logged',None) != 1:
		return redirect('https://***.ru')
	if session.get("level",None) != "admin":
		return redirect("https://***.ru/account")
	
	addtaskform = AddTaskForm()
	
	if addtaskform.validate_on_submit():
		test = task.query.filter_by(taskname=addtaskform.name.data).first()
		if test is None:
			test = data.query.filter_by(username=addtaskform.foruser.data).first()
			if not test is None:
				newtask = task(taskname=addtaskform.name.data,foruser=addtaskform.foruser.data,status='not_ready',info=addtaskform.info.data)
				db.session.add(newtask)
				db.session.commit()
				return redirect('https://***.ru/admin')
			else:
				flash('Такого пользователя не существует!')
		else:
			flash('Задание с таким названием уже есть!')
		return redirect('https://***.ru/admin/addtask')
	
	return render_template('addtask.html',addtaskform=addtaskform,title='Добавить задание')
	
@application.route("/account/done")	#Пользователь заявил о выполнении задания
def done():
	if session.get('logged',None) != 1:
		return redirect('https://***.ru')
	if session.get("level",None) != "user":
		return redirect("https://***.ru/admin")
	args = request.args.to_dict()	#в словарь загружаем параметры из url
	
	donetask = task.query.filter_by(taskname=args['name']).first()
	
	if not donetask is None:	#проверяем, есть задание в базе с таким именем - защита от произвольного url
		donetask.status = 'check'
		db.session.commit()
	
	return redirect('https://***.ru/account')
	
@application.route("/admin/accept")	#админ подтвержает выполнение задачи
def admindone():
	if session.get('logged',None) != 1:
		return redirect('https://***.ru')
	if session.get("level",None) != "admin":
		return redirect("https://***.ru/account")	#проверяем уровень доступа
	args = request.args.to_dict()
	
	accepttask = task.query.filter_by(taskname=args['name']).first()
	
	if not accepttask is None:	#проверяем, есть задание в базе с таким именем - защита от произвольного url
		accepttask.status = 'done'
		db.session.commit()
	
	return redirect('https://***.ru/admin')
	