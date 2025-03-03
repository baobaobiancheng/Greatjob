from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TelField, SelectField
from wtforms.validators import DataRequired, Email, Length, EqualTo, Regexp

class LoginForm(FlaskForm):
    username = StringField('用户名', validators=[
        DataRequired(message='用户名不能为空'),
        Length(min=3, max=20, message='用户名长度必须在3-20个字符之间')
    ])
    password = PasswordField('密码', validators=[
        DataRequired(message='密码不能为空'),
        Length(min=6, max=20, message='密码长度必须在6-20个字符之间')
    ])

class RegisterForm(FlaskForm):
    username = StringField('用户名', validators=[
        DataRequired(message='用户名不能为空'),
        Length(min=3, max=20, message='用户名长度必须在3-20个字符之间')
    ])
    phone = TelField('手机号', validators=[
        DataRequired(message='手机号不能为空'),
        Regexp(r'^1[3-9]\d{9}$', message='请输入正确的手机号')
    ])
    password = PasswordField('密码', validators=[
        DataRequired(message='密码不能为空'),
        Length(min=6, max=20, message='密码长度必须在6-20个字符之间')
    ])
    confirm_password = PasswordField('确认密码', validators=[
        DataRequired(message='请确认密码'),
        EqualTo('password', message='两次输入的密码不一致')
    ])

class ResumeForm(FlaskForm):
    name = StringField('姓名', validators=[
        DataRequired(message='姓名不能为空'),
        Length(max=20, message='姓名长度不能超过20个字符')
    ])
    age = StringField('年龄', validators=[
        DataRequired(message='年龄不能为空'),
        Regexp(r'^\d{1,2}$', message='请输入正确的年龄')
    ])
    education = SelectField('学历', choices=[
        ('本科', '本科'),
        ('硕士', '硕士'),
        ('博士', '博士')
    ], validators=[DataRequired(message='请选择学历')]) 