import base64
from datetime import datetime, timedelta
from sqlalchemy import func
from flask import Flask, request, render_template, redirect, url_for, session, Blueprint
from models import db, User, AdminUser, Book, BookBorrowing, PrinterBalanceDeposit, RatingReview, PrinterBalance, Goods, BorrowingGoods, Rooms, BorrowingRooms


admin_bp = Blueprint('admin', __name__)

# Login and Logout

@admin_bp.route('/admin-login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'GET':
        return render_template('admin/admin_login.html')
    elif request.method == 'POST':
        nim = request.form['nim']
        password = request.form['password']
    
    admin = AdminUser.query.filter_by(nomor_induk=nim).first()
    print(admin)

    if admin is None:
        return render_template('admin/admin_login.html', error='Invalid username or password.')

    if admin.password != password:
        return render_template('admin/admin_login.html', error='Invalid username or password.')

    session['logged_in'] = True
    session['nim'] = nim
    return redirect(url_for('admin.admin_book'))

@admin_bp.route("/admin-logout")
def admin_logout():
    session.pop('logged_in', None)
    return redirect(url_for('admin.admin_login'))


# Books

@admin_bp.route('/admin-book')
def admin_book():
    if 'logged_in' not in session:
        return render_template('admin/admin_login.html')
    
    if not session['logged_in']:
        return render_template('admin/admin_login.html')
    
    books = Book.query.all()

    for book in books:
        if book.book_cover != None:
            book.book_cover = base64.b64encode(book.book_cover).decode('utf-8')
        
    return render_template('admin/book_handler.html', books=books)

@admin_bp.route("/add-book", methods=["GET", "POST"])
def add_book():
    if 'logged_in' not in session:
        return render_template('admin/admin_login.html')
    
    if not session['logged_in']:
        return render_template('admin/admin_login.html')

    if request.method == "POST":
        new_title = request.form["title"]
        uploaded_file = request.files['cover']
        new_book_cover = uploaded_file.read() if uploaded_file else None
        new_writer = request.form.get("author")
        new_description = request.form.get("description")
        new_genre_id = request.form["genre"]

        new_book = Book(title=new_title, book_cover=new_book_cover, writer=new_writer, 
                        description=new_description, status="Available", genre_id=new_genre_id)

        db.session.add(new_book)
        db.session.commit()

    return redirect(url_for('admin.admin_book'))

@admin_bp.route("/edit-book/<path:title>/<int:book_id>", methods=["GET", "POST"])
def edit_book(title, book_id):
    if 'logged_in' not in session:
        return render_template('admin/admin_login.html')
    
    if not session['logged_in']:
        return render_template('admin/admin_login.html')

    book = Book.query.filter_by(
        book_id=book_id
    ).first()

    if request.method == "POST":
        new_title = request.form.get("title")
        uploaded_file = request.files['cover']
        new_book_cover = uploaded_file.read() if uploaded_file else book.book_cover
        new_writer = request.form["author"]
        new_description = request.form.get("description")
        if new_description == None:
            new_description = request.form.get("before_description")
        new_genre_id = request.form["genre"]

        if book:
            book.title = new_title
            book.book_cover = new_book_cover
            book.writer = new_writer
            book.description = new_description
            book.genre_id = new_genre_id
            db.session.commit()

    return redirect(url_for('admin.admin_book', title=title, id=book_id))

@admin_bp.route("/delete-book/<path:title>/<int:book_id>")
def delete_book(title, book_id):
    if 'logged_in' not in session:
        return render_template('admin/admin_login.html')
    
    if not session['logged_in']:
        return render_template('admin/admin_login.html')

    book = Book.query.filter_by(
        book_id=book_id
    ).first()

    if book:
        db.session.delete(book)
        db.session.commit()

    return redirect(url_for('admin.admin_book', title=title, id=book_id))


# Books Borrowing Handler

@admin_bp.route('/admin-borrowing-handler')
def admin_borrow():
    if 'logged_in' not in session:
        return render_template('admin/admin_login.html')
    
    if not session['logged_in']:
        return render_template('admin/admin_login.html')
    
    books_borrowing = BookBorrowing.query.all()
    users = User.query.all()
    books = Book.query.all()

    return render_template('admin/borrowing_handler.html', books_borrowing=books_borrowing, users=users, books=books)

@admin_bp.route("/add-borrowing-handler", methods=["GET", "POST"])
def add_borrow():
    if 'logged_in' not in session:
        return render_template('admin/admin_login.html')
    
    if not session['logged_in']:
        return render_template('admin/admin_login.html')

    if request.method == "POST":
        new_nomor_induk = request.form["nim"]
        new_book_id = request.form["book"]
        new_borrowing_date = request.form["borrowing-date"]
        
        # Calculate due date as 2 weeks (14 days) after borrowing date
        borrowing_date = datetime.strptime(new_borrowing_date, '%Y-%m-%d')  # Convert to a datetime object
        new_due_date = borrowing_date + timedelta(days=14)  # Add 14 days to the borrowing date


        new_book_borrowing = BookBorrowing(book_id=new_book_id, borrowing_date=new_borrowing_date, 
                                            due_date=new_due_date, nomor_induk=new_nomor_induk)

        db.session.add(new_book_borrowing)
        db.session.commit()

    return redirect(url_for('admin.admin_borrow', id=id))

@admin_bp.route("/edit-borrowing-handler/<int:id>", methods=["GET", "POST"])
def edit_borrow(id):
    if 'logged_in' not in session:
        return render_template('admin/admin_login.html')
    
    if not session['logged_in']:
        return render_template('admin/admin_login.html')

    book_borrowing = BookBorrowing.query.filter_by(
        id=id
    ).first()

    if request.method == "POST":
        new_nomor_induk = book_borrowing.nomor_induk
        new_book_id = request.form["book"]
        new_borrowing_date = request.form["borrowing-date"]
        new_due_date = request.form["due-date"]
        new_return_date = request.form["returning-date"]
        new_fine = request.form.get("fine")

        if book_borrowing:
            book_borrowing.book_id = new_book_id
            book_borrowing.borrowing_date = new_borrowing_date
            book_borrowing.due_date = new_due_date
            book_borrowing.return_date = new_return_date
            book_borrowing.fine = new_fine
            book_borrowing.nomor_induk =new_nomor_induk
            db.session.commit()

    return redirect(url_for('admin.admin_borrow', id=id))

@admin_bp.route("/delete-borrowing-handler/<int:id>")
def delete_borrow(id):
    if 'logged_in' not in session:
        return render_template('admin/admin_login.html')
    
    if not session['logged_in']:
        return render_template('admin/admin_login.html')

    book_borrowing = BookBorrowing.query.filter_by(
        id=id
    ).first()

    if book_borrowing:
        db.session.delete(book_borrowing)
        db.session.commit()

    return redirect(url_for('admin.admin_borrow', id=id))


# Deposit

@admin_bp.route('/admin-deposit')
def admin_deposit():
    if 'logged_in' not in session:
        return render_template('admin/admin_login.html')
    
    if not session['logged_in']:
        return render_template('admin/admin_login.html')

    deposits = PrinterBalanceDeposit.query.filter_by(
        status="Pending"
        ).all()

    return render_template('admin/deposit_handler.html', deposits=deposits)


# Goods and Rooms

@admin_bp.route('/admin-goods-rooms')
def admin_goods_rooms():
    if 'logged_in' not in session:
        return render_template('admin/admin_login.html')
    
    if not session['logged_in']:
        return render_template('admin/admin_login.html')

    rooms = Rooms.query.all()
    goods = Goods.query.all()

    return render_template('admin/goods_rooms_handler.html', rooms=rooms, goods=goods)


# Users

@admin_bp.route('/admin-users')
def admin_users():
    if 'logged_in' not in session:
        return render_template('admin/admin_login.html')
    
    if not session['logged_in']:
        return render_template('admin/admin_login.html')

    users = User.query.all()

    return render_template('admin/user_handler.html', users=users)