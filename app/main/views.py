# -*— coding:utf-8 -*—
from flask import render_template,request,session,redirect,url_for,abort,flash,json,jsonify
from flask_login import login_required,current_user,login_user,logout_user
from . import main
from .forms import LoginForm,RegisterForm,AddBookForm,EditBookForm,SearchBookForm,\
    SearchUserForm,AdminUserForm,AdminPasswdForm,SysSetForm
from app import db
from app.models import User,Book,Library,Request,SysInfo,Want,Statics,category,choices
from sqlalchemy import or_,and_
from datetime import datetime

# ------------------------------ 渲染页面路由 --------------------------------#
# 浏览器首页
@main.route('/')
def first():
    return redirect(url_for('main.login'))

# 系统首页
@main.route('/index',methods=['GET','POST'])
@login_required
def index():
    return render_template('index.html')

# 登录页面
@main.route('/login',methods=['GET','POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is not None and user.verify_password(form.password.data):
            login_user(user, True)
            if user.user_type == 0:
                return redirect(url_for('main.index'))
            else:
                return redirect(url_for('reader.index'))
        flash('用户名或密码错误')
    return render_template('login.html',form=form)

# 注册用户页面
@main.route('/register',methods=['GET','POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        print(form.gender.data)
        user = User(username=form.username.data, password=form.password.data,
                    name=form.name.data, id=form.id.data,gender=int(form.gender.data),
                    depart=form.depart.data, contact=form.contact.data, room=form.room.data, avata=form.avata.data)
        db.session.add(user)
        db.session.commit()
        return redirect(url_for('main.login'))
    return render_template('register.html',form=form)

# 退出登录，跳转登录页面
@main.route('/logout')
@login_required
def logout():
    logout_user()
    flash('您已退出')
    return redirect(url_for('main.login'))


# 修改系统页面，修改系统设置
@main.route('/sys/sysinfo',methods=['GET','POST'])
@login_required
def sysinfo():
    form = SysSetForm()
    sysinfo = SysInfo.query.filter_by(id=1).first()
    if form.validate_on_submit():
        sysinfo.maxuser = form.maxuser.data
        sysinfo.maxbook = form.maxbook.data
        sysinfo.maxtime = form.maxtime.data
        db.session.commit()
        flash("修改成功")
        return redirect(url_for('main.sysinfo'))
    form.maxuser.data = sysinfo.maxuser
    form.maxbook.data = sysinfo.maxbook
    form.maxtime.data = sysinfo.maxtime
    return render_template('sysinfo.html',form=form)

# 用户信息页面，修改个人信息
@main.route('/sys/adminuser',methods=['GET','POST'])
@login_required
def adminuser():
    form = AdminUserForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=current_user.username).first()
        user.name = form.name.data
        user.depart = form.depart.data
        user.post = form.post.data
        user.contact = form.contact.data
        user.room = form.room.data
        db.session.commit()
        flash("修改成功")
        return redirect(url_for('main.adminuser'))

    form.username.data = current_user.username
    form.name.data = current_user.name
    form.gender.data = current_user.gender
    form.id.data = current_user.id
    form.depart.data = current_user.depart
    form.post.data = current_user.post
    form.contact.data = current_user.contact
    form.room.data = current_user.room
    return render_template('adminuser.html',form=form)

# 修改用户密码
@main.route('/sys/adminpasswd',methods=['GET','POST'])
@login_required
def adminpasswd():
    form = AdminPasswdForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            user = User.query.filter_by(username=current_user.username).first()
            user.password = form.password.data
            db.session.commit()
            flash('修改成功')
            return redirect(url_for('main.adminpasswd'))
        else:
            flash('输入密码不一致')
    return render_template('adminpasswd.html',form=form)


# 图书入库页面，新增图书
@main.route('/bookmanage/addbook',methods=['GET','POST'])
@login_required
def addbook():
    form = AddBookForm()
    if form.validate_on_submit():
        book = Book(isbn=form.isbn.data,name=form.name.data,author=form.author.data,
                    press=form.press.data,category=form.category.data,location=form.location.data,
                    intro=form.brefintro.data,cover=form.cover.data)
        library = Library(book_id=form.book_id.data,isbn_id=form.isbn.data,
                          location=form.location.data,status=0)
        db.session.add(book)
        db.session.commit()
        db.session.add(library)
        current_mon = int(datetime.now().strftime("%m"))
        statics = Statics.query.filter_by(mon=current_mon).first()
        statics.book_data = statics.book_data + 1
        db.session.commit()
        flash("添加成功，请继续添加")
        return redirect(url_for('main.addbook'))
    else:
        print(form.flag)
        if form.flag == 1:
            flash("ISBN已经存在，添加失败")
        elif form.flag == 2:
            flash("图书编号已经存在，添加失败")
    return render_template('addbook.html',form=form)


# 图书搜索页面，按条件搜索图书
@main.route('/bookmanage/searchbook',methods=['GET','POST'])
@login_required
def searchbook():
    form = SearchBookForm()
    return render_template('searchbook.html',form=form)

# 图书统计页面，显示图书信息统计图表
@main.route('/bookmanage/bookstatics',methods=['GET','POST'])
@login_required
def bookstatics():
    return render_template('bookstatics.html')

# 读者信息页面，显示全部读者信息列表，可按条件搜索读者
@main.route('/readermanage/readerinfo',methods=['GET','POST'])
@login_required
def readerinfo():
    form = SearchUserForm()
    return render_template('readerinfo.html',form=form)

# 读者信息统计页面，展示读者借书信息图表
@main.route('/readermanage/readerstatics',methods=['GET','POST'])
@login_required
def readerstatics():
    return render_template('readerstatics.html')

# 图书借阅界面，显示图书借阅申请列表，操作（借出/拒绝）
@main.route('/bookmanage/borrowbook',methods=['GET','POST'])
@login_required
def borrowbook():
    return render_template('borrowbook.html')

# 图书回收界面，显示图书回收申请列表，操作（回收）
@main.route('/bookmanage/returnbook',methods=['GET','POST'])
@login_required
def returnbook():
    return render_template('returnbook.html')

# 读者想看页，显示读者提交的想看的书单
@main.route('/wantsmanage/wantsbook',methods=['GET','POST'])
@login_required
def wantsbook():
    return render_template('wantsbook.html')



# ------------------------------ 数据 api --------------------------------#
# 返回当前登录的用户名，用于动态更新标题栏用户名
@main.route('/api/username',methods=['GET','POST'])
@login_required
def username_api():
    return jsonify({'username':current_user.username})

# 同名图书有多册需要入库时，从第二本开始只要指定isbn和图书编号即可
@main.route('/api/addinventory',methods=['GET','POST'])
@login_required
def addinventory_api():
    data = request.get_data().decode().split('&')
    isbn = data[0].split('=')[1]
    book_id = data[1].split('=')[1]
    book = Book.query.filter_by(isbn=isbn).first()
    if book:
        lib = Library(book_id=book_id,isbn_id=isbn,location=book.location,status=0)
        db.session.add(lib)
        db.session.commit()
        result = {"status":0}
    else:
        result = {"status":1}
    return jsonify(result)

# 用于首页显示借还书申请的数量，结果为请求表中的不同请求数量(0借阅，1归还)
@main.route('/api/indextips',methods=['GET','POST'])
@login_required
def indextips_api():
    breq = len(Request.query.filter_by(opcode=0).all())
    rreq = len(Request.query.filter_by(opcode=1).all())
    result = {"breq":breq,
              "rreq":rreq}
    return jsonify(result)

# 返回所有图书列表（根据ISBN标识每本书）
@main.route('/api/booklist',methods=['GET','POST'])
@login_required
def booklist_api():
    # 列出所有书目
    booklist= Book.query.all()
    data = []
    i = 0
    for item in booklist:
        i = i + 1
        # 查询库存，得到每一本书的存量
        library = Library.query.filter_by(isbn_id=item.isbn).all()
        total = len(library)
        # 查询库存，得到每一本未借出的书的存量，要除去已经被读者申请借阅的书
        library = Library.query.filter(and_(Library.isbn_id==item.isbn,Library.status==0,Library.readyto_borrow==0)).all()
        free = len(library)
        for cat in choices:
            if item.category == cat[0]:
                cg = cat[1]
        data_row = {"sno":i,"isbn":item.isbn,"name":item.name,"author":item.author,
                    "press":item.press,"category":cg,"location":item.location,
                    "total":total,"free":free}
        data.append(data_row)
    # 所有图书的数量
    count = len(booklist)
    result = {
        "code": 0,
        "msg": "",
        "count": count,
        "data":data
    }
    return jsonify(result)

# 返回每本书的借阅情况，用于弹出层显示列表信息
@main.route('/api/bookdetail',methods=['GET','POST'])
@login_required
def bookdetail_api():
    # 得到post过来的isbn
    isbn = request.get_data().decode().split('=')[1]
    # 找到该图书
    book = Book.query.filter_by(isbn=isbn).first()
    # 得到该图书库存中已借出部分的列表
    library = Library.query.filter(and_(Library.isbn_id==isbn,Library.status)).all()
    data = []
    for item in library:
        # 得到借阅者信息
        borrower = User.query.filter_by(id=item.borrower_id).first()
        borrower = borrower.name
        date = item.start_date
        date = datetime.fromtimestamp(date).strftime("20%y-%m-%d")
        row = {"bookname": book.name,
               "author": book.author,
               "press": book.press,
               "borrower": borrower,
               "date": date}
        data.append(row)
    # 该图书已借出库存的数量
    count = len(library)
    result = {
        "data":data,
        "count":count
    }
    return jsonify(result)

# 处理删除图书的请求，并返回操作结果
@main.route('/api/bookdelete',methods=['GET','POST'])
@login_required
def bookdelete_api():
    isbn = request.get_data().decode().split('=')[1]
    book = Book.query.filter_by(isbn=isbn).first()
    # 该图书借出的库存量，为0时该图书才能被删除
    lib = Library.query.filter(and_(Library.isbn_id==isbn,Library.status)).all()
    blen = len(lib)
    if book and blen == 0:
        # 把该图书相关的库存删除
        library = Library.query.filter_by(isbn_id=isbn).all()
        for item in library:
            db.session.delete(item)
            db.session.commit()
        # 把该图书信息也删除
        db.session.delete(book)
        db.session.commit()
        result = {"status":0}
    else:
        result = {"status":1}
    return jsonify(result)

# 处理修改图书的请求1，用于弹出层显示当前图书信息
@main.route('/api/bookedit',methods=['GET','POST'])
@login_required
def bookedit_api():
    isbn = request.get_data().decode().split('=')[1]
    book = Book.query.filter_by(isbn=isbn).first()
    if book:
        result = {"isbn": book.isbn,
              "name": book.name,
              "author": book.author,
              "press": book.press,
              "location": book.location,
              "intro": book.intro,
              "cover":book.cover}
    return jsonify(result)

# 处理修改图书的请求2，接收弹出层表单提交信息，更新数据库(这个其实不算api，而是表单action的目标，因而直接重定向页面)
@main.route('/api/bookedit2',methods=['GET','POST'])
@login_required
def bookedit_api2():
    # 获取form表单post过来的数据
    info = request.values.to_dict()
    print(info)
    book = Book.query.filter_by(isbn=info['isbn']).first()
    if book:
        book.isbn = info['isbn']
        book.name = info['name']
        book.author = info['author']
        book.press = info['press']
        book.location = info['location']
        book.intro = info['intro']
        book.cover = info['cover']
        db.session.commit()
        flash("修改成功")
    return redirect(url_for('main.searchbook'))

# 处理搜索图书请求，根据筛选条件码，按照不同条件进行筛选，返回信息用于渲染结果表格
@main.route('/api/searchbook',methods=['GET','POST'])
@login_required
def searchbook_api():
    # 获取form表单post过来的数据
    info = request.values.to_dict()
    data = []
    count = 0
    # 按书名查找类似图书
    if info['option']=='1':
        books = Book.query.filter(Book.name.like('%'+info['key']+'%')).all()
        count = len(books)
        i = 0
        for book in books:
            i = i+1
            library = Library.query.filter_by(isbn_id=book.isbn).all()
            total = len(library)
            library = Library.query.filter(and_(Library.isbn_id == book.isbn, Library.status == 0,Library.readyto_borrow == 0)).all()
            free = len(library)
            cg = ''
            for cat in choices:
                if book.category == cat[0]:
                    cg = cat[1]
            data_row = {"sno": i, "isbn": book.isbn, "name": book.name, "author": book.author,
                        "press": book.press, "category": cg, "location": book.location,
                        "total": total, "free": free}
            data.append(data_row)
    elif info['option']=='2':
        books = Book.query.filter(Book.author.contains(info['key'])).all()
        count = len(books)
        i = 0
        for book in books:
            i = i + 1
            library = Library.query.filter_by(isbn_id=book.isbn).all()
            total = len(library)
            library = Library.query.filter(and_(Library.isbn_id == book.isbn, Library.status == 0,Library.readyto_borrow == 0)).all()
            free = len(library)
            data_row = {"sno": i, "isbn": book.isbn, "name": book.name, "author": book.author,
                        "press": book.press, "category": book.category, "location": book.location,
                        "total": total, "free": free}
            data.append(data_row)
    elif info['option'] == '3':
        books = Book.query.filter(Book.isbn.contains(info['key'])).all()
        count = len(books)
        i = 0
        for book in books:
            i = i + 1
            library = Library.query.filter_by(isbn_id=book.isbn).all()
            total = len(library)
            library = Library.query.filter(and_(Library.isbn_id == book.isbn, Library.status == 0,Library.readyto_borrow == 0)).all()
            free = len(library)
            data_row = {"sno": i, "isbn": book.isbn, "name": book.name, "author": book.author,
                        "press": book.press, "category": book.category, "location": book.location,
                        "total": total, "free": free}
            data.append(data_row)
    result = {
        "code": 0,
        "msg": "",
        "count": count,
        "data": data
    }
    return jsonify(result)

# 返回渲染图书图表1的数据
@main.route('/api/bookstatics1',methods=['GET','POST'])
@login_required
def bookstatics_api1():
    # 计算当月读者数目
    libs = Library.query.filter(Library.borrower_id != 0).all()
    users = User.query.all()
    reader_data = 0
    for user in users:
        for lib in libs:
            if user.id == lib.borrower_id:
                reader_data = reader_data+1
                break
    current_mon = int(datetime.now().strftime("%m"))
    statics = Statics.query.filter_by(mon=current_mon).first()
    statics.reader_data = reader_data
    db.session.commit()
    statics = Statics.query.all()
    book = []
    reader = []
    for item in statics:
        book.append(item.book_data)
        reader.append(item.reader_data)
    result = {
        'book': book,
        'reader': reader
    }
    return jsonify(result)

# 返回渲染图书图表2的数据
@main.route('/api/bookstatics2',methods=['GET','POST'])
@login_required
def bookstatics_api2():
    data = []
    # category为从models.py表中导入的字典（图书分类）
    for item in category:
        print(item)
        books = Book.query.filter_by(category=item).all()
        data_row = {'value': len(books), 'name': category[item]}
        data.append(data_row)
    result = {'data': data}
    return jsonify(result)

# 返回所有读者信息
@main.route('/api/userinfo',methods=['GET','POST'])
@login_required
def userinfo_api():
    # 列出所有读者
    users = User.query.filter_by(user_type=1).all()
    data = []
    i = 0
    for user in users:
        i = i+1
        # 得到每个读者的信息
        if user.gender == 0:
            gender = '女'
        else:
            gender = '男'
        data_row = {'sno': i,
                    'name': user.name,
                    'gender': gender,
                    'id': user.id,
                    'depart': user.depart,
                    'post': user.post,
                    'contact': user.contact,
                    'room': user.room}
        data.append(data_row)
    count = len(users)
    result = {
        "code": 0,
        "msg": "",
        "count": count,
        "data": data
    }
    return jsonify(result)

# 返回符合搜索条件的读者信息，用于渲染结果表格
@main.route('/api/searchreader',methods=['GET','POST'])
@login_required
def searchreader_api():
    # 获取form表单post过来的数据
    info = request.values.to_dict()
    print(info)
    data = []
    count = 0
    if info['option']=='1':
        users = User.query.filter(User.name.like('%'+info['key']+'%')).all()
        count = len(users)
        i = 0
        for user in users:
            i = i+1
            if user.gender == 0:
                gender = '女'
            else:
                gender = '男'
            data_row = {'sno': i,
                        'name': user.name,
                        'gender': gender,
                        'id': user.id,
                        'depart': user.depart,
                        'post': user.post,
                        'contact': user.contact,
                        'room': user.room}
            data.append(data_row)
    elif info['option']=='2':
        users = User.query.filter(User.contact==info['key']).all()
        count = len(users)
        i = 0
        for user in users:
            i = i + 1
            if user.gender == 0:
                gender = '女'
            else:
                gender = '男'
            data_row = {'sno': i,
                        'name': user.name,
                        'gender': gender,
                        'id': user.id,
                        'depart': user.depart,
                        'post': user.post,
                        'contact': user.contact,
                        'room': user.room}
            data.append(data_row)
    elif info['option'] == '3':
        users = User.query.filter(User.id==info['key']).all()
        count = len(users)
        i = 0
        for user in users:
            i = i + 1
            if user.gender == 0:
                gender = '女'
            else:
                gender = '男'
            data_row = {'sno': i,
                        'name': user.name,
                        'gender': gender,
                        'id': user.id,
                        'depart': user.depart,
                        'post': user.post,
                        'contact': user.contact,
                        'room': user.room}
            data.append(data_row)

    result = {
        "code": 0,
        "msg": "",
        "count": count,
        "data": data
    }
    return jsonify(result)

# 返回某个读者借阅的图书信息，用于渲染弹出层表格
@main.route('/api/readerdetail',methods=['GET','POST'])
@login_required
def readerdetail_api():
    id = request.get_data().decode().split('=')[1]
    user = User.query.filter_by(id=id).first()
    # 得到该读者的全部图书
    libs = Library.query.filter_by(borrower_id=id).all()
    data = []
    for lib in libs:
        start_date = lib.start_date
        start_date = datetime.fromtimestamp(start_date).strftime("20%y-%m-%d")
        end_date = lib.end_date
        end_date = datetime.fromtimestamp(end_date).strftime("20%y-%m-%d")
        book = Book.query.filter_by(isbn=lib.isbn_id).first()
        row = {"bookname": book.name,
               "author": book.author,
               "press": book.press,
               "borrower": user.name,
               "start_date": start_date,
               "end_date":end_date}
        data.append(row)
    count = len(libs)
    result = {
        "data":data,
        "count":count
    }
    return jsonify(result)

# 返回读者统计图表渲染所需数据
@main.route('/api/readerstatics',methods=['GET','POST'])
@login_required
def readerstatics_api():
    maxcount = SysInfo.query.first().maxbook
    print(maxcount)
    data = []
    for i in range(1,maxcount+1):
        print(i)
        users = User.query.all()
        count = 0
        for user in users:
            if len(user.own_books) == i:
                count = count+1
        data_row = {'value': count, 'name': str(i)+'本'}
        data.append(data_row)
    result = {'data': data}
    return jsonify(result)

# 用于渲染借阅申请列表
@main.route('/api/borrowlist',methods=['GET','POST'])
@login_required
def borrowlist_api():
    reqlist = Request.query.all()
    data = []
    i = 0
    for item in reqlist:
        if item.opcode == 0:
            i = i+1
            libbook = Library.query.filter_by(book_id=item.book_id).first()
            book = Book.query.filter_by(isbn=libbook.isbn_id).first()
            user = User.query.filter_by(id=item.requester).first()
            row_data = {"sno": i,
                        "name": user.name,
                        "id": user.id,
                        "book_id":libbook.book_id,
                        "bookname": book.name,
                        "author": book.author,
                        "press": book.press}
            data.append(row_data)
    count = i
    result = {
        "code": 0,
        "msg": "",
        "count": count,
        "data": data
    }
    return jsonify(result)

# 图书借阅同意处理
@main.route('/api/borrowok',methods=['GET','POST'])
@login_required
def borrowok_api():
    # 判断图书能不能借由读者界面借阅操作验证，此处只是更改图书库存信息
    book_id = request.get_data().decode().split('=')[1]
    # 提取一条借还书请求
    req = Request.query.filter_by(book_id=book_id).first()
    # 得到申请人
    borrower_id = req.requester
    # 得到当前时间的时间戳
    start_date = datetime.now().timestamp()
    # 计算到期时间
    maxtime = SysInfo.query.first().maxtime
    end_date = start_date + 3600*24*30*maxtime
    # 更新该库存图书条目的信息
    library = Library.query.filter_by(book_id=book_id).first()
    library.status = 1
    library.borrower_id = borrower_id
    library.start_date = start_date
    library.end_date = end_date
    library.readyto_borrow = 0
    library.readyto_return = 0
    # 删除该条请求
    db.session.delete(req)
    db.session.commit()
    result = {"status":0}
    return jsonify(result)

# 图书借阅拒绝处理
@main.route('/api/borrowdeny',methods=['GET','POST'])
@login_required
def borrowdeny_api():
    # 不操作，直接删去相应请求
    book_id = request.get_data().decode().split('=')[1]
    req = Request.query.filter_by(book_id=book_id).first()
    db.session.delete(req)
    db.session.commit()
    library = Library.query.filter_by(book_id=book_id).first()
    library.readyto_borrow = 0
    db.session.commit()
    result = {"status": 0}
    return jsonify(result)

# 用于渲染借阅归还列表
@main.route('/api/returnlist',methods=['GET','POST'])
@login_required
def returnlist_api():
    reqlist = Request.query.all()
    data = []
    i = 0
    for item in reqlist:
        if item.opcode == 1:
            i = i+1
            libbook = Library.query.filter_by(book_id=item.book_id).first()
            book = Book.query.filter_by(isbn=libbook.isbn_id).first()
            user = User.query.filter_by(id=item.requester).first()
            row_data = {"sno": i,
                        "name": user.name,
                        "id": user.id,
                        "book_id": libbook.book_id,
                        "bookname": book.name,
                        "author": book.author,
                        "press": book.press}
            data.append(row_data)
    count = i
    result = {
        "code": 0,
        "msg": "",
        "count": count,
        "data": data
    }
    print(result)
    return jsonify(result)

# 图书回收处理
@main.route('/api/returnok',methods=['GET','POST'])
@login_required
def returnok_api():
    # 清除相应图书库存的借阅记录
    book_id = request.get_data().decode().split('=')[1]
    req = Request.query.filter_by(book_id=book_id).first()
    db.session.delete(req)
    db.session.commit()
    library = Library.query.filter_by(book_id=book_id).first()
    library.status = 0
    library.borrower_id = 0
    library.start_date = 0
    library.end_date = 0
    library.readyto_borrow = 0
    library.readyto_return = 0
    db.session.commit()
    print('成功回收')
    result = {"status":0}
    return jsonify(result)

# 用于渲染读者想看列表
@main.route('/api/wantslist',methods=['GET','POST'])
@login_required
def wantslist_api():
    wants = Want.query.all()
    data = []
    i = 0
    for item in wants:
        i = i+1
        user = User.query.filter_by(id=item.requester).first()
        row_data = {"sno": item.id,
                    "bookname": item.name,
                    "author": item.author,
                    "press": item.press,
                    "price": item.sale,
                    "name": user.name,
                    "time":item.date}
        data.append(row_data)
    count = len(wants)
    result = {
        "code": 0,
        "msg": "",
        "count": count,
        "data": data
    }
    print(result)
    return jsonify(result)

# 读者想看列表忽略处理
@main.route('/api/wantsignore',methods=['GET','POST'])
@login_required
def wantsignore_api():
    id = request.get_data().decode().split('=')[1]
    want = Want.query.filter_by(id=id).first()
    db.session.delete(want)
    db.session.commit()
    result = {"status":0}
    return jsonify(result)


# 注册页面头像上传接口
@main.route('/api/register_avata',methods=['GET','POST'])
def register_avata_api():
    import os
    path = os.path.abspath(os.path.dirname(__file__))
    path = path[0:-4] + 'static/img/avata/'
    file = request.files["file"]
    basename = str(request.files["file"]).split(':')[1].split(' ')[1].split('.')[0][1:]
    uniname = basename + datetime.now().strftime("%y_%m_%d_%H_%M_%S") + '.jpg'
    localpath = path + uniname
    file.save(localpath)
    url = '../static/img/avata/' + uniname
    result = {
      "code": 0
      ,"msg": ""
      ,"data": {
        "src": url
      }
    }
    print('注册')
    return jsonify(result)


# 添加图书封面接口
@main.route('/api/add_bookcover',methods=['GET','POST'])
def add_bookcover_api():
    import os
    path = os.path.abspath(os.path.dirname(__file__))
    path = path[0:-4] + 'static/img/cover/'
    file = request.files["file"]
    basename = str(request.files["file"]).split(':')[1].split(' ')[1].split('.')[0][1:]
    uniname = basename + datetime.now().strftime("%y_%m_%d_%H_%M_%S") + '.jpg'
    localpath = path + uniname
    file.save(localpath)
    url = '../static/img/cover/' + uniname
    result = {
      "code": 0
      ,"msg": ""
      ,"data": {
        "src": url
      }
    }
    print('加书')
    return jsonify(result)

# 从数据库中获取用户头像链接(不区分管理员普通用户)
@main.route('/api/get_avata_url',methods=['GET','POST'])
def get_avata_url_api():
    username = request.get_data().decode().split('=')[1]
    user = User.query.filter_by(username=username).first()
    result = {"url":user.avata}
    return jsonify(result)

# 从数据库中获取书籍封面
@main.route('/api/get_bookcover_url',methods=['GET','POST'])
def get_bookcover_url_api():
    isbn = request.get_data().decode().split('=')[1]
    book = Book.query.filter_by(isbn=isbn).first()
    result = {"url":book.cover}
    return jsonify(result)