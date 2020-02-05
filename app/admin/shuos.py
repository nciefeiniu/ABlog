from .base_view import *


####说说
@admin.route('/write/shuoshuo', methods=['GET','POST'])
@login_required
@admin_required
def write_shuoshuo():
    form = ShuoForm()
    if form.validate_on_submit():
        shuo = Shuoshuo(shuo=form.shuoshuo.data)
        db.session.add(shuo)
        db.session.commit()
        flash('发布成功')
        # 清除缓存
        update_global_cache('newShuo', shuo.body_to_html)
        return redirect(url_for('admin.write_shuoshuo'))
    return render_template('admin/admin_write_shuoshuo.html',
                           title='写说说', form=form)

@admin.route('/shuos')
@login_required
@admin_required
def admin_shuos():
    shuos = Shuoshuo.query.order_by(Shuoshuo.id.desc()).all()
    return render_template('admin/admin_shuoshuo.html',
                           title='管理说说',
                           shuos=shuos)

@admin.route('/delete/shuoshuo/<int:id>')
@login_required
@admin_required
def delete_shuo(id):
    shuo = Shuoshuo.query.get_or_404(id)
    db.session.delete(shuo)
    db.session.commit()
    flash('删除成功')

    # update cache
    new_shuo = Shuoshuo.query.order_by(Shuoshuo.id.desc()).first()
    value = new_shuo.body_to_html if new_shuo else '这家伙啥都不想说...'
    update_global_cache('newShuo', value)
    return redirect(url_for('admin.admin_shuos'))
