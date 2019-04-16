import json
from . import main
from flask import render_template, session, request, redirect, current_app, make_response
from sqlalchemy import or_

from ..models import *

import datetime
import os, math


@main.route('/favicon.ico')
def get_ico():
    return current_app.send_static_file('favicon.ico')

@main.route('/')
def index_views():
    if 'id' in session and 'username' in session:
        user = Users.query.filter_by(id=session['id']).first()
    # 最新发布
    new_posts = Posts.query.filter_by(status='published').order_by(Posts.created.desc()).limit(5)
    # 热门排行
    hot_posts = Posts.query.filter_by(status='published').order_by(Posts.views.desc(),Posts.likes.desc()).limit(5)
    # 点击排行
    click_posts = Posts.query.filter_by(status='published').order_by(Posts.views.desc()).offset(5).limit(8)
    return render_template('index.html',params=locals())


@main.route('/list')
def list_views():
    if 'id' in session and 'username' in session:
        user = Users.query.filter_by(id=session['id']).first()
    # 获取前端传递过来的分类
    cate_slug = request.args.get('cate')
    cate = Categories.query.filter_by(slug=cate_slug).first()
    cate_name = cate.cate_name
    # 查询出该分类下对应的文章
    posts = cate.posts.filter_by(status='published').order_by(Posts.created.desc()).all()

    # 点击排行
    click_posts = Posts.query.filter_by(status='published').order_by(Posts.views.desc()).offset(5).limit(5)
    return render_template('list.html',params=locals())

@main.route('/detail')
def details():
    if 'id' in session and 'username' in session:
        user = Users.query.filter_by(id=session['id']).first()
    # 接收传过来的post_id 查询文章
    id = request.args.get('post_id')
    post = Posts.query.filter_by(id=id).first()

    # 获取文章的评论数据
    comments = post.comments.filter(Comments.status=='published').order_by(Comments.created.desc()).all()
    # 点击排行
    click_posts = Posts.query.filter_by(status='published').order_by(Posts.views.desc()).offset(5).limit(10)

    return render_template('detail.html',params=locals())


# 设置点赞
@main.route('/dianzan')
def dianzan():
    num = request.args.get('num')
    post_id = request.args.get('post_id')
    post = Posts.query.filter_by(id=post_id).first()
    post.likes = num
    db.session.add(post)
    return 'xxx'


# 提交评论
@main.route('/add_comment',methods=['POST','GETS'])
def add_comment():
    if 'id' in session and 'username' in session:
        post_id = request.form.get('post_id')
        content = request.form.get('comment')
        uid = session['id']
        comment = Comments()
        comment.content=content
        comment.user_id=uid
        comment.post_id=post_id
        comment.created = datetime.datetime.now()
        db.session.add(comment)
        user = Users.query.filter_by(id=uid).first()

        dic = {
            'user_nickname':user.nickname,
            'avatar':user.avatar,
            'created':comment.created.strftime("%Y-%m-%d %H:%M:%S"),
            'content':comment.content
        }
        return json.dumps([dic])
    else:
        return json.dumps('x')

# 后台主页
@main.route('/admin/index')
def admin_index():
    if 'id' in session and 'username' in session:
        # 处理用户是否登陆
        user = Users.query.filter_by(id=session['id']).first()
        isIndex = True  # 设置高亮
        # 统计文章
        postNum = Posts.query.count()
        postDraNum=Posts.query.filter_by(status='drafted').count()
        cateNum = Categories.query.count()
        commentNum = Comments.query.count()
        comHeldNum = Comments.query.filter_by(status='held').count()
        return render_template('/admin/index.html', params=locals())
    else:
        return render_template('/admin/login.html', params=locals())


# 后台文章分类
@main.route('/admin/categories', methods=['POST', 'GET'])
def admin_categories():
    if 'id' in session and 'username' in session:
        # 处理用户是否登陆
        user = Users.query.filter_by(id=session['id']).first()
        isCate = True  # 设置高亮
        unfold = True  # 设置导航栏展开的标志
        if request.method == 'POST':
            cate_name = request.form['name']
            slug = request.form['slug']
            cateTest = db.session.query(Categories).filter(
                or_(Categories.slug == slug, Categories.cate_name == cate_name)).all()
            if cateTest:
                msg = '添加失败'
            else:
                cate = Categories()
                cate.cate_name = cate_name
                cate.slug = slug
                db.session.add(cate)
                msg = '添加成功'

        else:
            if 'id' in request.args:
                modify_cate = Categories.query.filter_by(id=request.args['id']).first()
        # 获取数据库中已有的分类
        cates = Categories.query.all()
        return render_template('/admin/categories.html', params=locals())
    else:
        return render_template('/admin/login.html', params=locals())


