from .base_view import *


@admin.route('/setting', methods=['GET', 'POST'])
@login_required
@admin_required
def set_site():
    form = AdminSiteForm(CombinedMultiDict((request.files, request.form)))
    user = Admin.query.all()[0]
    if form.validate_on_submit():
        #头像
        f = form.photo.data
        if f is not None:
            filepath=os.path.join(current_app.root_path, 'static/images/touxiang.jpg')
            f.save(filepath)
        #favicon.ico
        ico = form.ico.data
        if ico is not None:
            filepath=os.path.join(current_app.root_path, 'static/favicon.ico')
            ico.save(filepath)


        user.name = form.username.data
        user.profile = form.profile.data
        user.site_name = form.site_name.data
        user.site_title = form.site_title.data
        user.site_url = form.site_url.data
        user.tongji = form.tongji.data
        user.smms_token = form.token.data
        user.record_info = form.record_info.data or None
        db.session.add(user)
        db.session.commit()
        flash('设置成功')
        # 清除所有缓存
        clean_cache('global')
        return redirect(url_for('admin.set_site'))
    else:
        if len(form.errors.items())>0:
            flash(form.errors)
    form.username.data = user.name
    form.profile.data = user.profile
    form.token.data = user.smms_token
    form.site_name.data = user.site_name
    form.site_title.data = user.site_title
    form.site_url.data = user.site_url
    form.tongji.data = user.tongji
    form.record_info.data = user.record_info or None
    return render_template('admin/admin_profile.html',
                           title='设置网站信息',
                           form=form)

@admin.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    form = ChangePasswordForm()
    if form.validate_on_submit():
        if current_user.verify_password(form.old_password.data):
            if form.password.data == form.password2.data:
                current_user.password = form.password.data
                db.session.add(current_user)
                flash('密码更改成功')
                return redirect(url_for('admin.set_site'))
            flash('请确认密码是否一致')
            return redirect(url_for('admin.change_password'))
        flash('请输入正确的密码')
        return redirect(url_for('admin.change_password'))
    else:
        if len(form.errors.items())>0:
            flash(form.errors)
    return render_template('admin/change_password.html', form=form,
                           title='更改密码')
