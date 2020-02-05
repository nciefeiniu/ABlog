#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import datetime
from markdown import Markdown
from functools import wraps
from flask import current_app
from flask_login import current_user
from . import cache
from .models import Comment
import json

# 拼接站点地图
def get_sitemap(site_url,posts):
    header = '<?xml version="1.0" encoding="UTF-8"?> '+ '\n' + \
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
    footer = '</urlset>'
    contents = []
    body = ''
    if posts:
        for post in posts:
            content = '  <url>' + '\n' + \
                f'    <loc>{site_url}/archives/' + str(post.id) + '</loc>' + '\n' + \
                '    <lastmod>' + post.timestamp + '</lastmod>' + '\n' + \
                '  </url>'
            contents.append(content)
        for content in contents:
            body = body + '\n' + content
        sitemap = header + '\n' + body + '\n' + footer
        return sitemap
    return None

# 保存xml文件到静态文件目录
def save_file(sitemap, file):
    path = os.getcwd().replace('\\', '/')
    filename = path + '/app/static/' + file
    isExists = os.path.exists(filename)
    if not isExists:
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(sitemap)
    else:
        os.remove(filename)
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(sitemap)

# 生成 rss xml
def get_rss_xml(name, site_url, title, subtitle, time, update_time, posts):
    header = '<?xml version="1.0" encoding="UTF-8"?>' + '\n' + \
    '<feed xmlns="http://www.w3.org/2005/Atom">' + '\n' + \
      '  <title>' + title + '</title>' + '\n' + \
      '  <subtitle>' + subtitle + '</subtitle>' + '\n' + \
      '  <link rel="alternate" type="text/html" href="' + site_url + '/"/>' + '\n' + \
      '  <link href="' + site_url + '/atom.xml" rel="self"/>' + '\n' + \
      '  <id>tag:' + site_url + ',' + time + '://1</id>' + '\n' + \
      '  <updated>' + update_time + 'T00:00:00Z</updated>'
    content = []
    item = ''
    footer = '</feed>'
    if posts:
        for p in posts:
            body = '  <entry>' + '\n' + \
              '    <title>' + str(p.title) + '</title>' + '\n' + \
              '    <link rel="alternate" type="text/html" href="' + site_url + '/archives/' + str(p.id) + '"/>' + '\n' + \
              '    <id>tag:' + site_url + ',' + str(p.year) + '://1.' + str(p.id) + '</id>' + '\n' + \
              '    <published>' + str(p.timestamp) + 'T00:00:00Z</published>' + '\n' + \
              '    <updated>' + update_time + 'T00:00:00Z</updated>' + '\n' + \
              '    <summary>' + str(p.title) + '</summary>' + '\n' + \
              '    <author>' + '\n' + \
              '    <name>' + name + '</name>' + '\n' + \
              '    <uri>' + site_url + '</uri>' + '\n' + \
              '    </author>' + '\n' + \
              '    <category term="' + str(p.category.category) + '" scheme="' + site_url + '/category/' + str(p.category.category) + '"/>' + '\n' + \
              '    <content type="html"><![CDATA[' + str(p.body_to_html) + ']]></content>' + '\n' + \
            '  </entry>'
            content.append(body)
        for c in content:
            item = item + '\n' + c
        rss_xml = header + '\n' + item + '\n' + footer
        return rss_xml
    return None

# 解析markdown
def markdown_to_html(body):

    md = Markdown(extensions=['fenced_code', 'codehilite(css_class=highlight,linenums=None)',
                              'admonition', 'tables', 'extra'])
    content = md.convert(body)
    return content

class EmptyComment(object):
    id=None
    comment=None
    author=None
    email=None
    website=None
    isReply=None
    disabled=None
    timestamp=None
    gavatar=None

    parent_id=None
    parent_author=None
    parent_website=None
    parent_comment=None
    parent_gavatar=None
    parent_strptime=None

def iter_pages(pages,page, left_edge=2, left_current=2,right_current=5, right_edge=2):
    last = 0
    pgi=[]
    for num in range(1, pages + 1):
        if num <= left_edge or (num > page - left_current - 1 and num < page + right_current) or num > pages - right_edge:
            if last + 1 != num:
                pgi.append(None)
            else:
                pgi.append(num)
            last = num
    return pgi



@cache.memoize(60*60)
def get_comments(pid,page_id,article_id,page=1,key='20190813v2'):
    data={}
    max_page=1
    per_page=current_app.config['COMMENTS_PER_PAGE']
    if pid is not None:
        total_comments=Comment.query.filter_by(post_id=pid,disabled=True).order_by(Comment.id.desc()).all()
    elif page_id is not None:
        total_comments=Comment.query.filter_by(page_id=page_id,disabled=True).order_by(Comment.id.desc()).all()
    elif article_id is not None:
        total_comments=Comment.query.filter_by(article_id=article_id,disabled=True).order_by(Comment.id.desc()).all()
    max_page=len(total_comments) // per_page + 1 if len(total_comments) % per_page != 0 else len(total_comments) // per_page
    comments=total_comments[(page-1)*per_page:page*per_page]
    pagination =iter_pages(max_page,page)
    cs=[]
    for comment in comments:
        info=EmptyComment()
        info.id=comment.id
        info.comment=markdown_to_html(comment.comment)
        info.author=comment.author
        info.email=comment.email
        info.website=comment.website
        info.isReply=comment.isReply
        info.disabled=comment.disabled
        info.strptime=datetime.datetime.strftime(comment.timestamp, '%Y-%m-%d')
        info.gravatar=comment.gravatar(size=38)
        if comment.isReply==True:
            info.parent_id=comment.parent_id
            parent_comment=Comment.query.filter_by(id=comment.parent_id).first()
            info.parent_author=comment.parent.author
            info.parent_website=comment.parent.website
            info.parent_comment=markdown_to_html(comment.parent.comment)
            info.parent_strptime=datetime.datetime.strftime(comment.parent.timestamp, '%Y-%m-%d')
            info.parent_gravatar=comment.parent.gravatar(size=26)
        cs.append(info)

    data['pagination']=pagination
    data['comments']=cs
    data['total']=len(total_comments)
    data['max_page']=max_page
    return data


def admin_required(func):
    @wraps(func)
    def decorated_view(*args, **kwargs):
        if current_user.id>1:
            return abort(403)
        return func(*args, **kwargs)
    return decorated_view
