# -*— coding:utf-8 -*—
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField, RadioField,PasswordField,IntegerField,TextAreaField
from wtforms.validators import DataRequired,Length,Regexp,EqualTo
from wtforms import ValidationError
from app.models import User,Book,Library,choices


class LoginForm(FlaskForm):
    username = StringField('Username',validators=[DataRequired()])
    password = PasswordField('Password',validators=[DataRequired()])
    submit = SubmitField('登录')


class RegisterForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired(),EqualTo('password2',message='密码不一致.')])
    password2 = PasswordField('Password', validators=[DataRequired()])
    name = StringField('Name',validators=[DataRequired()])
    gender = SelectField('Gender',choices=[('1','男'),('2','女')],default='1',coerce=str)
    id = StringField('Id',validators=[DataRequired()])
    depart = StringField('Depart',validators=[DataRequired()])
    contact = StringField('Contact',validators=[DataRequired()])
    room = StringField('Room',validators=[DataRequired()])
    avata = StringField('Avata',validators=[])
    submit = SubmitField('注册')

    def validate_username(self,field):
        if User.query.filter_by(username=field.data).first():
            raise ValidationError('用户名已存在')


class AddBookForm(FlaskForm):
    book_id = StringField('Book_id',validators=[DataRequired()])
    isbn = StringField('ISBN', validators=[DataRequired()])
    name = StringField('Name', validators=[DataRequired()])
    author = StringField('Author', validators=[DataRequired()])
    press = StringField('Press', validators=[DataRequired()])
    choices = choices
    category = SelectField('Category', validators=[DataRequired()],choices=choices,coerce=str,default=0)
    location = StringField('Location', validators=[DataRequired()])
    brefintro = TextAreaField('Brefintro', validators=[DataRequired()])
    cover = StringField('Avata', validators=[])
    submit = SubmitField('新书入库')

    flag = 0
    def validate_isbn(self,field):
        if Book.query.filter_by(isbn=field.data).first():
            self.flag = 1
            raise ValidationError('该ISBN的图书已经存在')

    def validate_book_id(self,field):
        if Library.query.filter_by(book_id=field.data).first():
            self.flag = 2
            raise ValidationError('该图书编号的图书已经存在')

class EditBookForm(FlaskForm):
    isbn = StringField('ISBN', validators=[DataRequired()])
    name = StringField('Name', validators=[DataRequired()])
    author = StringField('Author', validators=[DataRequired()])
    press = StringField('Press', validators=[DataRequired()])
    category = StringField('Category', validators=[DataRequired()])
    brefintro = TextAreaField('Brefintro', validators=[DataRequired()])
    submit = SubmitField('提交')


class SearchBookForm(FlaskForm):
    choices = [('1','书名'),('2','作者'),('3','ISBN')]
    option = SelectField('Option',validators=[DataRequired()],choices=choices,coerce=str)
    key = StringField('key',validators=[DataRequired()])
    submit = SubmitField('提交')

class SearchUserForm(FlaskForm):
    choices = [('1','姓名'),('2','联系方式'),('3','证件号')]
    option = SelectField('Option',validators=[DataRequired()],choices=choices,coerce=str)
    key = StringField('key',validators=[DataRequired()])
    submit = SubmitField('提交')

class AdminUserForm(FlaskForm):
    username = StringField('Name', validators=[DataRequired()])
    name = StringField('Name', validators=[DataRequired()])
    gender = StringField('Gender', validators=[])
    id = StringField('Id', validators=[])
    depart = StringField('Depart', validators=[DataRequired()])
    post = StringField('Post', validators=[])
    contact = StringField('Contact', validators=[DataRequired()])
    room = StringField('Room', validators=[DataRequired()])
    submit = SubmitField('确认修改')

class AdminPasswdForm(FlaskForm):
    password = PasswordField('Password', validators=[DataRequired(), EqualTo('password2', message='密码不一致')])
    password2 = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('确认修改')


class SysSetForm(FlaskForm):
    maxuser = StringField('Maxuser', validators=[DataRequired()])
    maxbook = StringField('Maxbook', validators=[DataRequired()])
    maxtime = StringField('Maxtime', validators=[DataRequired()])
    submit = SubmitField('确认修改')