@main.route('/admin/cate-del')
def admin_cate_del():
    # 删除选中的分类
    ids = request.args.get('id').split(',')
    for id in ids:
        cate = Categories.query.filter_by(id=int(id)).first()
        if cate:
            db.session.delete(cate)
    return redirect(request.headers['Referer'])


@main.route('/admin/cate-modify', methods=['POST', 'GET'])
def admin_modify():
    # 获取前端传过来的id值 查询该分类进行修改
    id = request.form['modify-id']
    cate = Categories.query.filter_by(id=id).first()
    cate.cate_name = request.form['name']
    cate.slug = request.form['slug']
    db.session.add(cate)
    return redirect('/admin/categories')


@main.route('/admin/post-add', methods=['GET', 'POST'])
def admin_post_add():
    # 判断用户是否登陆
    if 'id' in session and 'username' in session:
        # 添加文章
        if request.method == 'POST':
            if 'id' in request.form:
                post = Posts.query.filter_by(id=request.form['id']).first()
            else:
                post = Posts()
            try:
                post.title = request.form['title']
                post.content = request.form['content']

                post.tags = request.form['tags']
                post.category_id = request.form['category']
                post.created = request.form['created']
                post.status = request.form['status']
                post.user_id = session['id']
                if 'feature' in request.files:
                    f = request.files['feature']
                    fname = datetime.datetime.now().strftime("%Y%m%d%H%M%S%f") + '-' + f.filename
                    fname = 'static/uploads/features/' + fname
                    basedir = os.path.dirname(__file__)
                    upload_path = os.path.join(os.path.dirname(basedir), fname)
                    f.save(upload_path)
                    post.feature = '/' + fname

                db.session.add(post)
                msg='操作成功'
                flg=True
            except Exception as e:
                flg=False
                msg = '操作失败'
        if 'id' in request.args:
            # 接收传过来的id值准备进行编辑操作
            modify_id = request.args['id']
            modify_post = Posts.query.filter_by(id=modify_id).first()
        user = Users.query.filter_by(id=session['id']).first()
        unfold = True  # 设置导航栏展开的标志
        isPostAdd = True  # 设置高亮
        # 获取数据库中已有的分类
        cates = Categories.query.all()
        return render_template('/admin/post-add.html', params=locals())
    else:
        return render_template('/admin/login.html', params=locals())

@main.route('/admin/post-checkTitle')
def checkTitke():
    # 校验文章标题
    title = request.args['title']
    flag = request.args['flag']
    post = Posts.query.filter(Posts.title != flag,Posts.title==title).first()

    if post:
        return '标题已经存在'
    else:
        return 'OK'

@main.route('/admin/posts', methods=['POST', 'GET'])
def admin_posts():
    if 'id' in session and 'username' in session:

        # 设置限定条件 进行数据筛选
        condition = []
        if session['role'] == 'author':
            # 不是管理员只能看到自己的文章
            condition.append(Posts.user_id==session['id'])

        cate = int(request.args.get('cate','0'))
        status = request.args.get('status','0')
        search =''
        if cate != 0:
            condition.append(Posts.category_id==cate)
            search += '&cate='+str(cate)
        if status != '0':
            condition.append(Posts.status==status)
            search += '&status='+status

        page = int(request.args.get('page', 1))
        size = 15  # 设定每页显示的文章数量

        # count = Posts.query.count()  # 获取文章总数量
        count = db.session.query(Posts).filter(*condition).count()

        totalPage = math.ceil(count / size)  # 总页数
        if page>totalPage:
            page=totalPage

        # 越过多少条取多少条数据
        posts = db.session.query(Posts).filter(*condition).order_by(Posts.created.desc()).offset((page - 1) * size).limit(size)
        try:
            print(posts[0])
        except:
            posts =[]
        visiables = 5   #页导航栏要显示的总数
        region = (visiables-1)/2

        beginPage = int(page - region)  #开始页
        endPage = int(page + region)    #结束页

        if beginPage < 1:
            beginPage = 1
            endPage = visiables

        if endPage > totalPage:
            endPage=totalPage
            beginPage=endPage-visiables+1;
            if beginPage < 1:
                beginPage=1;

        user = Users.query.filter_by(id=session['id']).first()  #获取当前用户信息

        cates = Categories.query.all()#获取分类信息
        unfold = True   #设置展开标志
        isPost = True  # 设置高亮

        return render_template('/admin/posts.html', params=locals())
    else:
        return render_template('/admin/login.html', params=locals())

