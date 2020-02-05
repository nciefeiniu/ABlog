from .base_view import *

# 侧栏box---begin
@admin.route('/add/sidebox', methods=['GET', 'POST'])
@login_required
@admin_required
def add_side_box():
    form = SideBoxForm()
    if form.validate_on_submit():
        is_advertising = form.is_advertising.data
        box = SideBox(title=form.title.data, body=form.body.data,
                      is_advertising=is_advertising)
        db.session.add(box)
        db.session.commit()
        flash('添加侧栏插件成功')
        # update cache
        clean_cache('global')
        return redirect(url_for('admin.admin_side_box'))
    else:
        if len(form.errors.items())>0:
            flash(form.errors)
    return render_template('admin/admin_edit_sidebox.html', form=form,
                           title='添加插件')


@admin.route('/edit/sidebox/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_side_box(id):
    box = SideBox.query.get_or_404(id)
    form = SideBoxForm()
    if form.validate_on_submit():
        box.title = form.title.data
        box.body = form.body.data
        box.is_advertising = form.is_advertising.data
        db.session.add(box)
        db.session.commit()
        flash('更新侧栏插件成功')
        # update cache
        clean_cache('global')
        return redirect(url_for('admin.admin_side_box'))
    else:
        if len(form.errors.items())>0:
            flash(form.errors)
    form.title.data = box.title
    form.body.data = box.body
    form.is_advertising.data = box.is_advertising
    return render_template('admin/admin_edit_sidebox.html', form=form,
                           title='更新插件', box=box)


@admin.route('/sideboxs')
@login_required
@admin_required
def admin_side_box():
    boxes = SideBox.query.order_by(SideBox.id.desc()).all()
    return render_template('admin/admin_sidebox.html', boxes=boxes, title='管理插件')


@admin.route('/unable/box/<int:id>')
@login_required
@admin_required
def unable_side_box(id):
    box = SideBox.query.get_or_404(id)
    if box.unable:
        box.unable = False
    else:
        box.unable = True
    db.session.add(box)
    db.session.commit()
    # 清除缓存
    clean_cache('global')
    return redirect(url_for('admin.admin_side_box'))


@admin.route('/delete/box/<int:id>')
@login_required
@admin_required
def delete_side_box(id):
    box = SideBox.query.get_or_404(id)
    db.session.delete(box)
    db.session.commit()
    flash('删除插件成功')
    # 清除缓存
    clean_cache('global')
    return redirect(url_for('admin.admin_side_box'))
# 侧栏box---end
