from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TelField, SelectField, IntegerField, SubmitField
from wtforms.validators import DataRequired, Email, Length, EqualTo, Regexp, NumberRange

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
        DataRequired(message='请输入用户名'),
        Length(min=3, max=20, message='用户名长度必须在3-20个字符之间')
    ])
    phone = StringField('手机号', validators=[
        DataRequired(message='请输入手机号'),
        Regexp(r'^1[3-9]\d{9}$', message='请输入有效的手机号')
    ])
    password = PasswordField('密码', validators=[
        DataRequired(message='请输入密码'),
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
    age = IntegerField('年龄', validators=[NumberRange(min=16, max=100)])
    education = SelectField('学历', choices=[
        ('高中', '高中'),
        ('专科', '专科'),
        ('本科', '本科'),
        ('硕士', '硕士'),
        ('博士', '博士')
    ], validators=[DataRequired(message='请选择学历')])

class ChangePasswordForm(FlaskForm):
    current_password = PasswordField('当前密码', validators=[DataRequired()])
    new_password = PasswordField('新密码', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('确认新密码', validators=[DataRequired(), EqualTo('new_password')])
    submit = SubmitField('修改密码') 