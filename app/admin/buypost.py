from .base_view import *



##购买金币
@admin.route('/buycoins', methods=['GET', 'POST'])
@login_required
def buycoins():
    form = BuyCoinForm()
    if form.validate_on_submit():
        Referer=request.headers.get("Referer")
        try:
            pid=re.findall('pid=(\d+)',Referer)[0]
            frompage=url_for('main.post',pid=pid)
        except:
            frompage='/'
        tradeid=str(int(time.time()*1000))+''.join(random.sample(strs,random.randint(5,8)))
        money=int(form.coins.data)*10
        site_url=Admin.query.filter_by(id=1).first().site_url
        notify_url=site_url+url_for('admin.payjs_notify')
        info='购买{}金币'.format(form.coins.data)
        qrurl=getqr(money,tradeid,info,notify_url)
        s=BuyCoinHistory(trade_id=tradeid,total_fee=money,type='wechat',uid=current_user.id,frompage=frompage)
        s.url=qrurl
        db.session.add(s)
        db.session.commit()
        return redirect(url_for('admin.showqr',tradeid=tradeid))
    else:
        if len(form.errors.items())>0:
            flash(form.errors)
    return render_template('admin/buycoins.html', form=form,title='购买金币')

@admin.route('/showqr', methods=['GET'])
@login_required
def showqr():
    tradeid=request.args.get('tradeid')
    if tradeid is None:
        return redirect(url_for('main.index'))
    t=BuyCoinHistory.query.filter_by(trade_id=tradeid).first()
    if t is None:
        return redirect(url_for('main.index'))
    # url=urllib.quote(t.url)
    url=t.url
    return render_template('admin/showqr.html', url=url,tradeid=tradeid,frompage=t.frompage,title='支付页面')


@admin.route('/payjs_notify',methods=['POST'])
def payjs_notify():
    tradeid = request.form.get('out_trade_no')
    return_code = request.form.get('return_code', type=int)
    if return_code == 1:
        t=BuyCoinHistory.query.filter_by(trade_id=tradeid).first()
        t.endtime=datetime.datetime.now()
        t.status=True
        user=Admin.query.filter_by(id=t.uid).first()
        user.coins+=int(t.total_fee/10)
        db.session.add(t)
        db.session.add(user)
        db.session.commit()
        return 'success'
    else:
        return 'fail'

@admin.route('/pay_status/<tradeid>')
def pay_status(tradeid):
    t=BuyCoinHistory.query.filter_by(trade_id=tradeid).first()
    return jsonify({'status':t.status})

#购买文章
@admin.route('/buy_post', methods=['POST'])
@login_required
def buy_post():
    data=json.loads(request.get_data().decode())
    pid=data['pid']
    uid=current_user.id
    post=Post.query.filter_by(id=pid).first()
    if current_user.coins>=post.coins:
        s=BuyHistory(uid=uid,pid=pid,type='post')
        user=Admin.query.filter_by(id=uid).first()
        user.coins-=post.coins
        db.session.add(s)
        db.session.add(user)
        db.session.commit()
        return jsonify('ok')
    else:
        return abort(403)


#用户购买过的文章
@admin.route('/posts_buy')
@login_required
def posts_buy():
    pids=BuyHistory.query.filter_by(uid=current_user.id).all()
    posts=[Post.query.filter_by(id=p.pid).first() for p in pids]
    return render_template('admin/posts_buy.html',
                           title='购买过的文章',
                           posts=posts)
