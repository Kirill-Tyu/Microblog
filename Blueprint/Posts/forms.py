from sanic_wtf import SanicForm
from wtforms import PasswordField, StringField, SubmitField
from wtforms.validators import DataRequired, InputRequired, EqualTo

#https://github.com/stopspazzing/Sanic-MDL-Blog/tree/master/app

class AddPostForm(SanicForm):
    title = StringField('Название поста', validators=[DataRequired()])
    text = StringField('Содержимое поста', validators=[DataRequired()])
    submit = SubmitField('Опубликовать')
