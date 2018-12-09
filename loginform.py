from flask import Flask
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import DataRequired
from database import application


application.config['SECRET_KEY'] = "something"

class LoginForm(FlaskForm):	#форма входа
	username = StringField('Логин', validators=[DataRequired()])
	password = PasswordField('Пароль', validators=[DataRequired()])
	submit = SubmitField('Войти')
	
class AddUserForm(FlaskForm):	#форма добавления пользователя
	name = StringField('Логин', validators=[DataRequired()])
	password = PasswordField('Пароль', validators=[DataRequired()])
	isadmin = BooleanField('Права администратора')
	adduser = SubmitField('Добавить')
	
class AddTaskForm(FlaskForm): #форма добавления задания
	name = StringField('Название', validators=[DataRequired()])
	foruser = StringField('Кому поручить (имя пользователя)', validators=[DataRequired()])
	info = StringField('Подробности', validators=[DataRequired()])
	addtasknow = SubmitField('Добавить')