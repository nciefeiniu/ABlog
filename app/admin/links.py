from .base_view import *


@admin.route('/links', methods=['GET', 'POST'])
@login_required
@admin_required
def add_link():
    form = SocialLinkForm()
    fr_form = FriendLinkForm()
    # 社交链接
    if form.submit.data and form.validate_on_submit():
        exist_link = SiteLink.query.filter_by(link=form.link.data).first()
        if exist_link:
            flash('链接已经存在哦...')
            return redirect(url_for('admin.add_link'))
        else:
            url = form.link.data
            name = form.name.data
            link = SiteLink(link=url, name=name, isFriendLink=False)
            db.session.add(link)
            db.session.commit()
            flash('添加成功')
            # update cache
            clean_cache('global')
            return redirect(url_for('admin.add_link'))
    else:
        if len(form.errors.items())>0:
            flash(form.errors)
    # 友链
    if fr_form.submit2.data and fr_form.validate_on_submit():
        exist_link = SiteLink.query.filter_by(link=fr_form.link.data).first()
        if exist_link:
            flash('链接已经存在哦...')
            return redirect(url_for('admin.add_link'))
        else:
            link = SiteLink(link=fr_form.link.data, name=fr_form.name.data,
                            info=fr_form.info.data, isFriendLink=True)
            db.session.add(link)
            db.session.commit()
            flash('添加成功')
            # update cache
            update_global_cache('friendCounts', 1, '+')
            return redirect(url_for('admin.add_link'))
    else:
        if len(form.errors.items())>0:
            flash(form.errors)
    return render_template('admin/admin_add_link.html', title="站点链接",
                           form=form, fr_form=fr_form)

@admin.route('/admin-links')
@login_required
@admin_required
def admin_links():
    links = SiteLink.query.order_by(SiteLink.id.desc()).all()
    social_links = [link for link in links if link.isFriendLink is False]
    friend_links = [link for link in links if link.isFriendLink is True]
    return render_template('admin/admin_link.html', title="管理链接",
                           social_links=social_links, friend_links=friend_links)

@admin.route('/delete/link/<int:id>')
@login_required
@admin_required
def delete_link(id):
    link = SiteLink.query.get_or_404(id)
    db.session.delete(link)
    db.session.commit()
    # update cache
    if link.isFriendLink is True:
        update_global_cache('friendCounts', 1, '+')
    else:
        clean_cache('global')

    return redirect(url_for('admin.admin_links'))

@admin.route('/great/link/<int:id>')
@login_required
@admin_required
def great_link(id):
    link = SiteLink.query.get_or_404(id)
    if link.isGreatLink:
        link.isGreatLink = False
    else:
        link.isGreatLink = True
    db.session.add(link)
    db.session.commit()
    # 清除缓存
    clean_cache('global')
    return redirect(url_for('admin.admin_links'))
