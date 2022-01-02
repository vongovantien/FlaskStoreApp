from flask import render_template, jsonify, session, flash
from myapp import *
from myapp.form import RegisterForm
from myapp import utils, app, form
from flask_login import login_user, logout_user, login_required
import math
import json
import cloudinary.uploader
from myapp.admin import *


# Google login route
@app.route('/login/google')
def google_login():
    google = oauth.create_client('google')
    redirect_uri = url_for('google_authorize', _external=True)
    return google.authorize_redirect(redirect_uri)


# Google authorize route
@app.route('/login/google/authorize')
def google_authorize():
    google = oauth.create_client('google')
    token = google.authorize_access_token()
    resp = google.get('userinfo').json()
    print(resp)
    utils.get_user_soccial(firstname=resp["name"], lastname=resp['given_name'], email=resp['email'],
                           avatar=resp['picture'])
    return "You are successfully signed in using google"


# Github login route
@app.route('/login/github')
def github_login():
    github = oauth.create_client('github')
    redirect_uri = url_for('github_authorize', _external=True)
    return github.authorize_redirect(redirect_uri)


# Github authorize route
@app.route('/login/github/authorize')
def github_authorize():
    github = oauth.create_client('github')
    token = github.authorize_access_token()
    resp = github.get('user')
    print(f"\n{resp}\n")
    return "You are successfully signed in using github"


@app.route("/test", methods=['post', 'get'])
def test():
    form = RegisterForm()
    if form.validate_on_submit():
        flash(f'Account created for {form.username.data}!', 'success')
        return redirect(url_for('home'))
    return render_template('test.html', title='Register', form=form)


@app.errorhandler(404)
def page_not_found(error):
    return render_template("404.html")


@app.route('/contact', methods=['get', 'post'])
def contact():
    if request.method.__eq__('POST'):
        name = request.form.get('name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        message = request.form.get('message')

        msg = Message(subject=f"Mail from {name}",
                      body=f"Name: {name}\nEmail: {email}\nPhone: {phone}\n\n\n\n {message}",
                      sender=str(email), recipients=['1851010134tien@ou.edu.vn'])
        mail.send(msg)

        return render_template("contact.html", err_msg="Gửi mail thành công")

    return render_template('contact.html')


@app.context_processor
def common_response():
    return {
        'categories': utils.read_categories(),
        'cart_stats': utils.count_cart(session.get('cart'))
    }


@app.route('/')
def home():
    products = utils.get_new_product()
    return render_template("index.html", products=products)


@app.route('/products')
def product_list():
    kw = request.args.get('kw')
    from_price = request.args.get('fromPrice')
    to_price = request.args.get('toPrice')
    page = request.args.get('page', 1)
    cate_id = request.args.get("category_id")
    next_page = request.args.get('next_num')
    prev_page = request.args.get('prev_num')
    categories = utils.read_categories()
    quantity = utils.count_products()
    products = utils.load_products(kw, from_price, to_price, cate_id, page=int(page), next_page=next_page,
                                   prev_page=prev_page)
    return render_template('products.html',
                           categories=categories,
                           products=products, pages=math.ceil(quantity / app.config['PAGE_SIZE']),
                           next_page=next_page, prev_page=prev_page)


@login.user_loader
def load_user(user_id):
    return utils.get_user_by_id(user_id=user_id)


@app.route('/products/<int:product_id>')
def product_detail(product_id):
    page = int(request.args.get('page', 1))
    product = utils.get_product_by_id(product_id=product_id)
    comments = utils.get_comments(product_id=product_id, page=page)

    return render_template('product-detail.html', comments=comments, product=product,
                           pages=math.ceil(utils.count_comment(product_id=product_id) / app.config['COMMENT_SIZE']))


@app.route('/admin-login', methods=['post'])
def admin_login():
    username = request.form.get('username')
    password = request.form.get('password')

    user = utils.check_login(username=username, password=password, role=UserRole.ADMIN)
    if user:
        login_user(user=user)

    return redirect('/admin')


@app.route("/register", methods=['get', 'post'])
def register():
    err_msg = ""
    if request.method.__eq__('POST'):
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        email = request.form.get('email')
        username = request.form.get('username')
        password = request.form.get('password')
        confirm = request.form.get('confirm')
        # avatar_path = 'images/upload/%s' % avatar.filename
        # avatar.save(os.path.join(app.root_path,
        #                          'static/',
        #                          avatar_path))
        if utils.check_user_name(username):
            err_msg = "Tên đăng nhập đã tồn tại"
            return render_template('register.html', err_msg=err_msg)
        else:
            if password.strip().__eq__(confirm.strip()):
                file = request.files.get('avatar')
                avatar = None
                if file:
                    res = cloudinary.uploader.upload(file)
                    avatar = res['secure_url']

                try:
                    utils.create_new_user(first_name=first_name,
                                          last_name=last_name,
                                          email=email,
                                          username=username,
                                          password=password,
                                          avatar=avatar)
                    return redirect(url_for('login'))

                except Exception as ex:
                    err_msg = "Có lỗi " + str(ex)
            else:
                err_msg = "Mật khẩu không khớp"

    return render_template('register.html', err_msg=err_msg)


@app.route("/login", methods=['get', 'post'])
def login():
    err_msg = ''
    if request.method.__eq__('POST'):
        username = request.form.get('username')
        password = request.form.get('password')
        user = utils.check_login(username=username, password=password)
        if user:
            login_user(user=user)
            return redirect(url_for(request.args.get('next', 'home')))
        else:
            err_msg = 'Username hoặc Password không chính xác!!!'

    return render_template('login.html', err_msg=err_msg)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home'))


@app.route('/cart')
def view_cart():
    return render_template("cart.html", stats=utils.count_cart(session.get('cart')))


@app.route('/api/add-to-cart', methods=['post'])
def add_to_cart():
    data = request.json
    id = str(data.get('id'))
    name = data.get('name')
    price = data.get('price')

    cart = session.get('cart')
    if not cart:
        cart = {}

    if id in cart:
        cart[id]['quantity'] = cart[id]['quantity'] + 1
    else:
        cart[id] = {
            'id': id,
            'name': name,
            'price': price,
            'quantity': 1
        }

    session['cart'] = cart

    return jsonify(utils.count_cart(cart))


@app.route('/api/update-cart', methods=['put'])
def update_cart():
    data = request.json
    id = str(data.get('id'))
    quantity = data.get('quantity', 1)

    cart = session.get('cart')
    if cart and id in cart:
        cart[id]['quantity'] = quantity
        session['cart'] = cart

    return jsonify(utils.count_cart(cart))


@app.route('/api/delete-cart/<int:product_id>', methods=['delete'])
def delete_cart(product_id):
    cart = session.get('cart')

    if cart and product_id in cart:
        del cart[product_id]
        session['cart'] = cart

    return jsonify(utils.count_cart(cart))


@app.route('/api/pay', methods=['post'])
def pay():
    try:
        utils.add_receipt(session.get('cart'))
        del session['cart']
    except:
        return jsonify({'code': 400})

    return jsonify({'code': 200})


@app.route('/api/comments', methods=['post'])
@login_required
def add_comment():
    data = request.json
    content = data.get('content')
    product_id = data.get('product_id')

    try:
        c = utils.add_comment(content=content, product_id=product_id)
    except:
        return {
            'status': 404, 'err_msg': 'Chương trình bị lỗi!!!'
        }
    return {
        'status': 201, 'comment': {
            'id': c.id,
            'content': c.content,
            'created_date': c.created_date,
            'user': {
                'username': current_user.username,
                'avatar': current_user.avatar
            }
        }
    }
