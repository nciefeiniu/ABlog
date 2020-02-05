from .base_view import *

@admin.route('/add-page', methods=['GET', 'POST'])
@login_required
@admin_required
def add_page():
    form = AddPageForm()
    if form.validate_on_submit():
        page = Page(title=form.title.data,
                    url_name=form.url_name.data,
                    body=form.body.data,
                    canComment=form.can_comment.data,
                    isNav=form.is_nav.data)
        db.session.add(page)
        db.session.commit()
        flash('添加成功')
        if page.isNav is True:
            # 清除缓存
            clean_cache('global')
        return redirect(url_for('admin.add_page'))
    return render_template('admin/admin_add_page.html',
                           form=form,
                           title='添加页面')

@admin.route('/edit-page/<id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_page(id):
    page = Page.query.filter_by(id=id).first()
    start_title = page.title
    form = AddPageForm()
    if form.validate_on_submit():
        page.title = form.title.data
        page.body = form.body.data
        page.canComment = form.can_comment.data
        page.isNav = form.is_nav.data
        page.url_name = form.url_name.data
        db.session.add(page)
        db.session.commit()
        flash('更新成功')
        # 清除缓存
        clean_cache('global')
        return redirect(url_for('admin.edit_page', id=page.id))
    else:
        if len(form.errors.items())>0:
            flash(form.errors)
    form.title.data = start_title
    form.body.data = page.body
    form.can_comment.data = page.canComment
    form.is_nav.data = page.isNav
    form.url_name.data = page.url_name
    return render_template('admin/admin_add_page.html',
                           title="编辑页面",
                           form=form,
                           page=page)

@admin.route('/page/delete/<id>')
@login_required
@admin_required
def delete_page(id):
    page = Page.query.filter_by(id=id).first()
    db.session.delete(page)
    db.session.commit()
    flash('删除成功')
    if page.isNav is True:
        # 清除缓存
        clean_cache('global')
    return redirect(url_for('admin.admin_pages'))

@admin.route('/pages')
@login_required
@admin_required
def admin_pages():
    pages = Page.query.order_by(Page.id.desc()).all()
    return render_template('admin/admin_page.html',
                           pages=pages,
                           title='管理页面')

