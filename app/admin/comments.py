from .base_view import *
from ..utils import get_comments

@admin.route('/comments')
@login_required
@admin_required
def admin_comments():
    page = request.args.get('page', 1, type=int)
    pagination = Comment.query.order_by(Comment.id.desc()).paginate(
        page, per_page=current_app.config['ADMIN_COMMENTS_PER_PAGE'],
        error_out=False
    )
    comments = pagination.items
    return render_template('admin/admin_comment.html', title='管理评论',
                        comments=comments, pagination=pagination)

@admin.route('/delete/comment/<int:id>')
@login_required
@admin_required
def delete_comment(id):
    comment = Comment.query.get_or_404(id)
    page = comment.page
    post = comment.post
    article = comment.article
    db.session.delete(comment)
    db.session.commit()
    flash('删除成功')

    if comment.disabled is True:
        if page and page.url_name == 'guest-book':
            # 清除缓存
            update_global_cache('guestbookCounts', 1, '-')
            cache.delete_memoized(get_comments,None,page.id,None)
        elif post and isinstance(post, Post):
            # 删除文章缓存
            cache_key = '$#$#'.join(map(str, ['post', post.id]))
            post_cache = cache.get(cache_key)
            post_cache['comment_count'] -= 1
            cache.set(cache_key, post_cache)
            cache.delete_memoized(get_comments,post.id,None,None)
        elif article:
            cache.delete_memoized(get_comments,None,None,article.id)

    return redirect(url_for('admin.admin_comments'))

@admin.route('/allow/comment/<int:id>')
@login_required
@admin_required
def allow_comment(id):
    comment = Comment.query.get_or_404(id)
    comment.disabled = True
    db.session.add(comment)
    db.session.commit()
    flash('允许通过')

    # 发送邮件
    admin_mail = current_app.config['ADMIN_MAIL']

    if comment.isReply:
        reply_to_comment = Comment.query.get_or_404(comment.parent_id)
        reply_email = reply_to_comment.email
    page = comment.page
    post = comment.post
    article = comment.article
    if page and page.url_name == 'guest-book':
        # 清除缓存
        update_global_cache('guestbookCounts', 1, '+')
        cache.delete_memoized(get_comments,None,page.id,None)
    elif post and isinstance(post, Post):
        # 更新文章缓存
        cache_key = '$#$#'.join(map(str, ['post', post.id]))
        post_cache = cache.get(cache_key)
        if post_cache:
            post_cache['comment_count'] += 1
            cache.set(cache_key, post_cache)
        cache.delete_memoized(get_comments,post.id,None,None)
    elif article:
        cache.delete_memoized(get_comments,None,None,article.id)
    return redirect(url_for('admin.admin_comments'))

@admin.route('/unable/comment/<int:id>')
@login_required
@admin_required
def unable_comment(id):
    comment = Comment.query.get_or_404(id)
    comment.disabled = False
    db.session.add(comment)
    db.session.commit()
    flash('隐藏成功')

    page = comment.page
    post = comment.post
    article = comment.article
    if page and page.url_name == 'guest-book':
        # 清除缓存
        update_global_cache('guestbookCounts', 1, '-')
        cache.delete_memoized(get_comments,None,page.id,None)
    elif post and isinstance(post, Post):
        # 更新文章缓存
        cache_key = '$#$#'.join(map(str, ['post', post.id]))
        post_cache = cache.get(cache_key)
        if post_cache:
            post_cache['comment_count'] -= 1
            cache.set(cache_key, post_cache)
        cache.delete_memoized(get_comments,post.id,None,None)
    elif article:
        cache.delete_memoized(get_comments,None,None,article.id)
    return redirect(url_for('admin.admin_comments'))


@admin.route('/reply/comment/<int:id>',methods=['POST','GET'])
@login_required
@admin_required
def reply_comment(id):
    old_comment=Comment.query.get_or_404(id)
    form = CommentForm()
    if form.validate_on_submit():
        admin=Admin.query.filter_by(id=1).first()
        # 站点链接
        base_url = admin.site_url
        #是否管理员评论
        disabled=True

        nickname = admin.name
        email = admin.email
        website = admin.site_url
        com = form.comment.data.replace('<', '&lt;').replace('>', '&gt;')\
            .replace('"', '&quot;').replace('\'', '&apos;')
        replyTo = id
        replyName = old_comment.author
        comment = Comment(comment=com, author=nickname,email=email,
                              website=website, isReply=True, parent_id=replyTo)
        comment.post_id=old_comment.post_id
        comment.page_id=old_comment.page_id
        comment.article_id=old_comment.article_id
        comment.disabled=disabled
        db.session.add(comment)
        db.session.commit()
        flash('回复成功')
        #删除缓存
        page = comment.page
        post = comment.post
        article = comment.article
        if page and page.url_name == 'guest-book':
            # 清除缓存
            update_global_cache('guestbookCounts', 1, '-')
            cache.delete_memoized(get_comments,None,page.id,None)
        elif post and isinstance(post, Post):
            # 更新文章缓存
            cache_key = '$#$#'.join(map(str, ['post', post.id]))
            post_cache = cache.get(cache_key)
            if post_cache:
                post_cache['comment_count'] -= 1
                cache.set(cache_key, post_cache)
            cache.delete_memoized(get_comments,post.id,None,None)
        elif article:
            cache.delete_memoized(get_comments,None,None,article.id)
        return redirect(url_for('admin.admin_comments'))
    else:
        if len(form.errors.items())>0:
            flash(form.errors)
    return render_template('admin/admin_reply_comment.html',
                           title='回复评论', form=form,id=id)
