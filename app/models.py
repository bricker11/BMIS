# -*— coding:utf-8 -*—
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from app import db, login_manager

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    __table_args__ = {'mysql_collate': 'utf8_general_ci'}
    id = db.Column(db.Integer, primary_key=True, unique=True)
    username = db.Column(db.String(64), unique=True, index=True)
    password_hash = db.Column(db.String(128))
    name = db.Column(db.String(64), index=True)
    gender = db.Column(db.Integer, default=1)
    depart = db.Column(db.String(64))
    post = db.Column(db.String(64))
    contact = db.Column(db.String(64))
    room = db.Column(db.String(64))
    # 0:管理员 1:读者
    user_type = db.Column(db.Integer, default=1)
    # 头像图片链接
    avata = db.Column(db.String(256),default='lost')
    # 反向关联到库存图书
    own_books = db.relationship('Library',backref='_borrower',lazy='select')

    # 密码加密及验证
    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)


class Book(db.Model):
    __tablename__ = 'books'
    __table_args__ = {'mysql_collate': 'utf8_general_ci'}
    isbn = db.Column(db.String(64), primary_key=True, unique=True)
    name = db.Column(db.String(128),index=True)
    author = db.Column(db.String(64),index=True)
    press = db.Column(db.String(64))
    category = db.Column(db.Integer,default=0)
    intro = db.Column(db.String(512))
    location = db.Column(db.String(64))
    # 封面图片链接
    cover = db.Column(db.String(256),default='lost')


class Library(db.Model):
    __tablename__ = 'librarys'
    __table_args__ = {'mysql_collate': 'utf8_general_ci'}
    book_id = db.Column(db.Integer, primary_key=True, unique=True)
    isbn_id = db.Column(db.String(64),db.ForeignKey('books.isbn'))
    location = db.Column(db.String(64))
    # 图书状态 1：已借出  2：未借出
    status = db.Column(db.Integer, default=0)
    borrower_id = db.Column(db.Integer,db.ForeignKey('users.id'))
    start_date = db.Column(db.Float,default=0)
    end_date = db.Column(db.Float,default=0)
    readyto_borrow = db.Column(db.Integer, default=0)
    readyto_return = db.Column(db.Integer, default=0)


class Request(db.Model):
    __tablename__ = 'requests'
    __table_args__ = {'mysql_collate': 'utf8_general_ci'}
    # 申请号
    id = db.Column(db.Integer, primary_key=True, unique=True)
    # 目标图书编号
    book_id = db.Column(db.Integer,db.ForeignKey('librarys.book_id'))
    # 操作码  0：借阅  1：归还
    opcode =  db.Column(db.Integer)
    # 申请者id
    requester = db.Column(db.Integer,db.ForeignKey('users.id'))
    # 请求生成时间
    requestdate = db.Column(db.Float,default=0)


class Want(db.Model):
    __tablename__ = 'wants'
    __table_args__ = {'mysql_collate': 'utf8_general_ci'}
    id = db.Column(db.Integer, primary_key=True, unique=True)
    name = db.Column(db.String(128), index=True)
    author = db.Column(db.String(64), index=True)
    press = db.Column(db.String(64))
    category = db.Column(db.Integer,default=0)
    sale = db.Column(db.Float)
    requester = db.Column(db.Integer,db.ForeignKey('users.id'))
    date = db.Column(db.Float)


class SysInfo(db.Model):
    __tablename__ = 'sysinfo'
    __table_args__ = {'mysql_collate': 'utf8_general_ci'}
    id = db.Column(db.Integer, primary_key=True,unique=True)
    maxuser = db.Column(db.Integer,default=100)
    maxbook = db.Column(db.Integer,default=5)
    maxtime = db.Column(db.Integer,default=3)


class Statics(db.Model):
    __tablename__ = 'statics'
    __table_args__ = {'mysql_collate': 'utf8_general_ci'}
    mon = db.Column(db.Integer, primary_key=True,unique=True)
    book_data = db.Column(db.Integer,default=0)
    reader_data = db.Column(db.Integer,default=0)


#----------------------------------- 图书分类 -------------------------------------
# 图书分类代码
category = {0:'通信',
            1:'计算机',
            2:'政治',
            3:'历史',
            4:'经济',
            5:'文学',
            6:'军事',
            7:'影音',
            8:'游戏',
            9:'生活'}
# 下拉菜单选项（与以上代码一一对应）
choices = [(0, '通信'), (1, '计算机'), (2, '政治'), (3, '历史'), (4, '经济'),
           (5, '文学'), (6, '军事'), (7, '影音'), (8, '游戏'), (9, '生活')]

#----------------------------------- 图书操作 -------------------------------------
# 请求操作码
opcode = {0:'借阅',
          1:'归还'}

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

