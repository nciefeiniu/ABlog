import os
import re
import time
import random
import json
import string
import subprocess
from flask import render_template, redirect, request, flash, current_app, url_for,abort,jsonify
from flask_login import login_required, login_user, logout_user, current_user
from werkzeug.utils import secure_filename
from werkzeug.datastructures import CombinedMultiDict
import datetime
from .. import cache
from ..models import *
from . import admin
from .forms import *
from ..utils import *
from ..payjs import getqr
import urllib.parse as urllib
from ..smms_picbed import *

strs=string.ascii_letters+string.digits


class Empty(object):
    """docstring for Empty"""
    id=None
    timestamp=None

def update_meta():
    cmd='python {}/countnum.py'.format(current_app.root_path)
    subprocess.Popen(cmd,shell=True)

def clean_cache(key):
    """
    在发布文章后删除首页，归档，分类，标签缓存，
    在更新文章后删除对应文章缓存
    在添加说说，更改友链页后删除对应缓存
    :param key: cache prefix
    """
    if key == 'all':
        cache.clear()
    elif key != 'all' and cache.get(key):
        cache.delete(key)
    else:
        return False

def update_global_cache(key, value, method=None):
    """
    update sidebar global cache
    : param key: dict key
    : param kwargs: key, value, method
    """
    global_cache = cache.get('global')
    if global_cache is None:
        return False
    if method == '+':
        value = value if isinstance(value, int) else 1
        global_cache[key] += value
    elif method == '-':
        value = value if isinstance(value, int) else 1
        global_cache[key] -= value
    else:
        global_cache[key] = value
    cache.set('global', global_cache)

    return True

def update_first_cache():
    """
    update first post behind commit article
    """
    posts = Post.query.order_by(Post.id.desc()).all()
    if len(posts) > 1:
        first_post = posts[1]
        cache_key = '$#$#'.join(map(str, ['post', first_post.id]))
        clean_cache(cache_key)
    return True

def save_tags(tags):
    """
    保存标签到模型
    :param tags: 标签集合，创建时间，文章ID
    """
    for tag in tags:
        exist_tag = Tag.query.filter_by(tag=tag).first()
        if not exist_tag:
            tag = Tag(tag=tag)
            db.session.add(tag)
    db.session.commit()

def save_post(form, draft=False):
    """
    封装保存文章到数据库的重复操作
    :param form: write or edit form
    :param draft: article is or not draft
    :return: post object
    """
    category = Category.query.filter_by(category=form.category.data).first()
    if not category:
        category = Category(category=form.category.data)
        db.session.add(category)

    tags = [tag for tag in form.tags.data.split(',')]
    post = Post(body=form.body.data
                ,title=form.title.data
                ,coins=form.coins.data
                ,paymode=form.paymode.data
                ,url_name=form.url_name.data
                ,category=category
                ,tags=form.tags.data
                ,timestamp=form.time.data
                ,lastModTime=form.time.data)
    if draft is True:
        post.draft=True
    else:
        post.draft=False
        update_meta()
        # 保存标签模型
        save_tags(tags)
        # 更新xml
        update_xml(post.timestamp)
    return post

# 编辑文章后更新sitemap
def update_xml(update_time):
    # 获取配置信息
    author_name = current_app.config['ADMIN_NAME']
    title = current_app.config['SITE_NAME']
    subtitle = current_app.config['SITE_TITLE']
    protocol = current_app.config['WEB_PROTOCOL']
    url = current_app.config['WEB_URL']
    web_time = current_app.config['WEB_START_TIME']
    count = current_app.config['RSS_COUNTS']
    site_url=Admin.query.first().site_url
    posts = Post.query.filter_by(draft=False).order_by(Post.id.desc()).all()
    # sitemap
    sitemap = get_sitemap(site_url,posts)
    save_file(sitemap, 'sitemap.xml')
    # rss
    rss_posts = posts[:count]
    rss = get_rss_xml(author_name, site_url, title, subtitle, web_time, update_time, rss_posts)
    save_file(rss, 'atom.xml')
