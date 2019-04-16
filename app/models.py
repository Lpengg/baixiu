"""
编写所有的实体类
"""

from . import db


class Options(db.Model):
    '''
    选项表：记录网站的配置信息
    '''
    __tablename__ = 'options'
    id = db.Column(db.Integer, primary_key=True)
    site = db.Column(db.String(200), nullable=False, unique=True)
    val = db.Column(db.Text, nullable=False)

class Users(db.Model):
    '''
    用户表：记录用户信息
    '''
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), nullable=False, unique=True)
    password = db.Column(db.String(20), nullable=False)
    role = db.Column(db.String(10), default='author')
    nickname = db.Column(db.String(30), nullable=False, unique=True)
    avatar = db.Column(db.String(200), nullable=False, default='/static/uploads/avatars/avatar.jpg')
    status = db.Column(db.Boolean, default=True)
    bio = db.Column(db.String(30), default='写点什么吧')

    # 关联属性
    posts = db.relationship("Posts",backref='users',lazy='dynamic')

    comments = db.relationship("Comments", backref='user', lazy='dynamic')


class Posts(db.Model):
    '''
    文章表：记录文章信息
    '''
    __tablename__ = 'posts'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200),nullable=False,unique=True)
    tags = db.Column(db.String(10),nullable=False)
    feature = db.Column(db.String(200))
    created = db.Column(db.DateTime)
    content = db.Column(db.Text)
    views = db.Column(db.Integer,default=0)
    likes = db.Column(db.Integer,default=0)
    status = db.Column(db.String(20),nullable=False)
    # 关系：一(Users)对多(Posts)
    user_id = db.Column(db.Integer,db.ForeignKey('users.id'))
    # 关系:一(Categories)对多(Posts)
    category_id = db.Column(db.Integer,db.ForeignKey('categories.id'))
    comments = db.relationship("Comments", backref='post', lazy='dynamic')


class Categories(db.Model):
    '''
    分类表：记录文章分类信息
    '''
    __tablename__ = 'categories'
    id = db.Column(db.Integer, primary_key=True)
    slug = db.Column(db.String(20),unique=True,nullable=False)
    cate_name = db.Column(db.String(20),unique=True,nullable=False)

    # 关联属性
    posts = db.relationship("Posts", backref='categories', lazy='dynamic')

class Comments(db.Model):
    '''
    评论表：用于记录文章评论信息
    '''
    __tablename__ = 'comments'
    id = db.Column(db.Integer, primary_key=True)
    created = db.Column(db.DateTime)
    content = db.Column(db.String(200),nullable=False)
    status = db.Column(db.String(20),default='published')
    # 关系：
    user_id = db.Column(db.Integer,db.ForeignKey('users.id'))
    post_id = db.Column(db.Integer,db.ForeignKey('posts.id'))







