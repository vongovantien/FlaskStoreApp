import hashlib
import json
from datetime import datetime
from myapp import db, app
from myapp.models import Category, Product, User, UserRole, ReceiptDetail, Receipt, Comment
from sqlalchemy import func
from sqlalchemy.sql import extract
from flask_login import current_user


# def get_user_soccial(firstname, lastname, email, avatar):
#     user = User(username='3', password='3', first_name=firstname, last_name=lastname, email=email, avatar=avatar)
#
#     db.session.add(user)
#     db.session.commit()


def get_new_product():
    products = Product.query.filter(Product.active.__eq__(True)).limit(4).all()
    return products


def change_user_password(user_id, password):
    password = str(hashlib.md5(password.strip().encode('utf-8')).hexdigest())

    user = User.query.get(user_id)
    user.password = password
    db.session.commit()


def check_user_name(username):
    return User.query.filter(User.username.__eq__(username)).first()


def create_new_user(username, password, **kwargs):
    password = str(hashlib.md5(password.strip().encode('utf-8')).hexdigest())

    user = User(first_name=kwargs.get('first_name'),
                last_name=kwargs.get('last_name'),
                email=kwargs.get('email'),
                username=username.strip(),
                password=password,
                avatar=kwargs.get('avatar'))
    db.session.add(user)
    db.session.commit()


def read_categories():
    return Category.query.all()


def get_product_by_id(product_id):
    return Product.query.get(product_id)


def get_user_by_id(user_id):
    return User.query.get(user_id)


def check_login(username, password, role=UserRole.USER):
    if username and password:
        password = str(hashlib.md5(password.strip().encode('utf-8')).hexdigest())

    return User.query.filter(User.username.__eq__(username.strip()),
                             User.password.__eq__(password),
                             User.user_role.__eq__(role)).first()


def count_products():
    return Product.query.filter(Product.active.__eq__(True)).count()


def load_products(kw=None, from_price=None, to_price=None, cate_id=None, page=1, next_page=None, prev_page=None):
    products = Product.query.filter(Product.active.__eq__(True))

    if kw:
        products = products.filter(Product.name.contains(kw))
    if cate_id:
        products = products.filter(Product.category_id.__eq__(cate_id))
    if from_price:
        products = products.filter(Product.price.__ge__(from_price))
    if to_price:
        products = products.filter(Product.price.__le__(to_price))

    page_size = app.config['PAGE_SIZE']

    if next_page:
        page = page + 1
    if prev_page:
        page = page - 1

    start = (page - 1) * page_size

    return products.slice(start, start + page_size).all()


def count_cart(cart):
    total_quantity, total_amount = 0, 0

    if cart:
        for c in cart.values():
            total_quantity += c['quantity']
            total_amount += c['quantity'] * c['price']

    return {
        'total_quantity': total_quantity,
        'total_amount': total_amount,
    }


def add_receipt(cart):
    if cart:
        receipt = Receipt(user=current_user)
        db.session.add(receipt)

        for c in cart.values():
            d = ReceiptDetail(receipt=receipt,
                              product_id=c['id'],
                              quantity=c['quantity'],
                              unit_price=c['price'])
            db.session.add(d)

        db.session.commit()


def category_stats():
    # return Category.query.join(Product, Product.category_id.__eq__(Category.id), isouter=True)\
    #     #     .add_columns(func.count(Product.id)).group_by(Category.id).all()
    return db.session.query(Category.id, Category.name, func.count(Product.id)) \
        .join(Product, Category.id.__eq__(Product.category_id), isouter=True) \
        .group_by(Category.id).order_by(Category.id).all()


def product_stats(kw=None, from_date=None, to_date=None):
    p = db.session.query(Product.id, Product.name,
                         func.sum(ReceiptDetail.quantity * ReceiptDetail.unit_price)) \
        .join(ReceiptDetail, ReceiptDetail.product_id.__eq__(Product.id), isouter=True) \
        .join(Receipt, Receipt.id.__eq__(ReceiptDetail.receipt_id)) \
        .group_by(Product.id, Product.name)

    if kw:
        p = p.filter(Product.name.contains(kw))

    if from_date:
        p = p.filter(Receipt.created_date.__ge__(from_date))

    if to_date:
        p = p.filter(Receipt.created_date.__le__(to_date))

    return p.all()


def product_month_stats(year):
    return db.session.query(extract('month', Receipt.created_date),
                            func.sum(ReceiptDetail.quantity * ReceiptDetail.unit_price)) \
        .join(ReceiptDetail, ReceiptDetail.receipt_id.__eq__(Receipt.id)) \
        .filter(extract('year', Receipt.created_date) == year) \
        .group_by(extract('month', Receipt.created_date)) \
        .order_by(extract('month', Receipt.created_date)) \
        .all()


def add_comment(content, product_id):
    # if content is None:
    #     msg_err = "Khong duoc de trong"

    c = Comment(content=content, product_id=product_id, user=current_user)

    db.session.add(c)
    db.session.commit()
    return c


def get_comments(product_id, page=1):
    page_size = app.config['COMMENT_SIZE']
    start = (page - 1) * page_size

    return Comment.query.filter(Comment.product_id.__eq__(product_id)).order_by(-Comment.id).slice(start,
                                                                                                   start + page_size).all()


def count_comment(product_id):
    return Comment.query.filter(Comment.product_id.__eq__(product_id)).count()
