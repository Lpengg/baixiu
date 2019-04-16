from . import users

from flask import render_template,request,session,redirect,make_response

from ..models import *

import base64,os,datetime,math

@users.route('/admin/login' ,methods=['POST','GET'])
def login_views():
    if request.method == 'GET':
        # 如果cookie中存有账号密码，那就把账号密码自动填入
        if 'username' in request.cookies and 'password' in request.cookies:
            username = base64.b64decode(request.cookies['username']).decode()
            password = base64.b64decode(request.cookies['password']).decode()
        return render_template('/admin/login.html',params=locals())
    else:
        username = request.form['uname']
        password = request.form['pswd']
        user = Users.query.filter_by(username=username,password=password).first()
        if user:
            # 如果该用户存在说明登陆成功，将信息保存进session
            session['id'] = user.id
            session['username'] = user.username
            session['role'] = user.role
            resp = make_response('OK')
            if request.form['isRem'] == 'true':
                #    选择保持登陆 将账号密码存入cookie

                # 使用base64 进行密码简单的加密存入cookie中
                resp.set_cookie('username',base64.b64encode(username.encode()),60*60*24*365)
                resp.set_cookie('password',base64.b64encode(password.encode()),60*60*24*365)
                # 解码方法：base64.b64decode(request.cookies['username']).decode()
            return resp
        return '账号或密码错误'

@users.route('/admin/register',methods=['GET','POST'])
def register_user():
    # 注册用户
    user = Users()
    user.username = request.form['username']
    user.password = request.form['password']
    user.nickname = request.form['nickname']
    db.session.add(user)
    return redirect(request.headers.get('Referer','/'))

@users.route('/admin/check-name',methods=['POST','GET'])
def check_uname():
    if request.method == 'GET':
        uname = request.args.get('name')
        user = Users.query.filter_by(username=uname).first()
        if user:
            return '用户名已存在'
        else:
            return 'OK'
    else:
        nickname = request.form['name']
        user = Users.query.filter_by(nickname=nickname).first()
        if user:
            return '用户名已存在'
        else:
            return 'OK'


# 处理用户
@users.route('/admin/users',methods=['POST','GET'])
def admin_user():
    if 'id' in session and 'username' in session:
        if request.method == 'POST':
            user = Users()
            user.username = request.form['username']
            user.password = request.form['password']
            user.role ='author'
            user.nickname = '用户'+datetime.datetime.now().strftime("%m%d%H%M%S")
            user.status=True
            user.avatar='/static/assets/img/default.png'
            db.session.add(user)
            msg = '添加成功'
        page = int(request.args.get('page',1))
        size = 10  # 设定每页显示的文章数量
        condition = []

        count = db.session.query(Users).filter(*condition).count()

        totalPage = math.ceil(count / size)  # 总页数
        if page > totalPage:
            page = totalPage
        # 越过多少条取多少条数据
        users = db.session.query(Users).filter(*condition).order_by(Users.role,Users.status.desc()).offset(
            (page - 1) * size).limit(size)

        visiables = 5  # 页导航栏要显示的总数
        region = (visiables - 1) / 2

        beginPage = int(page - region)  # 开始页
        endPage = int(page + region)  # 结束页

        if beginPage < 1:
            beginPage = 1
            endPage = visiables

        if endPage > totalPage:
            endPage = totalPage
            beginPage = endPage - visiables + 1;
            if beginPage < 1:
                beginPage = 1;

        isUser = True #设置高亮标志
        user = Users.query.filter_by(id=session['id']).first()
        return render_template('/admin/users.html',params=locals())
    else:
        return redirect('/admin/login')

@users.route('/admin/users-modifyRole',methods=['POST','GET'])
def admin_users_modifyRole():
    role = request.form['role']
    id = request.form['id']
    user = Users.query.filter_by(id=id).first()
    user.role=role
    db.session.add(user)
    return 'xxx'

@users.route('/admin/users-modifyStatus',methods=['POST','GET'])
def admin_users_modifyStatus():
    status = request.form['status']
    id = request.form['id']
    user = Users.query.filter_by(id=id).first()
    if status =='0':
        user.status=False
    else:
        user.status = False
    db.session.add(user)
    return 'xxx'

@users.route('/admin/user-del')
def admin_user_del():
    id = request.args.get('id','')
    user = Users.query.filter_by(id=id).first()
    db.session.delete(user)
    return redirect(request.headers.get('Referer','/'))


# 个人设置页面
@users.route('/admin/profile',methods=['POST','GET'])
def admin_profile():
    if 'id' in session and 'username' in session:
        if request.method =='POST':
            print(request.form)
            user = Users.query.filter_by(id=session['id']).first()  #查询出当前用户的所有信息 进行修改
            # 接收数据
            user.nickname = request.form['nickname']
            user.bio = request.form['bio']

            if 'avatar' in request.files:
                f = request.files['avatar']
                fname = user.username+'-'+datetime.datetime.now().strftime("%Y%m%d%H%M%S%f") + '-' + f.filename
                fname = 'static/uploads/avatars/' + fname
                basedir = os.path.dirname(__file__)
                upload_path = os.path.join(os.path.dirname(basedir), fname)
                f.save(upload_path)
                user.avatar = '/' + fname
            db.session.add(user)
        user = Users.query.filter_by(id=session['id']).first()
        isProfile = True
        return render_template('/admin/profile.html',params=locals())
    else:
        return redirect('/admin/login')


# 修改密码页面
@users.route('/admin/password-reset',methods=['POST','GET'])
def admin_password_rest():
    if 'id' in session and 'username' in session:
        user = Users.query.filter_by(id=session['id']).first()
        isProfile=True

        return render_template('/admin/password-reset.html',params=locals())
    else:
        return redirect('/admin/login')


@users.route('/logout')
def logout():
    # 判断是否有登陆信息
    if 'id' in session and 'username' in session:
        # session存在 删除session 返回到主页
        del session['id']
        del session['username']
        return redirect('/')
    else:
        # 没有session 直接返回到主页
        return redirect('/')
