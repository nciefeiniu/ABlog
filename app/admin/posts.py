from .base_view import *

@admin.route('/posts')
@login_required
@admin_required
def admin_posts():
    page = request.args.get('page', 1, type=int)
    pagination = Post.query.filter_by(draft=False).order_by(Post.id.desc()).paginate(
        page, per_page=current_app.config['ADMIN_POSTS_PER_PAGE'],
        error_out=False
    )
    posts = pagination.items
    return render_template('admin/admin_post.html',
                           title='管理文章',
                           posts=posts,
                           pagination=pagination)


@admin.route('/write', methods=['GET', 'POST'])
@login_required
@admin_required
def write():
    form = AdminWrite()
    if form.validate_on_submit():
        # 保存草稿
        if 'save_draft' in request.form and form.validate():
            post = save_post(form, True)
            db.session.add(post)
            flash('保存成功！')
        # 发布文章
        elif 'submit' in request.form and form.validate():
            post = save_post(form)
            db.session.add(post)
            flash('发布成功！')
            # updata cache
            clean_cache('global')
            update_first_cache()
        db.session.commit()
        return redirect(url_for('admin.admin_edit',id=post.id))
    else:
        if len(form.errors.items())>0:
            flash(form.errors)
    post=Empty()
    return render_template('admin/admin_write.html',
                           form=form, title='写文章',post=post)

# 编辑文章或草稿
@admin.route('/edit/<id>', methods=['GET', 'POST'])
@login_required
@admin_required
def admin_edit(id):
    # timestamp = str(time)[0:4] + '-' + str(time)[4:6] + '-' + str(time)[6:8]
    post = Post.query.filter_by(id=id).first()

    form = AdminWrite()
    if form.validate_on_submit():
        category = Category.query.filter_by(category=form.category.data).first()
        post.category = category
        post.tags = form.tags.data
        post.url_name = form.url_name.data
        post.lstModTime = datetime.datetime.now().strftime('%Y-%m-%d')
        post.coins = form.coins.data
        post.paymode = form.paymode.data
        post.title = form.title.data
        post.body = form.body.data
        # 编辑草稿
        if post.draft is True:
            if 'save_draft' in request.form and form.validate():
                db.session.add(post)
                flash('保存成功！')
            elif 'submit' in request.form and form.validate():
                post.draft = False
                db.session.add(post)
                db.session.commit()
                update_meta()
                flash('发布成功')
                # 清除缓存
                clean_cache('global')
                update_first_cache()
                # 更新 xml
                update_xml(post.lstModTime)
            return redirect(url_for('admin.admin_edit', id=post.id))
        # 编辑文章
        else:
            db.session.add(post)
            db.session.commit()
            update_meta()
            flash('更新成功')
            # 清除对应文章缓存
            key = '$#$#'.join(map(str, ['post', post.id]))
            clean_cache(key)
            update_xml(post.lstModTime)
            return redirect(url_for('admin.admin_edit', id=post.id))
    else:
        if len(form.errors.items())>0:
            flash(form.errors)
    form.category.data = post.category.category
    form.tags.data = post.tags
    form.url_name.data = post.url_name
    form.time.data = post.timestamp
    form.title.data = post.title
    form.coins.data = post.coins
    form.paymode.data = post.paymode
    form.body.data = post.body
    return render_template('admin/admin_write.html',
                           form=form, post=post, title='编辑文章')


@admin.route('/draft')
@login_required
def admin_drafts():
    drafts = Post.query.filter_by(draft=True).order_by(Post.id.desc()).all()
    return render_template('admin/admin_draft.html',
                           drafts=drafts,
                           title='管理草稿')

@admin.route('/delete/<id>')
@login_required
@admin_required
def delete_post(id):
    post = Post.query.filter_by(id=id).first()
    db.session.delete(post)
    db.session.commit()
    update_meta()
    flash('删除成功')
    # update cache
    if post.draft is False:
        update_global_cache('postCounts', 1, '-')
    return redirect(url_for('admin.admin_posts'))
