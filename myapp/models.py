from sqlalchemy import Enum, Column, Integer, String, DateTime, Boolean, Float, ForeignKey
from sqlalchemy.orm import backref, relationship
from datetime import datetime
from myapp import db
from flask_login import UserMixin
from enum import Enum as UserEnum


class UserRole(UserEnum):
    ADMIN = 1
    USER = 2


class BaseModel(db.Model):
    __abstract__ = True

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), nullable=True)
    created_date = Column(DateTime, default=datetime.now())
    description = Column(String(200), nullable=True)

    def __str__(self):
        return self.name


class User(BaseModel, UserMixin):
    first_name = Column(String(50), nullable=True)
    last_name = Column(String(50), nullable=True)
    username = Column(String(50), nullable=False, unique=True)
    password = Column(String(50), nullable=False)
    active = Column(Boolean, default=True)
    email = Column(String(50))
    avatar = Column(String(100), default='image/1.png')
    user_role = Column(Enum(UserRole), default=UserRole.USER)
    receipts = relationship('Receipt', backref='user', lazy=True)
    comments = relationship('Comment', backref='user', lazy=True)

    def __str__(self):
        return self.name


class Category(BaseModel):
    __tablename__ = 'category'

    products = relationship('Product', backref='category', lazy=True)


class Supplier(BaseModel):
    __tablename__ = 'supplier'

    products = relationship('Product', backref='supplier', lazy=True)


class Product(BaseModel):
    __tablename__ = 'product'

    price = Column(Float, default=0)
    image = Column(String(100), nullable=True)
    active = Column(Boolean, default=True)
    category_id = Column(Integer, ForeignKey(Category.id), nullable=False)
    tags = relationship('Tag', secondary='product_tag',
                        lazy='subquery', backref=backref('products', lazy=True))
    supplier_id = Column(Integer, ForeignKey(Supplier.id), nullable=False)
    receipt_details = relationship('ReceiptDetail', backref='product', lazy=True)
    comments = relationship('Comment', backref='product', lazy=True)


class Employee(BaseModel):
    last_name = Column(String(50), nullable=False)
    first_name = Column(String(50), nullable=False)
    title = Column(String(30), nullable=False)
    address = Column(String(30), nullable=False)
    day_of_birth = DateTime


class Customer(BaseModel):
    company_name = Column(String(50), nullable=False)
    contact_name = Column(String(30), nullable=False)
    contact_title = Column(String(30), nullable=False)
    address = Column(String(60), nullable=False)
    city = Column(String(15), nullable=False)
    phone = Column(String(20), nullable=False)
    receipt_details = relationship('ReceiptDetail', backref='customer', lazy=True)


class Tag(db.Model):
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), nullable=False, unique=True)


product_tag = db.Table('product_tag',
                       db.Column('product_id', Integer, ForeignKey('product.id'), primary_key=True),
                       db.Column('tag_id', Integer, ForeignKey('tag.id'), primary_key=True))


class Receipt(db.Model):
    id = Column(Integer, primary_key=True, autoincrement=True)
    created_date = Column(DateTime, default=datetime.now())
    user_id = Column(Integer, ForeignKey(User.id), nullable=False)
    receipt_details = relationship('ReceiptDetail', backref='receipt', lazy=True)


class ReceiptDetail(db.Model):
    id = Column(Integer, primary_key=True, autoincrement=True)
    receipt_id = Column(Integer, ForeignKey(Receipt.id), nullable=False)
    product_id = Column(Integer, ForeignKey(Product.id), nullable=False)
    customer_id = Column(Integer, ForeignKey(Customer.id), nullable=False)
    quantity = Column(Integer, default=0)
    unit_price = Column(Float, default=0)


class ChuQuan(db.Model):
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=True)


class Comment(BaseModel):
    content = Column(String(255), nullable=False)
    product_id = Column(Integer, ForeignKey(Product.id), nullable=False)
    user_is = Column(Integer, ForeignKey(User.id), nullable=False)

    def __str__(self):
        return self.content


if __name__ == '__main__':
    db.create_all()

    # p1 = Product(name='iPhone 8 plus', description="dsdsds", price=17, image="image/1.png", category_id=1)
    # p2 = Product(name='iPhone 4 plus', description="dsdsds", price=17, image="image/1.png", category_id=1)
    # p3 = Product(name='iPhone 5 plus', description="dsdsds", price=17, image="image/1.png", category_id=1)
    # p4 = Product(name='iPhone 6 plus', description="dsdsds", price=17, image="image/1.png", category_id=1)
    # p5 = Product(name='iPhone 7 plus', description="dsdsds", price=17, image="image/1.png", category_id=1)
    #
    # db.session.add(p1)
    # db.session.add(p2)
    # db.session.add(p3)
    # db.session.add(p4)
    # db.session.add(p5)
    # db.session.commit()
