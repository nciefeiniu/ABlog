from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField,SelectField
from wtforms.validators import DataRequired
from flask_uploads import UploadSet, IMAGES
from flask_wtf.file import FileField, FileAllowed, FileRequired

images = UploadSet('images', IMAGES)

class AdminLogin(FlaskForm):
    username = StringField('username', validators=[DataRequired()])
    password = PasswordField('password', validators=[DataRequired()])
    remember_me = BooleanField('remember', default=False)

class AdminReg(FlaskForm):
    username = StringField('username', validators=[DataRequired()])
    email = StringField('email', validators=[DataRequired()])
    password = PasswordField('password', validators=[DataRequired()])


class AdminWrite(FlaskForm):
    title = StringField('title', validators=[DataRequired()])
    time = StringField('datetime', validators=[DataRequired()])
    tags = StringField('tag')
    category = StringField('category', validators=[DataRequired()])
    url_name = StringField('urlName', validators=[DataRequired()])
    body = TextAreaField('body', validators=[DataRequired()])

    paymode = BooleanField('paymode',default=False)
    coins = StringField('coins',default=0)

    save_draft = SubmitField('save')
    submit = SubmitField('submit')

class AddPageForm(FlaskForm):
    title = StringField('title', validators=[DataRequired()])
    url_name = StringField('url_name', validators=[DataRequired()])
    body = TextAreaField('body', validators=[DataRequired()])
    can_comment = BooleanField('can_comment')
    is_nav = BooleanField('is_nav')
    submit = SubmitField('submit')

class SocialLinkForm(FlaskForm):
    link = StringField('url', validators=[DataRequired()])
    name = StringField('name', validators=[DataRequired()])
    submit = SubmitField('submit')

class FriendLinkForm(FlaskForm):
    link = StringField('url', validators=[DataRequired()])
    name = StringField('name', validators=[DataRequired()])
    info = StringField('info', validators=[DataRequired()])
    submit2 = SubmitField('submit2')

class AdminSiteForm(FlaskForm):
    photo = FileField('image', validators=[FileAllowed(['jpg','jpeg'], '仅限.jpg格式')])
    ico = FileField('ico', validators=[FileAllowed(['ico',], '仅限.ico格式')])
    site_name = StringField('name', validators=[DataRequired()])
    site_title = StringField('title', validators=[DataRequired()])
    site_url = StringField('site_url', validators=[DataRequired()])
    username = StringField('username', validators=[DataRequired()])
    token = StringField('token')
    tongji = StringField('tongji')
    profile = StringField('profile', validators=[DataRequired()])
    record_info = StringField('record info')

class ShuoForm(FlaskForm):
    shuoshuo = TextAreaField('shuoshuo', validators=[DataRequired()])


###回复评论
class CommentForm(FlaskForm):
    comment = TextAreaField('comment', validators=[DataRequired()])


# 专题表单 start
class ColumnForm(FlaskForm):
    column = StringField('column', validators=[DataRequired()])
    date = StringField('datetime', validators=[DataRequired()])
    url_name = StringField('urlName', validators=[DataRequired()])
    password = StringField('password')
    body = TextAreaField('body', validators=[DataRequired()])
    submit = SubmitField('submit')

class ColumnArticleForm(FlaskForm):
    title = StringField('title', validators=[DataRequired()])
    date = StringField('datetime', validators=[DataRequired()])
    body = TextAreaField('body', validators=[DataRequired()])
    secrecy = BooleanField('secrecy')
    submit = SubmitField('submit')
    save_draft = SubmitField('save')
# end

# 侧栏插件表单
class SideBoxForm(FlaskForm):
    title = StringField('title')
    body = TextAreaField('body', validators=[DataRequired()])
    is_advertising = BooleanField('is_advertising')
    submit = SubmitField('submit')

# 更改密码
class ChangePasswordForm(FlaskForm):
    old_password = PasswordField('Old password', validators=[DataRequired()])
    password = PasswordField('New password', validators=[ DataRequired()])
    password2 = PasswordField('Confirm new password', validators=[DataRequired()])


####
class BuyCoinForm(FlaskForm):
    coins=SelectField('coins', choices=[('10', '10金币'), ('50', '50金币'), ('100', '100金币'), ('500', '500金币'), ('1000', '1000金币')])


