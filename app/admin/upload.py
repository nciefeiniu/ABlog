from .base_view import *


# 上传文件到静态目录
@admin.route('/upload/file', methods=['GET', 'POST'])
@login_required
@admin_required
def upload_file():
    source_folder = current_app.config['UPLOAD_PATH']
    cur_year=datetime.datetime.now().strftime('%Y')
    cur_month=datetime.datetime.now().strftime('%m')
    folder_y=os.path.join(source_folder,cur_year)
    if not os.path.exists(folder_y):
        os.mkdir(folder_y)
    folder_m=os.path.join(folder_y,cur_month)
    if not os.path.exists(folder_m):
        os.mkdir(folder_m)
    if request.method == 'POST':
        file = request.files['file']
        filename = secure_filename(file.filename)
        path = os.path.join(folder_m, filename)
        file.save(path)
        file_url='/static/upload/{}/{}/{}'.format(cur_year,cur_month,filename)
        return redirect(url_for('admin.upload_file',file_url=file_url))
    file_url=request.args.get('file_url')
    return render_template('admin/upload_file.html', title="上传文件",file_url=file_url)



# qiniu picture bed begin
@admin.route('/qiniu/picbed', methods=['GET', 'POST'])
@login_required
@admin_required
def qiniu_picbed():
    if request.method == 'POST':
        token=current_user.smms_token
        file = request.files.get('file')
        filename = secure_filename(file.filename)
        if file.mimetype.startswith('image'):
            smms=SmmsUpload(token)
            r=smms.upload(file.stream.read())
            if r.get('code')=='success':
                flash('上传成功')
                d=SMMS(hash=r.get('data').get('hash'),url=r.get('data').get('url'))
                db.session.add(d)
                db.session.commit()
            else:
                flash(r.get('message'))
    page = request.args.get('page', 1, type=int)
    pagination = SMMS.query.order_by(SMMS.id.desc()).paginate(page, per_page=20,error_out=False)
    images = pagination.items
    return render_template('plugin/picbed.html',
                           title="七牛图床", images=images, counts=pagination.total,time=int(time.time()),pagination=pagination)

@admin.route('/qiniu/delete', methods=['GET', 'POST'])
@login_required
@admin_required
def delete_img():
    token=current_user.smms_token
    hash = request.get_json()['hash']
    smms=SmmsUpload(token)
    r=smms.delete(hash)
    d=SMMS.query.filter_by(hash=hash).first()
    db.session.delete(d)
    db.session.commit()
    flash(r.get('message'))
    return redirect(url_for('admin.qiniu_picbed'))
