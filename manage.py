#!/usr/bin/env python
import os
from app import create_app, db
from app.models import *
from flask_script import Manager, Shell
from flask_migrate import Migrate, MigrateCommand
from config import Config
import datetime
import re

def get_id(pid):
    if pid is None:
        if Post.query.count()==0:
            return 1
        else:
            p=Post.query.order_by(Post.id.desc()).first()
            return p.id+1
    else:
        return pid

def get_date(date):
    if date is None:
        return datetime.datetime.now().strftime('%Y-%m-%d')
    return date



app = create_app(os.getenv('CONFIG') or 'default')
manager = Manager(app)
migrate = Migrate(app, db)


def make_shell_context():
    return dict(app=app, db=db, Admin=Admin, Post=Post, Tag=Tag,
                Category=Category, SiteLink=SiteLink, Page=Page,
                LoveMe=LoveMe, Comment=Comment, Shuoshuo=Shuoshuo, SideBox=SideBox)


manager.add_command('shell', Shell(make_context=make_shell_context))
manager.add_command('db', MigrateCommand)


@manager.command
def clear_alembic():
    from app.models import Alembic
    Alembic.clear_A()


@manager.command
def add_admin():
    from app.models import Admin, LoveMe
    from config import Config
    # 创建管理员
    admin = Admin(site_name=Config.SITE_NAME, site_title=Config.SITE_TITLE,email=Config.ADMIN_MAIL,
                    site_url=Config.WEB_PROTOCOL+'://'+Config.WEB_URL, name=Config.ADMIN_NAME,
                  profile=Config.ADMIN_PROFILE, login_name=Config.ADMIN_NAME,
                  password=Config.ADMIN_PASSWORD)
    # 创建love-me
    love = LoveMe(loveMe=0)
    # 创建留言板
    guest_book = Page(title='留言板', url_name='guest-book', canComment=True,
                      isNav=False, body='留言板')
    db.session.add(admin)
    db.session.add(love)
    db.session.add(guest_book)
    db.session.commit()

@manager.command
def deploy():
    db.drop_all()
    db.create_all()
    add_admin()


@app.template_filter()
def cut_desc(text):
    s=text.split('<!--more-->')[0]
    s=re.sub('<.*?>','',s)[:50]+'...'
    return s


@app.template_filter()
def cut_desc_seo(text):
    s = text.split('<!--more-->')[0]
    s = re.sub('<.*?>', '', s)[:274] + '...'
    return s


@app.template_filter()
def cut_title(text):
    s=text.split('<!--more-->')[0]
    s=re.sub('<.*?>','',s)[:20]+'...'
    return s

def cut_buy(text,paymode,pid,uid):
    if not paymode:
        return text
    else:
        hasbuy=BuyHistory.query.filter_by(pid=pid,uid=uid).count()>0
        if hasbuy:
            return text
        else:
            return text.split('<!--free-->')[0]



app.jinja_env.globals['Config']=Config
app.jinja_env.globals['cut_buy']=cut_buy
app.jinja_env.globals['get_id']=get_id
app.jinja_env.globals['get_date']=get_date
app.jinja_env.globals['int']=int


if __name__ == '__main__':
    manager.run()
