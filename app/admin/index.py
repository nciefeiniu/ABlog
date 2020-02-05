from .base_view import *


@admin.route('/')
@admin.route('/index')
@login_required
def index():
    return render_template('admin/admin_index.html')

@admin.route('/login/', methods=['GET', 'POST'])
def login():
    form = AdminLogin()
    if form.validate_on_submit():
        user = Admin.query.filter_by(login_name=form.username.data).first()
        if user is not None and user.verify_password(form.password.data):
            login_user(user, form.remember_me.data)
            return redirect(url_for('admin.index'))
    else:
        if len(form.errors.items())>0:
            flash(form.errors)
    return render_template('admin/login.html',
                           title='登录',
                           form=form)

@admin.route('/reg/', methods=['GET', 'POST'])
def reg():
    username_not_allow=['admin','root','administrator']
    form = AdminReg()
    if form.validate_on_submit():
        username=form.username.data
        email=form.email.data
        password=form.password.data
        if username.lower() not in username_not_allow \
            and email!='' and password!='' and username!='' \
            and Admin.query.filter_by(login_name=username).count()==0\
            and Admin.query.filter_by(email=email).count()==0:
            user = Admin(site_name='', site_title='',email=email,site_url='', name=username,profile='', login_name=username,password=password)
            db.session.add(user)
            db.session.commit()
            flash('注册成功')
            user=Admin.query.filter_by(login_name=username).first()
            login_user(user)
            return redirect(url_for('admin.index'))
        else:
            flash('注册出错！')
            return redirect(url_for('admin.reg'))
    else:
        if len(form.errors.items())>0:
            flash(form.errors)
    return render_template('admin/reg.html',
                           title='注册',
                           form=form)


@admin.route('/logout')
@login_required
def logout():
    logout_user()
    flash('你已经登出账号。')
    return redirect(url_for('admin.index'))