@main.route('/admin/posts-del')
def admin_posts_del():
    # 删除文章
    ids = request.args.get('id').split(',')
    for id in ids:
        post = Posts.query.filter_by(id=int(id)).first()
        db.session.delete(post)
    return redirect(request.headers.get('Referer','/'))


# 操作评论
@main.route('/admin/comments',methods=['POST','GET'])
def admin_comments():
    if 'id' in session and 'username' in session:
        # 设置限定条件 进行数据筛选
        condition = []
        if session['role'] == 'author':
            # 不是管理员只能看到自己文章评论
            condition.append(Comments.user_id==session['id'])
        status = request.args.get('status','all')
        search = ''
        if status != 'all':
            condition.append(Comments.status == status)
            search += '&status=' + status
        page = int(request.args.get('page',1))
        size = 15
        count = db.session.query(Comments).filter(*condition).count()
        totalPage = math.ceil(count/size)   #总页数

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

        # 查询评论数据
        comments = db.session.query(Comments).filter(*condition).order_by(Comments.created.desc()).offset((page-1)*size).limit(size)
        user = Users.query.filter_by(id=session['id']).first()
        isComment = True # 设置高亮
        return render_template('/admin/comments.html',params=locals())
    else:
        return redirect('/admin/login')

# 设置评论状态
@main.route('/admin/comment-manage')
def admin_comment_manage():
    ids = request.args.get('id').split(',')
    status = request.args.get('status')
    for id in ids:
        comment = Comments.query.filter_by(id=int(id)).first()
        comment.status = status
        db.session.add(comment)
    return redirect(request.headers.get('Referer','/'))

# 删除评论
@main.route('/admin/comments-del')
def admin_comments_del():
    ids = request.args.get('id').split(',')
    for id in ids:
        comment = Comments.query.filter_by(id=int(id)).first()
        db.session.delete(comment)
    return redirect(request.headers.get('Referer','/'))

@main.route('/admin/nav-menus')
def admin_nav_menus():
    if 'id' in session and 'username' in session:
        user = Users.query.filter_by(id=session['id']).first()
        isNavMenu =True
        isSet = True
        return render_template('/admin/nav-menus.html',params=locals())
    else:
        return redirect('/admin/login')

@main.route('/admin/slides')
def admin_slides():
    if 'id' in session and 'username' in session:
        user = Users.query.filter_by(id=session['id']).first()
        isSlides =True
        isSet = True
        return render_template('/admin/slides.html',params=locals())
    else:
        return redirect('/admin/login')

@main.route('/admin/settings',methods=['POST','GET'])
def admin_settings():
    if 'id' in session and 'username' in session:
        if request.method == 'POST':
            options = db.session.query(Options).all()
            if 'site_logo' in request.files:
                f = request.files['site_logo']
                fname = datetime.datetime.now().strftime("%Y%m%d%H%M%S%f") + '-' + f.filename
                fname = 'static/uploads/logo/' + fname
                basedir = os.path.dirname(__file__)
                upload_path = os.path.join(os.path.dirname(basedir), fname)
                f.save(upload_path)
                options[0].val = '/' + fname
            options[1].val=request.form['site_name']
            options[2].val = request.form['site_description']
            options[3].val = request.form['site_keywords']
            options[4].val = request.form['site_footer']
            print(options)
        options = db.session.query(Options).all()
        user = Users.query.filter_by(id=session['id']).first()
        isSettings =True
        isSet = True
        return render_template('/admin/settings.html',params=locals())
    else:
        return redirect('/admin/login')
