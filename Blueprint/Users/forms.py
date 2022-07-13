from sanic_wtf import SanicForm
from wtforms import PasswordField, StringField, SubmitField
from wtforms.validators import DataRequired, InputRequired, EqualTo

#https://github.com/stopspazzing/Sanic-MDL-Blog/tree/master/app

class LoginForm(SanicForm):
    name = StringField('Имя пользователя', validators=[DataRequired()])
    password = PasswordField('Введите пароль', validators=[DataRequired()])
    submit = SubmitField('Войти')

class RegisterForm(SanicForm):
    name = StringField('Имя пользователя', validators=[DataRequired()])
    password = PasswordField('Придумайте пароль', [InputRequired(), EqualTo('confirm', message='Пароли должны совпадать')])
    confirm = PasswordField('Повторите пароль')
    submit = SubmitField('Зарегистрироваться')