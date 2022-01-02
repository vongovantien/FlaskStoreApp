from flask_admin import BaseView, expose, Admin, AdminIndexView
from myapp.models import Category, Product, User, Supplier, Tag, Employee, Customer, UserRole
from flask_admin.contrib.sqla import ModelView
from myapp import db, utils, app
from flask import redirect, request, url_for
from flask_login import logout_user, current_user
from datetime import datetime
from wtforms import TextAreaField
from wtforms.widgets import TextArea
from sqlalchemy.event import listens_for


class CKTextAreaWidget(TextArea):
    def __call__(self, field, **kwargs):
        if kwargs.get('class'):
            kwargs['class'] += ' ckeditor'
        else:
            kwargs.setdefault('class', 'ckeditor')
        return super(CKTextAreaWidget, self).__call__(field, **kwargs)


class CKTextAreaField(TextAreaField):
    widget = CKTextAreaWidget()


class MyAdminIndex(AdminIndexView):
    @expose('/')
    def index(self):
        stats = utils.category_stats()
        return self.render('admin/index.html', stats=stats)


class AdminView(ModelView):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.static_folder = 'static'


class AdminAuthenticatedView(ModelView):
    def is_accessible(self):
        return current_user.is_authenticated and current_user.user_role.__eq__(UserRole.ADMIN)


class ProductView(AdminAuthenticatedView):
    column_display_pk = True
    can_view_details = True
    can_export = True
    column_filters = ['name', "price"]
    column_searchable_list = ['name', 'price']
    column_exclude_list = ['created_date']
    column_labels = {
        'name': 'Tên SP',
        'price': 'Giá tiền'
    }
    column_descriptions = dict(
        discription='name and price'
    )
    create_modal = True
    edit_modal = True

    form_overrides = {
        'name': CKTextAreaField
    }


class CategoryView(AdminAuthenticatedView):
    can_view_details = True
    column_filters = ['name']
    page_size = 10

    extra_js = ['//cdn.ckeditor.com/4.6.0/standard/ckeditor.js']

    form_overrides = {
        'name': CKTextAreaField
    }


class StatsView(BaseView):
    @expose('/')
    def index(self):
        kw = request.args.get('kw')
        from_date = request.args.get('from_date')
        to_date = request.args.get('to_date')
        year = request.args.get('year', datetime.now().year, type=int)

        return self.render('admin/stats.html', month_stats=utils.product_month_stats(year=year),
                           stats=utils.product_stats(kw=kw, from_date=from_date, to_date=to_date))

    def is_accessible(self):
        return current_user.is_authenticated


class LogoutView(BaseView):
    @expose("/")
    def __index__(self):
        logout_user()

        return redirect("/admin")

    def is_accessible(self):
        return current_user.is_authenticated and current_user.user_role.__eq__(UserRole.ADMIN)


admin = Admin(app=app, name="Quản trị sản phẩm bán hàng điện thoại", template_mode='bootstrap4',
              index_view=MyAdminIndex())

admin.add_view(CategoryView(Category, db.session, name="Danh mục"))
admin.add_view(ProductView(Product, db.session, name="Sản phẩm"))
admin.add_view(AdminAuthenticatedView(Employee, db.session, name="Nhân viên"))
admin.add_view(AdminAuthenticatedView(Supplier, db.session, name="Nhà cung cấp"))
admin.add_view(AdminAuthenticatedView(Customer, db.session, name="Khách hàng"))
admin.add_view(AdminAuthenticatedView(Tag, db.session, name="Tag"))
admin.add_view(AdminAuthenticatedView(User, db.session, name="User"))
admin.add_view(StatsView(name='Thống kê báo cáo'))
admin.add_view(LogoutView(name="Đăng Xuất"))
