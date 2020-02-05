from flask import send_from_directory,current_app
import os
from . import main


@main.route('/sitemap.xml')
def sitemap():
    return send_from_directory('static', 'sitemap.xml')

@main.route('/robots.txt')
def robots():
    return send_from_directory('static', 'robots.txt')

@main.route('/atom.xml')
def rss():
    return send_from_directory('static', 'atom.xml')

@main.route('/favicon.ico')
def favicon():
    resp=send_from_directory('static', 'favicon.ico')
    # lastmodtime=os.path.getmtime(os.path.join(current_app.root_path,'static/favicon.ico'))
    # resp.set_etag(str(lastmodtime))
    return resp


# @main.route('/static/<filename>')
# def get_file(filename):
#     resp=send_from_directory('static', filename)
#     # lastmodtime=os.path.getmtime(os.path.join(current_app.root_path,'static/{0}'.format(filename)))
#     # resp.set_etag(str(lastmodtime))
#     return resp

