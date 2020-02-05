from .base_view import *



# 管理专栏
@admin.route('/write/column', methods=['GET','POST'])
@login_required
@admin_required
def write_column():
    form = ColumnForm()
    if form.validate_on_submit():
        column = Column(column=form.column.data, timestamp=form.date.data,
                        url_name=form.url_name.data, body=form.body.data,
                        password=form.password.data)
        db.session.add(column)
        db.session.commit()
        flash('专题发布成功！')
        return redirect(url_for('admin.admin_column', id=column.id))
    return render_template('admin_column/edit_column.html',
                           form=form, title='编辑专题')

@admin.route('/edit/column/<int:id>', methods=['GET','POST'])
@login_required
@admin_required
def edit_column(id):
    column = Column.query.get_or_404(id)
    form = ColumnForm()
    if form.validate_on_submit():
        column.column = form.column.data
        column.timestamp = form.date.data
        column.url_name = form.url_name.data
        column.body = form.body.data
        password = form.password.data
        if password:
            column.password = password
        db.session.add(column)
        db.session.commit()
        flash('专题更新成功！')
        return redirect(url_for('admin.admin_column', id=column.id))

    form.column.data = column.column
    form.date.data = column.timestamp
    form.url_name.data = column.url_name
    form.body.data = column.body
    return render_template('admin_column/edit_column.html',
                           form=form, title='更新专题', column=column)

@admin.route('/admin/columns')
@login_required
@admin_required
def admin_columns():
    columns = Column.query.all()
    return render_template('admin_column/admin_columns.html',
                           columns=columns, title='管理专题')

@admin.route('/admin/column/<int:id>')
@login_required
@admin_required
def admin_column(id):
    column = Column.query.get_or_404(id)
    articles = column.articles.order_by(Article.id.desc()).all()
    return render_template('admin_column/admin_column.html', column=column,
                           articles=articles, title=column.column)

@admin.route('/delete/column/<int:id>')
@login_required
@admin_required
def delete_column(id):
    column = Column.query.get_or_404(id)
    articles = column.articles.order_by(Article.id.desc()).all()
    db.session.delete(column)
    db.session.commit()
    flash('删除专题')
    # clean all of this column cache
    clean_cache('column$#$#' + column.url_name)
    for i in articles:
        clean_cache('$#$#'.join(['article', column.url_name, str(i.id)]))
    return redirect(url_for('admin.admin_columns'))

@admin.route('/<url>/write/article', methods=['GET','POST'])
@login_required
@admin_required
def write_column_article(url):
    column = Column.query.filter_by(url_name=url).first()
    form = ColumnArticleForm()
    if form.validate_on_submit():
        article = Article(title=form.title.data, timestamp=form.date.data,
                          body=form.body.data, secrecy=form.secrecy.data, column=column)
        if 'save_draft' in request.form:
            article.draft=True
        else:
            article.draft=False
        db.session.add(article)
        db.session.commit()
        flash('添加文章成功！')
        # clean cache
        clean_cache('column$#$#' + url)
        return redirect(url_for('admin.admin_column', id=column.id))
    else:
        if len(form.errors.items())>0:
            flash(form.errors)
    post=Empty()
    return render_template('admin_column/write_article.html', form=form,
                           title='编辑文章', column=column,article=post)

@admin.route('/<url>/edit/article/<int:id>', methods=['GET','POST'])
@login_required
@admin_required
def edit_column_article(url, id):
    column = Column.query.filter_by(url_name=url).first()
    article = Article.query.filter_by(id=id).first()
    _title = article.title

    form = ColumnArticleForm()
    if form.validate_on_submit():
        article.title = form.title.data
        article.timestamp = form.date.data
        article.secrecy = form.secrecy.data
        article.body = form.body.data
        if 'save_draft' in request.form:
            article.draft=True
        else:
            article.draft=False
        db.session.add(article)
        db.session.commit()
        flash('更新文章成功！')
        # clear cache
        clean_cache('$#$#'.join(['article', url, str(id)]))
        if article.title != _title:
            # the title is change
            clean_cache('column$#$#' + url)
        return redirect(url_for('admin.admin_column', id=column.id))
    else:
        if len(form.errors.items())>0:
            flash(form.errors)

    form.title.data = article.title
    form.date.data = article.timestamp
    form.body.data = article.body
    form.secrecy.data = article.secrecy
    return render_template('admin_column/write_article.html', form=form,
                           title='更新文章', column=column, article=article)

@admin.route('/<url>/delete/article/<int:id>')
@login_required
@admin_required
def delete_column_article(url, id):
    column = Column.query.filter_by(url_name=url).first()
    article = Article.query.filter_by(id=id).first()
    db.session.delete(article)
    db.session.commit()
    flash('删除文章成功！')
    # 清除对于缓存
    clean_cache('$#$#'.join(['article', url, str(id)]))
    clean_cache('column$#$#' + url)
    return redirect(url_for('admin.admin_column', id=column.id))
